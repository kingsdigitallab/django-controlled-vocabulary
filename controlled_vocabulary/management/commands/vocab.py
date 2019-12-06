from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = '''Controlled vocabularies toolbox

Usage: vocab ACTION OPTIONS

ACTION:

  update
    update vocabulary metadata from the plugins / managers into the database
  managers
    lists the plugins / managers

OPTIONS:

  -f PREFIXES
    limit action to some vocabularies.
    PREFIX is a comma separated list of vocabulary prefixes.
    Use managers to see available prefixes.

'''

    def add_arguments(self, parser):
        parser.add_argument('action', nargs=1, type=str)

        parser.add_argument(
            '-f',
            action='store',
            help='list of vocabulary prefixes',
        )

    def handle(self, *args, **options):
        show_help = True

        self.options = options
        action = options['action'][0]

        from django.apps import apps
        self.app = apps.get_app_config('controlled_vocabulary')

        action_method = getattr(self, 'action_' + action, None)
        if action_method:
            show_help = False
            action_method()

        if show_help:
            self.stdout.write(self.help)
        else:
            self.stdout.write('done ({})'.format(action))

    def action_managers(self):
        template = '{:12.12} {:25.25} {:22.22} {}'
        self.stdout.write(template.format(
            'prefix', 'concept', 'base', 'module'))
        for voc in self._get_vocabularies():
            self.stdout.write(template.format(
                voc.prefix,
                voc.concept,
                voc.__class__.__bases__[0].__name__,
                voc.__module__,
            ))

    def action_update(self):
        vocs = self.app.write_vocabulary_records_from_managers()

        for voc in vocs.values():
            self.stdout.write(voc.__module__)

    def action_download(self):
        vocs = self.app.vocabulary_managers

        for voc in vocs.values():
            download_method = getattr(voc, 'download', None)
            if download_method:
                self.stdout.write(voc.prefix)
                url, filepath, size = download_method()
                self.stdout.write(
                    '{}\t{}\t{:.3f}MB'.format(
                        url,
                        filepath,
                        size / 1024 / 1024
                    )
                )

    def _get_vocabularies(self):
        '''Returns a list of Vocabulary plugin objects.
        All of them by default.
        Or only those selected with -f arg on the command line.
        '''
        prefixes = self._get_prefixes()
        ret = [
            voc
            for voc
            in self.app.vocabulary_managers.values()
            if not prefixes or voc.prefix in prefixes
        ]

        return ret

    def _get_prefixes(self):
        '''Returns a list of voc prefixes
        selected with -f arg on the command line.
        Can be empty.
        '''
        ret = []
        prefixes = (self.options['f'] or '').strip()
        if prefixes:
            ret = prefixes.split(',')
        return ret
