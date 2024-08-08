# apps/core/management/commands/init_test_db.py

import os
import random
from time import sleep

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from faker import Faker

from apps.commerce.models.client import Client
from apps.commerce.models.employee import (
    Employee, EmployeeAvailabilityInterval, EmployeeLeave
)
from apps.core.models import User, Language, WeekDays, Gender
from apps.daily_co.models import DailyCoConference
from apps.psychology.models.consultation import (
    ConsultationDurationCategory, Consultation, ConsultationStatus,
    ConsultationReschedule, ConsultationCancel, ConsultationLanguage,
    ConsultationCommunicationType, ConsultationType
)
from apps.psychology.models.psychologist import (
    PsychologistSkill, Psychologist
)
from apps.psychology.models.webinar import WebinarAccess, WebinarLesson, Webinar

AVATAR_DIR = os.path.join(settings.BASE_DIR, 'apps/core/tests/test_data/user/images/avatar/')
WEBINAR_IMG_DIR = os.path.join(settings.BASE_DIR, 'apps/core/tests/test_data/webinar_picture/')
fake = Faker()


class Command(BaseCommand):
    help = 'Initialize the test database with fake data'

    def handle(self, *args, **kwargs):
        self.reset_database()
        self.run_migrations()
        self.create_test_data()

    def reset_database(self):
        db_settings = settings.DATABASES['default']
        if db_settings['ENGINE'] == 'django.db.backends.sqlite3':
            db_path = db_settings['NAME']
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except PermissionError:
                    self.stdout.write("sqlite3 isn't deleted")
                self.stdout.write(f'Deleted SQLite database file: {db_path}')

    def run_migrations(self):
        call_command('remakemigrations')
        sleep(5)
        self.disable_foreign_keys()
        self.stdout.write('Running migrate...')
        call_command('migrate')
        call_command('pre_init')  # Run the pre_init command to create initial data
        self.enable_foreign_keys()
        self.stdout.write(self.style.SUCCESS('Migrate completed'))

    def disable_foreign_keys(self):
        db_settings = settings.DATABASES['default']
        if db_settings['ENGINE'] == 'django.db.backends.sqlite3':
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA foreign_keys = OFF;')

    def enable_foreign_keys(self):
        db_settings = settings.DATABASES['default']
        if db_settings['ENGINE'] == 'django.db.backends.sqlite3':
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA foreign_keys = ON;')

    def create_test_data(self):
        self.stdout.write('Starting to initialize the test database with fake data...')
        pysch = self.create_superuser()
        client = self.create_test_client()
        self.create_users()
        # self.create_consultations()
        self.create_employee_leaves()
        self.create_fixed_consultations()
        self.stdout.write(self.style.SUCCESS('Test database initialization complete.'))

    def create_user(self):
        password = '123'
        user = User.objects.create_user(
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            middle_name=fake.first_name(),
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=90),
            gender=random.choice([Gender.MALE, Gender.FEMALE]),
            password=password,
            email=fake.email(),
        )
        self.set_avatar(user)
        return user

    def set_avatar(self, user):
        avatar_files = [f for f in os.listdir(AVATAR_DIR) if f.endswith('.jpg')]
        if avatar_files:
            avatar_path = os.path.join(AVATAR_DIR, random.choice(avatar_files))
            with open(avatar_path, 'rb') as avatar_file:
                user.avatar.save(os.path.basename(avatar_path), File(avatar_file), save=True)

    def create_superuser(self):
        username = '123'
        password = '123'
        user, created = User.objects.get_or_create(
            first_name='Бурбон', last_name='Вискович', username=username
        )
        if created:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.set_avatar(user)
            Client.objects.create(user=user, about_me=fake.text(), status=Client.Status.NEW)
            Psychologist.objects.create(
                user=user,
                status=Employee.EmployeeStatus.WORKING,
                education=fake.sentence(),
                experience_text=fake.text(),
                is_employed=True
            )
            self.create_webinars(user)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created with password {password}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} already exists'))
        return user

    def create_test_client(self):
        username = '321'
        password = '123'
        user, created = User.objects.get_or_create(
            first_name='Рофл', last_name='Клиентыч', username=username
        )
        if created:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.set_avatar(user)
            Client.objects.create(user=user, about_me=fake.text(), status=Client.Status.NEW)
            self.create_webinars(user)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created with password {password}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} already exists'))
        return user

    def create_webinars(self, user):
        youtube_video_ids = [
            "dQw4w9WgXcQ", "3JZ_D3ELwOQ", "L_jWHffIx5E", "d-diB65scQU",
            "otCpCn0l4Wo", "eBGIQ7ZuuiU", "tVj0ZTS4WF4", "6_b7RDuLwcI",
            "kJQP7kiw5Fk", "9bZkp7q19f0"
        ]

        webinars = []
        webinar_picture_files = [f for f in os.listdir(WEBINAR_IMG_DIR) if f.endswith('.svg')]
        for i in range(6):
            webinar = Webinar.objects.create(
                name=fake.sentence(nb_words=3),
                price=random.uniform(20.0, 100.0),
                currency='USD',
                description=fake.text(max_nb_chars=200),
                is_public=True
            )
            if webinar_picture_files:
                webinar_picture_path = os.path.join(WEBINAR_IMG_DIR, random.choice(webinar_picture_files))
                with open(webinar_picture_path, 'rb') as avatar_file:
                    webinar.picture.save(os.path.basename(webinar_picture_path), File(avatar_file), save=True)
            webinars.append(webinar)
            self.stdout.write(self.style.SUCCESS(f'Webinar "{webinar.name}" created'))
            self.create_webinar_lessons(webinar, youtube_video_ids)

        self.assign_webinar_access(user, webinars)

    def create_webinar_lessons(self, webinar, youtube_video_ids):
        lesson_count = random.randint(4, 10)
        for _ in range(lesson_count):
            lesson = WebinarLesson.objects.create(
                webinar=webinar,
                name=fake.sentence(nb_words=5),
                description=fake.text(max_nb_chars=500),
                youtube_embed_code=random.choice(youtube_video_ids),
                consultation_count_for_access=random.randint(0, 5),
                is_accessed=True,
                document_url=fake.url()
            )
            self.stdout.write(self.style.SUCCESS(f'Lesson "{lesson.name}" created for webinar "{webinar.name}"'))

    def assign_webinar_access(self, user, webinars):
        webinars_to_assign = random.sample(webinars, 4)
        for webinar in webinars_to_assign:
            WebinarAccess.objects.create(user=user, webinar=webinar)
            self.stdout.write(
                self.style.SUCCESS(f'Access to webinar "{webinar.name}" assigned to user "{user.username}"'))

    def create_users(self):
        for _ in range(30):
            user = self.create_user()
            if random.choice([True, False]):
                Client.objects.create(user=user, about_me=fake.text(), status=Client.Status.NEW)
                self.stdout.write(self.style.SUCCESS(f'Client {user.username} created'))
            else:
                psych = Psychologist.objects.create(
                    user=user,
                    status=Employee.EmployeeStatus.WORKING,
                    education=fake.sentence(),
                    experience_text=fake.text(),
                    is_employed=True
                )
                self.create_skills_for_psychologist(psych)
                self.create_availability_intervals(user)
                self.stdout.write(self.style.SUCCESS(f'Psychologist {user.username} created'))

    def create_skills_for_psychologist(self, psych):
        skills = PsychologistSkill.objects.all()
        for _ in range(random.randint(1, 16)):
            skill = random.choice(skills)
            psych.skills.add(skill)
            self.stdout.write(
                self.style.SUCCESS(f'Skill {skill.name} added to psychologist {psych.user.username}'))

    def create_availability_intervals(self, user):
        for _ in range(random.randint(1, 5)):
            start_time = fake.time_object()
            end_time = fake.time_object()
            if start_time > end_time:
                start_time, end_time = end_time, start_time
            EmployeeAvailabilityInterval.objects.create(
                user=user,
                employment_type=random.choice(EmployeeAvailabilityInterval.EmploymentType.choices)[0],
                day_of_week=random.choice(WeekDays.choices)[0],
                start_time=start_time,
                end_time=end_time
            )
            self.stdout.write(self.style.SUCCESS(f'Availability interval added to user {user.username}'))

    def create_consultations(self):
        superuser_psych = Psychologist.objects.get(user__username='123').user
        test_client = self.create_user()
        self.generate_random_consultations(superuser_psych, 'psychologist')
        self.generate_random_consultations(test_client, 'client')

    def generate_random_consultations(self, user, role):
        for _ in range(100):
            self.create_consultation(user=user, role=role)

    def create_consultation(self, user=None, date=None, language=None, status=None, role=None):
        categories = ConsultationDurationCategory.objects.all()
        psychologists = Psychologist.objects.exclude(user__username='123').values_list('user', flat=True)
        clients = Client.objects.exclude(user__username='123').values_list('user', flat=True)
        consultation_type_choice = random.choice([ConsultationType.Choices.INDIVIDUAL, ConsultationType.Choices.PAIR])
        consultation_type, created = ConsultationType.objects.get_or_create(name=consultation_type_choice)

        consultation = Consultation.objects.create(
            duration_category=random.choice(categories),
            status=status or random.choice([status[0] for status in ConsultationStatus.choices]),
            expired_at=timezone.now() + timezone.timedelta(days=random.randint(1, 30)),
            created_at=timezone.now(),
            type=consultation_type  # Используем объект ConsultationType
        )

        if role == 'psychologist' and psychologists.exists():
            consultation.psychologists.add(user)
            num_clients = random.choice([1, 1, 2])
            consultation.clients.add(*random.sample(list(clients), num_clients))
        elif role == 'client' and clients.exists():
            consultation.clients.add(user)
            num_psychologists = random.randint(1, min(2, len(psychologists)))
            consultation.psychologists.add(*random.sample(list(psychologists), num_psychologists))

        consultation.date = date or (timezone.now() + timezone.timedelta(days=random.randint(1, 30)))
        consultation.language = language or self.get_random_language()
        consultation.save()
        self.create_consultation_type(consultation)
        self.stdout.write(self.style.SUCCESS(f'Consultation {consultation.id} created'))

        if random.choice([True, False]):
            ConsultationReschedule.objects.create(
                consultation=consultation,
                consultation_status=consultation.status,
                old_date=consultation.date,
                new_date=consultation.date + timezone.timedelta(days=random.randint(1, 30)),
                reason=fake.text()
            )
            self.stdout.write(self.style.SUCCESS(f'Consultation {consultation.id} rescheduled'))

        if random.choice([True, False]):
            ConsultationCancel.objects.create(
                consultation=consultation,
                reason=fake.text()
            )
            self.stdout.write(self.style.SUCCESS(f'Consultation {consultation.id} cancelled'))

    def get_random_language(self):
        return ConsultationLanguage.objects.filter(
            language=random.choices(
                [lang[0] for lang in Language.choices],
                [0.8 if lang[0] == Language.RUS else 0.2 for lang in Language.choices]
            )[0]
        ).first()

    def create_consultation_type(self, consultation):
        comm_type = random.choices(
            [choice[0] for choice in ConsultationCommunicationType.Choices.choices],
            [0.8 if choice[0] == ConsultationCommunicationType.Choices.VIDEO else 0.2 for choice in
             ConsultationCommunicationType.Choices.choices]
        )[0]
        consultation_communication_type = ConsultationCommunicationType.objects.get_or_create(type=comm_type)
        consultation.communication_type = consultation_communication_type[0]
        consultation.save()

    def create_employee_leaves(self):
        psychologists = Psychologist.objects.all()
        leave_types = [choice[0] for choice in EmployeeLeave.EmployeeLeaveType.choices]
        for psych in psychologists:
            for _ in range(random.randint(1, 3)):
                EmployeeLeave.objects.create(
                    user=psych.user,
                    leave_type=random.choice(leave_types),
                    start_date=timezone.now() - timezone.timedelta(days=random.randint(1, 30)),
                    end_date=timezone.now() + timezone.timedelta(days=random.randint(1, 30)),
                    reason=fake.text()
                )
                self.stdout.write(self.style.SUCCESS(f'Leave created for psychologist {psych.user.username}'))

    def create_fixed_consultations(self):
        # Создаем консультации для пользователей 321 и 123
        client_321 = User.objects.get(username='321')
        client_123 = User.objects.get(username='123')
        psychologist_123 = User.objects.get(username='123')

        consultation_types = ConsultationType.objects.all()
        duration_categories = ConsultationDurationCategory.objects.all()
        languages = ConsultationLanguage.objects.all()
        communication_types = ConsultationCommunicationType.objects.all()

        now = timezone.now()

        def create_consultations(client, psychologist):
            for consultation_type in consultation_types:
                for duration_category in duration_categories:
                    if Consultation.objects.filter(clients=client, psychologists=psychologist).count() < 10:
                        consultation = Consultation.objects.create(
                            type=consultation_type,
                            duration_category=duration_category,
                            language=self.get_random_language(),
                            status=ConsultationStatus.NEW,
                            date=now + timezone.timedelta(hours=7),
                            expired_at=now + timezone.timedelta(days=21),
                            conference=DailyCoConference.objects.create(
                                room_name="Fj5zf0zbUUwySpgygnh3",
                                room_url="https://life-help-ru.daily.co/Fj5zf0zbUUwySpgygnh3",
                            )
                        )
                        consultation.clients.set([client])
                        consultation.psychologists.set([psychologist])
                        self.stdout.write(self.style.SUCCESS(f'Consultation {consultation.id} created'))

                        consultation_paid = Consultation.objects.create(
                            type=consultation_type,
                            duration_category=duration_category,
                            language=self.get_random_language(),
                            status=ConsultationStatus.PAID,
                            date=now + timezone.timedelta(days=1),
                            expired_at=now + timezone.timedelta(days=5),
                            conference=DailyCoConference.objects.create(
                                room_name="Fj5zf0zbUUwySpgygnh3",
                                room_url="https://life-help-ru.daily.co/Fj5zf0zbUUwySpgygnh3",
                            )
                        )
                        consultation_paid.clients.set([client])
                        consultation_paid.psychologists.set([psychologist])
                        self.stdout.write(self.style.SUCCESS(f'Consultation {consultation_paid.id} created'))

                        consultation_completed_1 = Consultation.objects.create(
                            type=consultation_type,
                            duration_category=duration_category,
                            language=self.get_random_language(),
                            status=ConsultationStatus.COMPLETED,
                            date=now - timezone.timedelta(days=1),
                            expired_at=now + timezone.timedelta(days=6),
                            conference=DailyCoConference.objects.create(
                                room_name="Fj5zf0zbUUwySpgygnh3",
                                room_url="https://life-help-ru.daily.co/Fj5zf0zbUUwySpgygnh3",
                            )
                        )
                        consultation_completed_1.clients.set([client])
                        consultation_completed_1.psychologists.set([psychologist])
                        self.stdout.write(
                            self.style.SUCCESS(f'Consultation {consultation_completed_1.id} created'))

                        consultation_completed_2 = Consultation.objects.create(
                            type=consultation_type,
                            duration_category=duration_category,
                            language=self.get_random_language(),
                            status=ConsultationStatus.COMPLETED,
                            date=now - timezone.timedelta(days=3),
                            expired_at=now + timezone.timedelta(days=5),
                            conference=DailyCoConference.objects.create(
                                room_name="Fj5zf0zbUUwySpgygnh3",
                                room_url="https://life-help-ru.daily.co/Fj5zf0zbUUwySpgygnh3",
                            )
                        )
                        consultation_completed_2.clients.set([client])
                        consultation_completed_2.psychologists.set([psychologist])
                        self.stdout.write(
                            self.style.SUCCESS(f'Consultation {consultation_completed_2.id} created'))

        create_consultations(client_321, psychologist_123)
