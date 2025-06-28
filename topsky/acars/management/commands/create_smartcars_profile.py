from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from acars.models import SmartcarsProfile


class Command(BaseCommand):
    help = 'Create SmartCARS profile for a user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email address')
        parser.add_argument(
            '--api-key',
            type=str,
            help='Custom API key (if not provided, will be auto-generated)'
        )
        parser.add_argument(
            '--acars-token',
            type=str,
            help='Custom ACARS token (if not provided, will be auto-generated)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing profile if it exists',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        try:
            user = User.objects.get(email__iexact=options['email'])
        except User.DoesNotExist:
            raise CommandError(f'User with email "{options["email"]}" does not exist.')

        # Check if profile already exists
        try:
            profile = SmartcarsProfile.objects.get(user=user)
            if not options['force']:
                self.stdout.write(
                    self.style.WARNING(
                        f'SmartCARS profile already exists for {user.email}.\n'
                        f'Current API key: {profile.api_key}\n'
                        f'Use --force to overwrite.'
                    )
                )
                return
            else:
                # Update existing profile
                if options['api_key']:
                    profile.api_key = options['api_key']
                else:
                    profile.api_key = ''  # Will be auto-generated on save
                if options['acars_token']:
                    profile.acars_token = options['acars_token']
                else:
                    profile.acars_token = ''  # Will be auto-generated on save
                profile.save()
                action = 'Updated'
        except SmartcarsProfile.DoesNotExist:
            # Create new profile
            profile_data = {'user': user}
            if options['api_key']:
                profile_data['api_key'] = options['api_key']
            if options['acars_token']:
                profile_data['acars_token'] = options['acars_token']
            
            profile = SmartcarsProfile.objects.create(**profile_data)
            action = 'Created'

        self.stdout.write(
            self.style.SUCCESS(
                f'{action} SmartCARS profile for {user.email}\n'
                f'Username: {user.username}\n'
                f'API Key: {profile.api_key}\n'
                f'ACARS Token: {profile.acars_token}\n'
                f'Profile ID: {profile.id}\n'
                f'Active: {profile.is_active}'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                f'\nFor testing with curl:\n'
                f'curl -v -X POST "https://dtopsky.topsky.app/acars/api/login?debug=1" \\\n'
                f'     -H "Content-Type: application/x-www-form-urlencoded" \\\n'
                f'     --data-urlencode "email={user.email}" \\\n'
                f'     --data-urlencode "api_key={profile.api_key}"'
            )
        ) 