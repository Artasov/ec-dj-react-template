import os

import pyperclip
from django.conf import settings
from django.core.management.base import BaseCommand

TARGET_ALL = [
    'controllers',
    'serializers',
    # 'exceptions',
    'tests',
    'models',
    'routes',
    'urls',
    'service',
    'services',
    # 'decorators',
    # 'permissions',
    # 'tasks',
    # 'middleware',
    # 'forms',
    'async_django',
    # 'components',
    # 'pages',
    'services'
]


class Command(BaseCommand):
    help = 'Copy project structure and contents of specific files and directories.'

    IGNORE_FILES = ['__init__.py']

    def add_arguments(self, parser):
        parser.add_argument(
            'target_names', nargs='*', type=str,
            help='List of target names to collect. Defaults to all if not provided.'
        )
        parser.add_argument(
            '--apps', nargs='+', type=str,
            help='List of apps to collect from. Defaults to all if not provided.'
        )

    def handle(self, *args, **options):
        target_names = options['target_names']
        if not target_names or target_names[0] == 'all':
            target_names = TARGET_ALL

        apps_to_include = options['apps'] or self.get_all_apps()

        result = []
        collected_files = {name: [] for name in target_names}

        for app in apps_to_include:
            app_path = os.path.join(settings.BASE_DIR, 'apps', app)
            if not os.path.exists(app_path):
                self.stdout.write(self.style.ERROR(f"App {app} does not exist. Skipping."))
                continue
            for root, dirs, files in os.walk(app_path):
                for name in target_names:
                    if name in dirs:
                        dir_path = os.path.join(root, name)
                        self.collect_directory_contents(dir_path, collected_files[name])
                    if name + '.py' in files:
                        file_path = os.path.join(root, name + '.py')
                        self.collect_file_contents(file_path, collected_files[name])

        for name in target_names:
            if collected_files[name]:
                result.append(f'\n# {name.capitalize()}\n')
                result.extend(collected_files[name])

        final_text = '\n'.join(result)
        pyperclip.copy(final_text)
        self.stdout.write(self.style.SUCCESS('Project structure and contents copied to clipboard.'))
        print(final_text)

    def collect_directory_contents(self, dir_path, result):
        for sub_root, sub_dirs, sub_files in os.walk(dir_path):
            for file in sub_files:
                if file.endswith('.py') and file not in self.IGNORE_FILES:
                    file_path = os.path.join(sub_root, file)
                    self.collect_file_contents(file_path, result)

    @staticmethod
    def collect_file_contents(file_path, result):
        result.append(f'\n# {os.path.relpath(file_path, settings.BASE_DIR)}\n')
        with open(file_path, 'r', encoding='utf-8') as f:
            result.append(f.read())

    def get_all_apps(self):
        apps_path = os.path.join(settings.BASE_DIR, 'apps')
        return [name for name in os.listdir(apps_path) if os.path.isdir(os.path.join(apps_path, name))]
