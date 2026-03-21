from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.


class ModeChoice(models.IntegerChoices):
    NORMAL = 1, _("normal")
    HALFTRUSTED = 2, _("half-trusted")
    TRUSTED = 3, _("trusted")


class Room(models.Model):
    
    name = models.CharField(verbose_name=_("Room name"), max_length=100, blank=True, null=True)
    slug = models.SlugField(verbose_name=_("Room slug"), max_length=100, unique=True) # add auto generate slug later
    admin = models.ForeignKey(verbose_name=_("Room admin"), to="users.CustomUser", on_delete=models.CASCADE, related_name="room_admin")
    mode = models.IntegerField(verbose_name=_("Room status"), choices=ModeChoice, default=1)
    created_at = models.DateTimeField(verbose_name=_("Created time"), auto_now_add=True)

    def __str__(self):
        return self.name if self.name else self.slug
    

class MemberShip(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="membership_user")
    room = models.ForeignKey("users.Room", on_delete=models.CASCADE, related_name="membership_room")
    joined = models.DateTimeField(verbose_name=_("Joined Time"), auto_now_add=True)


class FriendShipStatus(models.IntegerChoices):
    PENDING = 1, _("pending")
    CONFIRMED = 2, _("confirmed")


# develop this model later. (changing status, endpoints and...)
class FriendShip(models.Model):
        
    user1 = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="freindsip_user1")
    user2 = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="friendship_user2")
    status = models.IntegerField(_("status"), choices=FriendShipStatus, default=1)
    since = models.DateTimeField(_("since"), auto_now_add=True)

    class Meta:
        # Avoid building 2 ralations between users (one time User A be user1 and in other time as user2)
        unique_together = ('user1', 'user2')
    
    def save(self, *args, **kwargs):
        # user1 is always that one with lower id
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1

        if self.user1 == self.user2:
            raise ValueError("Users can not be friend with themselves.")
        
        return super().save(*args, **kwargs)
