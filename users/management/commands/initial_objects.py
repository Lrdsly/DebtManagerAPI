from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save 
# from django.dispatch import 

from users.models import Room, MemberShip
from users.signals import join_global_room_when_user_created
# Enter your code here.

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        
        # Build admin user
        post_save.disconnect(join_global_room_when_user_created, sender=User)
        try:
            admin = User.objects.get(username = "admin")
            self.stdout.write(self.style.NOTICE("Admin already exists."))
        except:
            admin = User.objects.create_superuser(username="admin", password="admin123", name="admin")
            self.stdout.write(self.style.SUCCESS("Admin User Created."))
        post_save.connect(join_global_room_when_user_created, sender=User)


        global_room, global_room_created = Room.objects.get_or_create(slug="global",
                                                 defaults= {
                                                     "name": "Global",
                                                     "admin": admin
                                                 })
        
        if global_room_created:
            self.stdout.write(self.style.SUCCESS("Global Room Created."))
        else:
            self.stdout.write(self.style.NOTICE("Global room already exists."))
        
        member_ship, member_ship_created = MemberShip.objects.get_or_create(user=admin, room=global_room)
        if member_ship_created:
            self.stdout.write(self.style.SUCCESS("Admin User Joined Global Room."))
        else:
            self.stdout.write(self.style.NOTICE("Admin user is already a global room member."))
        