# (c) Crown Owned Copyright, 2016. Dstl.

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.teams.models import Team


class UserManager(BaseUserManager):
    def create_user(self, userid=None, password=None, **extra_fields):
        now = timezone.now()
        fields = {
            'date_joined': now,
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'last_login': now,
            'userid': userid,
        }

        # Allow kwargs to over-write default value for is_active etc.
        fields.update(extra_fields)

        user = self.model(**fields)

        # create a unique slug (TODO there is a race condition
        # here, just a very unlikely to occur one)
        new_slug = None
        suffix = 0
        while new_slug is None:
            test_slug = slugify(user.userid)
            if suffix:
                test_slug = '%s%s' % (test_slug, suffix)
            try:
                User.objects.get(slug=test_slug)
            except User.DoesNotExist:
                new_slug = test_slug
            suffix = suffix + 1

        user.slug = new_slug
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, userid, password, **extra_fields):
        user = self.create_user(userid, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(PermissionsMixin, AbstractBaseUser):
    """
    Custom user class that calls the unique login identifier "userid" and
    because it has no restrictions on what it can contain (unlike the default
    django user model) we also use a slug. Also don't split the user's name
    into first/last for no real reason.
    """

    userid = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=256, unique=True)
    name = models.CharField(max_length=512, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    best_way_to_find = models.CharField(
        max_length=1024, blank=True, default='')
    best_way_to_contact = models.CharField(
        max_length=1024, blank=True, default='')
    phone = models.CharField(max_length=256, blank=True, default='')
    email = models.CharField(max_length=256, blank=True, default='')
    teams = models.ManyToManyField(Team)

    objects = UserManager()

    USERNAME_FIELD = 'userid'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['name', 'userid']

    def get_full_name(self):
        return self.name or self.userid

    def get_short_name(self):
        return self.name or self.userid

    def top_links(self):
        from apps.links.models import Link
        #   Get the 'top' links/tools for the selected users
        return Link.objects.filter(usage__user=self).annotate(
            linkusagecount=models.Count('usage')
        ).order_by('-linkusagecount', 'name')

    def __str__(self):
        return self.get_full_name()
