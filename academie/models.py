from django.db import models


class Academy(models.Model):
    name         = models.CharField(max_length=100)
    city         = models.CharField(max_length=100, blank=True)
    address      = models.TextField(blank=True)
    description  = models.TextField(blank=True)
    picture      = models.ImageField(upload_to='academies/', blank=True, null=True)
    specialities = models.JSONField(default=list, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OpeningHour(models.Model):
    DAYS = [
        ('monday',    'Monday'),
        ('tuesday',   'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday',  'Thursday'),
        ('friday',    'Friday'),
        ('saturday',  'Saturday'),
        ('sunday',    'Sunday'),
    ]

    academy      = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='opening_hours')
    day          = models.CharField(max_length=10, choices=DAYS)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_closed    = models.BooleanField(default=False)

    class Meta:
        unique_together = ('academy', 'day')
        ordering = ['id']

    def __str__(self):
        if self.is_closed:
            return f"{self.academy.name} – {self.day}: closed"
        return f"{self.academy.name} – {self.day}: {self.opening_time}–{self.closing_time}"


class SwimmingPool(models.Model):
    academy = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='swimming_pools')
    name = models.CharField(max_length=100)
    speciality = models.JSONField(default=list, blank=True)
    dimension = models.JSONField(default=list, blank=True)
    heated = models.BooleanField(default=False)
    showers = models.IntegerField(default=0)
    image = models.ImageField(upload_to='swimming_pools/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.academy.name})"