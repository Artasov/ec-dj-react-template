import os

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Dumps data from all models into separate files within a specified directory'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory where data files will be saved')

    def handle(self, *args, **options):
        directory = options['directory']
        if not os.path.exists(directory):
            os.makedirs(directory)

        for app in apps.get_app_configs():
            for model in app.get_models():
                model_label = f"{app.label}_{model._meta.model_name}"
                output_file_path = os.path.join(directory, f"{model_label}.json")
                self.stdout.write(f"Dumping data for {model_label} into {output_file_path}")
                try:
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        call_command('dumpdata', f'{app.label}.{model._meta.model_name}', stdout=output_file)
                except Exception:
                    print(f'{model._meta.model_name} Not Loaded')