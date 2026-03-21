from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from users.models import Room, MemberShip
# Enter your code here.

User = get_user_model()

@receiver(post_save, sender=User)
def join_global_room_when_user_created(sender, instance, created, **kwargs):
    if created:
        global_room = Room.objects.get(slug="global")
        MemberShip.objects.create(user=instance, room=global_room)
        