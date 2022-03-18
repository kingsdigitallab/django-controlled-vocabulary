from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = """Controlled vocabularies toolbox

Usage: vocab ACTION OPTIONS

ACTION:

  init
    same as 'update' followed by 'fetch'
  update
    update vocabulary records from the enabled plugins / managers
  fetch
    download the remote data source for each plugin / manager
    a data source can be a CSV, RDF, ...
    note: some managers don't need source files
    note: does nothing if the file already exists
  refetch
    same as fetch but always download the source data even if already on disk
  managers
    lists the plugins / managers
  search
    look up a pattern in the vocabulary with the given prefix
    note: this bypasses the database and calls search() on the voc manager
    e.g. vocab search -f iso639-2 -p english

OPTIONS:

  -f PREFIXES
    limit action to some vocabularies
    PREFIX is a comma separated list of vocabulary prefixes.
    Use managers to see available prefixes.
  -p PATTERN
    a pattern to look up in a vocabulary
    pattern is a plain string, not a regular expression

"""

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        from argparse import RawTextHelpFormatter
        # to avoid the above help text to be displayed on a single line
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument("action", nargs=1, type=str)

        parser.add_argument(
            "-f", action="store", help="list of vocabulary prefixes",
        )

        parser.add_argument(
            "-p", action="store", help="a string pattern to look up",
        )

    def handle(self, *args, **options):
        show_help = True

        self.options = options
        action = options["action"][0]

        from django.apps import apps
        self.app = apps.get_app_config("controlled_vocabulary")

        action_method = getattr(self, "action_" + action, None)
        if action_method:
            show_help = False
            res = action_method()
            if res not in [None, True]:
                import sys
                sys.exit(1)

        if show_help:
            self.stdout.write(self.help)
        else:
            self.stdout.write("done (vocab {})".format(action))

    def action_search(self):
        pattern = (self.options['p'] or '').strip()
        prefixes = self._get_prefixes()
        if not (prefixes and pattern):
            self.stdout.write("Please use -f and -p "
                              "to pass a vocabulary prefix and a pattern")

        for prefix in prefixes:
            manager = self.app.get_vocabulary_manager(prefix)
            if manager:
                res = manager.search(pattern)
                self.stdout.write("{}: {}".format(prefix, type(manager)))
                self.stdout.write(repr(res))
            else:
                self.stdout.write("{}: manager not found".format(prefix))

    def action_managers(self):
        template = "{:12.12} {:25.25} {:22.22} {}"
        self.stdout.write(template.format("prefix", "concept", "base", "module"))
        for voc in self._get_vocabularies():
            self.stdout.write(
                template.format(
                    voc.prefix,
                    voc.concept,
                    voc.__class__.__bases__[0].__name__,
                    voc.__module__,
                )
            )

    def action_update(self):
        vocs = self.app.write_vocabulary_records_from_managers()
        if self.options["verbosity"] > 0:
            if vocs:
                for voc in vocs.values():
                    self.stdout.write(voc.__module__)
            else:
                self.stdout.write('Please run django migrate.')

    def action_refetch(self):
        return self.action_fetch(True)

    def action_fetch(self, overwrite=False):
        ret = True

        for voc in self._get_vocabularies():
            download_method = getattr(voc, "download", None)
            if download_method:
                if self.options["verbosity"] > 0:
                    self.stdout.write(voc.prefix)
                url, filepath, size, downloaded = download_method(overwrite=overwrite)
                if self.options["verbosity"] > 0:
                    if size > 0:
                        self.stdout.write(
                            "\t{}\n\t{}\n\t{:.3f}MB".format(
                                url, filepath, size / 1024 / 1024
                            )
                        )
                    else:
                        self.stdout.write(f"ERROR: vocabulary download failed {url}.")
                if size < 1:
                    ret = False

        return ret

    def action_init(self):
        self.action_update()
        self.action_fetch()

    def action_transform(self):
        for voc in self._get_vocabularies():
            transform = getattr(voc, "transform_download", None)
            if transform:
                transform()

    def _get_vocabularies(self):
        """Returns a list of Vocabulary plugin objects.
        All of them by default.
        Or only those selected with -f arg on the command line.
        """
        prefixes = self._get_prefixes()
        ret = [
            voc
            for voc in self.app.vocabulary_managers.values()
            if not prefixes or voc.prefix in prefixes
        ]

        return ret

    def _get_prefixes(self):
        """Returns a list of voc prefixes
        selected with -f arg on the command line.
        Can be empty.
        """
        ret = []
        prefixes = (self.options["f"] or "").strip()
        if prefixes:
            ret = prefixes.split(",")
        return ret
