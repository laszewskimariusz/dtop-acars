from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from acars.models import SmartcarsProfile


class Command(BaseCommand):
    help = 'Tworzy profile SmartCARS dla wszystkich użytkowników, którzy nie mają jeszcze profili'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Pokazuje co zostanie zrobione bez wykonywania zmian',
        )

    def handle(self, *args, **options):
        # Znajdź użytkowników bez profilu SmartCARS
        users_without_profile = User.objects.filter(smartcarsprofile__isnull=True)
        
        if not users_without_profile.exists():
            self.stdout.write(
                self.style.SUCCESS('Wszyscy użytkownicy mają już profile SmartCARS!')
            )
            return

        self.stdout.write(
            f'Znaleziono {users_without_profile.count()} użytkowników bez profilu SmartCARS'
        )

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN - żadne zmiany nie zostaną wykonane'))
            for user in users_without_profile:
                self.stdout.write(f'  - {user.username} ({user.email})')
            return

        created_count = 0
        error_count = 0

        for user in users_without_profile:
            try:
                profile = SmartcarsProfile.objects.create(user=user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Utworzono profil SmartCARS dla {user.username} '
                        f'(API Key: {profile.api_key[:8]}...)'
                    )
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Błąd podczas tworzenia profilu dla {user.username}: {e}'
                    )
                )
                error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nPodsumowanie:\n'
                f'  - Utworzono: {created_count} profili\n'
                f'  - Błędów: {error_count}'
            )
        )

        if created_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    '\nUwaga: Nowe API Keys zostały wygenerowane automatycznie. '
                    'Użytkownicy znajdą je w swoim panelu użytkownika.'
                )
            ) 