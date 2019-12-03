from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = '''Controlled vocabularies toolbox

Actions:

  update
    update the list of vocabularies from the plugins / managers.

'''

    def add_arguments(self, parser):
        parser.add_argument('action', nargs=1, type=str)

    def handle(self, *args, **options):
        show_help = True

        action = options['action'][0]

        if action == 'update':
            self.action_update()
            show_help = False

        if show_help:
            self.stdout.write(self.help)
        else:
            self.stdout.write('done ({})'.format(action))

    def action_update(self):
        from django.apps import apps
        app = apps.get_app_config('controlled_vocabulary')
        vocs = app.write_vocabulary_records_from_managers()

        for voc in vocs.values():
            self.stdout.write(voc.__module__)
