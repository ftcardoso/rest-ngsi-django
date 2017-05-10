from django.db import models
try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey    
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from doh.models import Hook
import jsonfield
import isodate
import datetime


def duration_to_datetime(duration):
    duration = isodate.parse_duration(duration)
    return datetime.datetime.now() + duration


class HookRelation(models.Model):
    hook = models.OneToOneField(Hook)
    subscription = models.ForeignKey('Subscription')


class Subscription(models.Model):
    hooks = models.ManyToManyField(Hook, through='HookRelation')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    attributes = jsonfield.JSONField(null=True, blank=True)
    conditions = jsonfield.JSONField(null=True, blank=True)

    def destroy(self):
        self.hooks.all().delete()
        self.delete()

    def update(self, duration=None, conditions=None):
        if duration:
            self.hooks.update(expiration_date=duration_to_datetime(duration))
        if conditions:
            self.conditions = conditions
            self.save()
        return self
            
    @classmethod
    def create(cls, instances, user, duration, target, conditions, attributes):
        
        def create_hook(content_object, expiration_date):
            hook = Hook(
                user=user, target=target, content_object=content_object,
                expiration_date=expiration_date
            )
            hook.validate_and_save()
            return hook
                
        def create_hooks():
            expiration_date = duration_to_datetime(duration)
            return [
                create_hook(each, expiration_date) for each in instances
            ]
        
        subscription = cls.objects.create(
            attributes=attributes, conditions=conditions, user=user
        )
        subscription.hooks.add(*create_hooks())
        return subscription
