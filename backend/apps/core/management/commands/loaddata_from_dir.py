import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Loads data from all files within a specified directory into the corresponding models'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory from which data files will be loaded')

    def handle(self, *args, **options):
        directory = options['directory']
        if not os.path.exists(directory):
            self.stdout.write(self.style.ERROR(f'Directory {directory} does not exist'))
            return

        total_files = 0
        loaded_files = 0
        failed_files = []
        successful_files = []

        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                total_files += 1
                self.stdout.write(f'Loading data from {filename}')
                try:
                    call_command('loaddata', os.path.join(directory, filename))
                    loaded_files += 1
                    successful_files.append(filename)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'{filename} Not Loaded'))
                    self.stdout.write(self.style.ERROR(str(e)))
                    failed_files.append(filename)

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {loaded_files}/{total_files} files.'))

        if successful_files:
            self.stdout.write(self.style.SUCCESS('Successfully loaded the following files:'))
            for successful_file in successful_files:
                self.stdout.write(self.style.SUCCESS(f'- {successful_file}'))

        if failed_files:
            self.stdout.write(self.style.ERROR('Failed to load the following files:'))
            for failed_file in failed_files:
                self.stdout.write(self.style.ERROR(f'- {failed_file}'))
