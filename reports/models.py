from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_countries.fields import CountryField


class TreeReport(models.Model):
    """A tree reported by an I-V Tree community member."""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        PROTECTED = 'PROTECTED', 'Protected'
        RESOLVED = 'RESOLVED', 'Resolved'
        NEEDS_ATTENTION = 'NEEDS_ATTENTION', 'Needs Attention'

    class Visibility(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        PRIVATE = 'PRIVATE', 'Private'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tree_reports',
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=120)

    tree_species = models.CharField(
        max_length=120,
        blank=True,
    )

    description = models.TextField()

    photo = models.ImageField(
        upload_to='tree-reports/',
        blank=True,
    )

    # Temporary legacy field retained while older reports are migrated.
    location_name = models.CharField(
        max_length=255,
        blank=True,
    )

    country = CountryField(
        blank_label='Select country',
    )

    region = models.CharField(
        max_length=120,
        blank=True,
        help_text='County, state, province or region.',
    )

    town_city = models.CharField(
        max_length=120,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90),
        ],
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180),
        ],
    )

    what3words = models.CharField(
        max_length=80,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ProgressUpdate(models.Model):
    """A dated progress entry linked to an existing tree report."""

    tree_report = models.ForeignKey(
        TreeReport,
        on_delete=models.CASCADE,
        related_name='progress_updates',
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='progress_updates',
        null=True,
        blank=True,
    )

    description = models.TextField()

    photo = models.ImageField(
        upload_to='progress-updates/',
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=TreeReport.Status.choices,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Update for {self.tree_report.title}'