from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from users.models import Room, FriendShip, MemberShip, ModeChoise
# Create your models here.

User = get_user_model()


class StatusDebt(models.IntegerChoices):
    PENDING = 1, _("pending"),
    CONFIRMED = 2, _("confirmed"),
    REJECTED = 3, _("rejected"),
    PAIED = 4, _("paied"),
    PAYCONFIRMED = 5, ("pay_confirmed")


class Debt(models.Model):

    debtor = models.ForeignKey(User, on_delete=models.PROTECT)
    creditor = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(_("debt amount"), max_digits=13, decimal_places=2)
    room = models.ForeignKey(Room, on_delete=models.PROTECT, blank=True)
    description = models.CharField(_("description"), max_length=150, blank=True, null=True)
    status = models.IntegerField(_("status"), choices=StatusDebt, default=1)
    paied_at = models.DateTimeField(_("Paied time"), blank=True, null=True)
    created_at = models.DateTimeField(_("Created time"), auto_now_add=True)

    class Meta:
        verbose_name = "debt"
        verbose_name_plural = "debts"
        ordering = ['status', '-created_at']
    
    def __str__(self):
        return f"Debt of {self.debtor} with amount of {self.amount} to {self.creditor}"

    def clean(self):
        global_room = Room.objects.get(slug="global")
        if self.room is None:
            self.room = global_room

        if self.creditor == self.debtor:
            raise ValidationError("Debtor and Creditor can not be same")
        
        if self.room == global_room:
            freindship = FriendShip.objects.filter(Q(user1=self.creditor, user2=self.debtor) | Q(user1=self.debtor, user2=self.creditor)).exists()
            if not freindship:
                raise ValidationError("Only friend users can sumbit debts on global room")
       
        room_memberships = MemberShip.objects.filter(room=self.room).values_list("user__username", flat=True)
        if not self.creditor.username in room_memberships or not self.debtor.username in room_memberships:
            raise ValidationError("Debtor and Creditor must be in the room at the same time")
   
    def _suggest_next_status(self, current_status):
        if current_status == StatusDebt.PENDING:
            if self.room.mode in [ModeChoise.TRUSTED, ModeChoise.HALFTRUSTED]:
                return StatusDebt.CONFIRMED
            return current_status
        elif current_status == StatusDebt.PAIED:
            if self.room.mode == ModeChoise.Trusted:
                return StatusDebt.PAYCONFIRMED
            return current_status
        return current_status

    def change_status(self, new_status, user):
        current_status = self.status
        suggested_status = self._suggest_next_status(new_status)
        self.status = suggested_status
        self.save()
   
        if suggested_status != new_status:
            return suggested_status
        else: return new_status


class StatusLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    debt = models.ForeignKey(Debt, on_delete=models.DO_NOTHING)
    from_status = models.ForeignKey(StatusDebt)
    to_status = models.ForeignKey(StatusDebt)
    operated_at = models.DateTimeField(auto_now_add=True)
