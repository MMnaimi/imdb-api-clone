from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


"""
this code automatically creates a new authentication token for every new user 
immediately after the user is saved to the database. This is useful in a REST 
API context where you might want to return the token to the user immediately 
after they register, so they can start making authenticated requests.
"""

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)