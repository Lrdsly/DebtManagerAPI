from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from users.models import Room
from debts.models import Debt

from random import choice
# Enter your code here.

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        
        # identify initial objects
        admin = User.objects.get(username="admin")
        global_room = Room.objects.get(slug="global")

        # create 5 random users
        ordinary_users = []
        for u in range(1,6):
            try:
                user = User.objects.get(username=f"user{u}")
                self.stdout.write(self.style.NOTICE(f"user{u} already exists."))
            except:
                user = User.objects.create_user(username=f"user{u}", name=f"user{u}", password="12345")
                self.stdout.write(self.style.SUCCESS(f"user{u} Created Suucessfully."))
            ordinary_users.append(user)

        # create 2 random rooms
        ordinary_rooms = []
        for r in range(1,3):
            room, room_created = Room.objects.get_or_create(slug=f"room{r}",
                                                            defaults={
                                                                'name': f"room{r}",
                                                                'admin': choice(ordinary_users),
                                                            })
            if room_created:
                self.stdout.write(self.style.SUCCESS(f"room{r} Created Suucessfully."))
            else:
                self.stdout.write(self.style.NOTICE(f"roomr{r} already exists."))
            ordinary_rooms.append(room)

        # create 10 random debts
        for d in range(1,11):
            # print("="*100)
            # print(type(choice(ordinary_rooms)))
            debt = Debt.objects.create(creditor=choice(ordinary_users),
                                       debtor=choice(ordinary_users),
                                       amount=choice([10,50,100]),
                                       room=choice(ordinary_rooms))
            
            self.stdout.write(self.style.SUCCESS(f"debt of {debt.debtor} to {debt.creditor} with amount {debt.amount} created"))
