import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates (or resets) the demo login used for grading/review.'

    def handle(self, *args, **options):
        email = os.getenv('DEMO_USER_EMAIL', 'demo@workboard.app')
        password = os.getenv('DEMO_USER_PASSWORD', 'DemoPass123!')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'first_name': 'Demo', 'last_name': 'User'},
        )
        user.set_password(password)
        user.is_active = True
        user.save()

        action = 'Created' if created else 'Reset'
        self.stdout.write(self.style.SUCCESS(
            f'{action} demo user -> email: {email}  password: {password}'
        ))
