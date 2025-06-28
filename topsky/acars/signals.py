from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import SmartcarsProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_smartcars_profile(sender, instance, created, **kwargs):
    """
    Automatycznie tworzy profil SmartCARS dla każdego nowego użytkownika
    """
    if created:
        try:
            profile = SmartcarsProfile.objects.create(user=instance)
            logger.info(f"Utworzono profil SmartCARS dla użytkownika {instance.username} z API key: {profile.api_key[:8]}...")
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia profilu SmartCARS dla {instance.username}: {e}")


@receiver(post_save, sender=User)
def save_smartcars_profile(sender, instance, **kwargs):
    """
    Zapewnia, że każdy użytkownik ma profil SmartCARS (na wypadek gdyby nie został utworzony)
    """
    if not hasattr(instance, 'smartcarsprofile'):
        try:
            profile = SmartcarsProfile.objects.create(user=instance)
            logger.info(f"Utworzono brakujący profil SmartCARS dla użytkownika {instance.username}")
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia brakującego profilu SmartCARS dla {instance.username}: {e}") 