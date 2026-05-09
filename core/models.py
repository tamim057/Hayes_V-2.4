from django.db import models


class Duty(models.Model):

    user_id = models.CharField(max_length=100)

    is_on_duty = models.BooleanField(default=False)

    start_time = models.DateTimeField(
        null=True,
        blank=True
    )

    total_seconds = models.IntegerField(default=0)

    bell_required = models.BooleanField(default=False)

    last_cycle = models.IntegerField(default=0)

    last_bell = models.DateTimeField(
        null=True,
        blank=True
    )

    # DAILY RESET FIELD
    last_reset = models.CharField(
        max_length=20,
        default=""
    )