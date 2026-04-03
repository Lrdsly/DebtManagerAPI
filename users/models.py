from django.db import models
from django.contrib.auth.models import AbstractBaseUser, Permission
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CUserManager
# Create your models here.


class CPermissionMixin(models.Model):
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_superuser = models.BooleanField(_("superuser status"), default=False)
    is_premium = models.BooleanField(_("premium account status"), default=False)

    is_suspend = models.BooleanField(_("suspend status"), default=False)

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="cuser_set",
        related_query_name="cuser",
    )


class CustomUser(AbstractBaseUser, CPermissionMixin):

    # What does it do when django normal unique validator exists?
    username_validator = UnicodeUsernameValidator()

    name = models.CharField(verbose_name=_("Name"), max_length=100)
    username = models.CharField(verbose_name=_("Username"), max_length=50, unique=True, validators=[username_validator])
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    room = models.ManyToManyField(verbose_name=_("Room"), to="users.Room", through="users.MemberShip")

    email = None
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = CUserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]
    
    def __str__(self):
        return self.name
    

class NotificationStatus(models.IntegerChoices):
    UNREAD = 1, _("unread")
    CHECKED = 2, _("checked")


class Notification(models.Model):

    reciver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(_("title"), max_length=50)
    text = models.TextField(_("notification text"), max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(NotificationStatus)
    
    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
