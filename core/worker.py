import time
import requests

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Duty
from core.views import send_webhook

BELL_TIME = 15
GRACE = 10


class Command(BaseCommand):

    help = "Duty background worker"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.SUCCESS("Worker Started"))

        while True:

            users = Duty.objects.all()

            for u in users:

                if not u.is_on_duty or not u.start_time:
                    continue

                diff = int(
                    (timezone.now() - u.start_time).total_seconds()
                )

                # BELL TRIGGER
                cycles = diff // BELL_TIME

                if cycles > u.last_cycle:

                    u.last_cycle = cycles

                    u.bell_required = True

                    u.last_bell = timezone.now()

                    u.save()

                    print(f"Bell Required For {u.user_id}")

                # AUTO OFF DUTY
                if u.bell_required and u.last_bell:

                    grace = int(
                        (timezone.now() - u.last_bell).total_seconds()
                    )

                    print(f"Grace: {grace}")

                    if grace >= GRACE:

                        off_user(u)

            time.sleep(1)


def off_user(u):

    session = 0

    if u.start_time:

        session = int(
            (timezone.now() - u.start_time).total_seconds()
        )

        u.total_seconds += session

    u.is_on_duty = False

    u.start_time = None

    u.bell_required = False

    u.save()

    send_webhook(
        u.user_id,
        "⛔ AUTO OFF DUTY",
        session,
        u.total_seconds
    )

    print(f"{u.user_id} AUTO OFF")