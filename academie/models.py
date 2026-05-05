from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


WEEKDAYS = [
    ('monday',    'Monday'),
    ('tuesday',   'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday',  'Thursday'),
    ('friday',    'Friday'),
    ('saturday',  'Saturday'),
    ('sunday',    'Sunday'),
]


class Academy(models.Model):
    owner        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_academies',
        limit_choices_to={'user_type': 'academy_owner'},
        null=True, blank=True,
    )
    name         = models.CharField(max_length=100)
    city         = models.CharField(max_length=100, blank=True)
    address      = models.TextField(blank=True)
    latitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description  = models.TextField(blank=True)
    picture      = models.ImageField(upload_to='academies/', blank=True, null=True)
    specialities  = models.JSONField(default=list, blank=True)
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OpeningHour(models.Model):
    academy      = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='opening_hours')
    day          = models.CharField(max_length=10, choices=WEEKDAYS)
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


class Course(models.Model):
    LEVEL_BEGINNER     = 'beginner'
    LEVEL_INTERMEDIATE = 'intermediate'
    LEVEL_ADVANCED     = 'advanced'

    LEVELS = (
        (LEVEL_BEGINNER,     'Beginner'),
        (LEVEL_INTERMEDIATE, 'Intermediate'),
        (LEVEL_ADVANCED,     'Advanced'),
    )

    academy     = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='courses')
    coach       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='taught_courses',
        limit_choices_to={'user_type': 'coach'},
        null=True, blank=True,
    )
    pool        = models.ForeignKey(
        SwimmingPool,
        on_delete=models.SET_NULL,
        related_name='courses',
        null=True, blank=True,
    )
    name            = models.CharField(max_length=100)
    description     = models.TextField(blank=True)
    level           = models.CharField(max_length=20, choices=LEVELS, default=LEVEL_BEGINNER)
    price_per_month = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.academy.name})"


class CourseTiming(models.Model):
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='timings')
    weekday    = models.CharField(max_length=10, choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time   = models.TimeField()

    class Meta:
        unique_together = ('course', 'weekday', 'start_time')
        ordering = ['weekday', 'start_time']

    def __str__(self):
        return f"{self.course.name} – {self.weekday} {self.start_time}–{self.end_time}"


class Review(models.Model):
    academy    = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating     = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('academy', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.academy.name} ({self.rating}/5)"


class Invitation(models.Model):
    STATUS_PENDING  = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'

    STATUSES = (
        (STATUS_PENDING,  'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
    )

    from_owner   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        limit_choices_to={'user_type': 'academy_owner'},
    )
    to_coach     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_invitations',
        limit_choices_to={'user_type': 'coach'},
    )
    academy      = models.ForeignKey(
        Academy,
        on_delete=models.CASCADE,
        related_name='coach_invitations',
        null=True, blank=True,
    )
    course       = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        related_name='invitations',
        null=True, blank=True,
    )
    status       = models.CharField(max_length=10, choices=STATUSES, default=STATUS_PENDING)
    created_at   = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('to_coach', 'academy')
        ordering = ['-created_at']

    def __str__(self):
        course_label = self.course.name if self.course else 'no course'
        return f"{self.from_owner} → {self.to_coach} [{course_label}] [{self.status}]"


class Subscription(models.Model):
    STATUS_ACTIVE    = 'active'
    STATUS_CANCELLED = 'cancelled'

    STATUSES = (
        (STATUS_ACTIVE,    'Active'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    user                  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        limit_choices_to={'user_type': 'user'},
    )
    academy               = models.ForeignKey(Academy, on_delete=models.CASCADE, related_name='subscriptions')
    course                = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        related_name='enrollments',
        null=True, blank=True,
    )
    price_at_subscription = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status                = models.CharField(max_length=20, choices=STATUSES, default=STATUS_ACTIVE)
    subscribed_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-subscribed_at']

    def __str__(self):
        return f"{self.user.username} → {self.academy.name} [{self.status}]"
