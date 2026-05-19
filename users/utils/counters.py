from django.contrib.auth import get_user_model
from django.db.models import Q
from debts.models import Debt
from users.models import Room, MemberShip
# Enter your code here.

User = get_user_model()

def get_user_total_debt(slug, username):
    total_amount = 0
    room = Room.objects.get(slug=slug)
    user = User.objects.get(username=username)
    debts = Debt.objects.filter(Q(room=room) & (Q(debtor=user) | Q(creditor=user)))

    for debt in debts:
        if debt.debtor == user:
            total_amount += debt.amount
        else:
            total_amount -= debt.amount
    
    # if the number is negetive it mean user want some amount of money at last
    return total_amount 

def get_total_value(slug):
    total_value = 0
    room = Room.objects.get(slug=slug)
    print('-'*20)
    memberships = MemberShip.objects.filter(room=room)
    for member in memberships:
        user_total_debt = get_user_total_debt(slug, member.user.username)
        if user_total_debt < 0:
            # -user_total_debt = user_credit
            total_value -= user_total_debt

    # the whole amount of mony which most be paied in this room
    return total_value
