# apps/core/management/commands/pre_init.py

from django.core.management.base import BaseCommand

from apps.core.models import Language
from apps.psychology.models.consultation import (
    ConsultationDurationCategory, ConsultationLanguage,
    ConsultationCommunicationType, ConsultationType
)
from apps.psychology.models.psychologist import (
    PsychologistSkillCategory, PsychologistSkill
)


class Command(BaseCommand):
    help = 'Pre-initialize categories and types for the application'

    def handle(self, *args, **kwargs):
        self.create_languages()
        self.create_communication_types()
        self.create_consultation_duration_categories()
        self.create_consultation_types()
        self.create_skills()

    def create_languages(self):
        for lang_code, lang_name in Language.choices:
            ConsultationLanguage.objects.get_or_create(language=lang_code)
            self.stdout.write(self.style.SUCCESS(f'Consultation language "{lang_name}" created or already exists'))

    def create_communication_types(self):
        for comm_type, comm_name in ConsultationCommunicationType.Choices.choices:
            ConsultationCommunicationType.objects.get_or_create(type=comm_type)
            self.stdout.write(
                self.style.SUCCESS(f'Consultation communication type "{comm_name}" created or already exists'))

    def create_consultation_duration_categories(self):
        durations = (50, 90)  # Example durations in minutes
        for duration in durations:
            ConsultationDurationCategory.objects.get_or_create(duration=duration)
            self.stdout.write(
                self.style.SUCCESS(f'Consultation duration category "{duration}" created or already exists'))

    def create_consultation_types(self):
        for cons_type, cons_name in ConsultationType.Choices.choices:
            ConsultationType.objects.get_or_create(name=cons_type)
            self.stdout.write(self.style.SUCCESS(f'Consultation type "{cons_name}" created or already exists'))

    def create_skills(self):
        categories = {
            'Состояние': [
                'Стресс', 'Ощущение одиночества', 'Упадок сил', 'Перепады настроения',
                'Проблемы со сном', 'Навязчивые мысли о здоровье', 'Приступы тревоги и страха',
                'Панические атаки', 'Нестабильная самооценка', 'Раздражительность',
                'Эмоциональная зависимость', 'Расстройство пищевого поведения',
                'Сложности с алкоголем/наркотиками', 'Проблемы с весом (похудение, набор веса)',
                'Проблемы с концентрацией'
            ],
            'События в жизни': [
                'Переезд, эмиграция', 'Финансовые изменения', 'Насилие',
                'Утрата близкого человека', 'Беременность, рождение ребенка',
                'Разрыв отношений, развод', 'Болезнь, своя или близких'
            ],
            'Отношения': [
                'С партнером', 'С детьми', 'Сексуальные', 'С родителями',
                'В целом, с окружающими', 'Сложности с ориентацией, её поиск'
            ],
            'Работа, учёба': [
                'Выгорание', 'Прокрастинация', 'Отсутствие цели',
                'Недостаток мотивации', 'Не знаю, чем хочу заниматься',
                'Смена, потеря работы', 'Нужна супервизия'
            ]
        }
        for category_name, skill_names in categories.items():
            category, _ = PsychologistSkillCategory.objects.get_or_create(name=category_name)
            self.stdout.write(
                self.style.SUCCESS(f'Skill category "{category_name}" created or already exists'))
            for skill_name in skill_names:
                skill, _ = PsychologistSkill.objects.get_or_create(name=skill_name)
                category.skills.add(skill)
            category.save()
