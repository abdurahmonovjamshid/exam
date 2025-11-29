from django.db import models
from django.utils.timezone import now

class TgUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, default='-')

    is_bot = models.BooleanField(default=False)
    language_code = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Joined')

    deleted = models.BooleanField(default=False)

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name or ''}".strip()
        return (full_name[:30] + '...') if len(full_name) > 30 else full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


class Menu(models.Model):
    key = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class JobCategory(models.Model):
    name = models.CharField(max_length=100)  # e.g. Office, Zavod, Region
    icon = models.CharField(max_length=20, blank=True, null=True)  # emoji icon

    def __str__(self):
        return self.name

class Location(models.Model):
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # Add coordinates
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    user = models.ForeignKey(TgUser, on_delete=models.CASCADE)

    birth_date = models.DateField()
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)

    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    previous_job = models.CharField(max_length=255, blank=True, null=True)

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)

    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[("new", "New"), ("review", "In Review"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        default="new"
    )

    def __str__(self):
        return f"{self.user.full_name} – {self.position}"


class PageContent(models.Model):
    key = models.CharField(max_length=50, unique=True)
    text = models.TextField()
    image = models.ImageField(upload_to='content/', blank=True, null=True)

    def __str__(self):
        return self.key
