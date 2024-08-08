import os
import glob
from time import sleep

from django.core.management import BaseCommand, call_command
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Delete all migration files from apps in the "apps." namespace, delete SQLite database file if used, and run makemigrations and migrate'

    def handle(self, *args, **kwargs):
        apps_namespace = 'apps.'
        base_dir = settings.BASE_DIR

        # Delete migration files
        for app in settings.INSTALLED_APPS:
            if app.startswith(apps_namespace):
                app_path = os.path.join(base_dir, app.replace('.', '/'))
                migrations_path = os.path.join(app_path, 'migrations')
                if os.path.exists(migrations_path):
                    files = glob.glob(os.path.join(migrations_path, '*.py'))
                    for file in files:
                        if os.path.basename(file) != '__init__.py':
                            os.remove(file)
                            self.stdout.write(f'Deleted {file}')

                    pyc_files = glob.glob(os.path.join(migrations_path, '*.pyc'))
                    for file in pyc_files:
                        os.remove(file)
                        self.stdout.write(f'Deleted {file}')

        self.stdout.write('All migration files in apps.* deleted')
        sleep(1)

        # Run makemigrations
        self.stdout.write('Running makemigrations...')
        call_command('makemigrations')
        self.stdout.write('Makemigrations completed')
        sleep(1)


