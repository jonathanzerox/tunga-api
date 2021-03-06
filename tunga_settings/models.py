from __future__ import unicode_literals

from django.db import models

# Create your models here.
from tunga import settings

VISIBILITY_DEVELOPER = 1
VISIBILITY_MY_TEAM = 2
VISIBILITY_CUSTOM = 3
VISIBILITY_ONLY_ME = 4
VISIBILITY_CHOICES = (
    (VISIBILITY_DEVELOPER, 'Developers'),
    (VISIBILITY_MY_TEAM, 'My Team'),
    (VISIBILITY_CUSTOM, 'Custom'),
    (VISIBILITY_ONLY_ME, 'Only Me')
)


class Setting(models.Model):
    slug = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100, verbose_name='display name')
    description = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='%(class)s_created', on_delete=models.DO_NOTHING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s - %s' % (self.slug, self.name)

    class Meta:
        abstract = True


class SwitchSetting(Setting):
    default_value = models.BooleanField()


class VisibilitySetting(Setting):
    default_value = models.PositiveSmallIntegerField(choices=VISIBILITY_CHOICES)


class UserSetting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Settings - %s' % self.user.get_short_name()

    class Meta:
        abstract = True


class UserSwitchSetting(UserSetting):
    setting = models.ForeignKey(SwitchSetting)
    value = models.BooleanField()

    class Meta:
        unique_together = ('user', 'setting')


class UserVisibilitySetting(UserSetting):
    setting = models.ForeignKey(VisibilitySetting)
    value = models.PositiveSmallIntegerField(choices=VISIBILITY_CHOICES)

    class Meta:
        unique_together = ('user', 'setting')
