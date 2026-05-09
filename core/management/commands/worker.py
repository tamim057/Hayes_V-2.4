import time
import requests

from zoneinfo import ZoneInfo
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Duty
from core.views import send_webhook


# NORMAL DUTY WEBHOOK
WEBHOOK = "https://discord.com/api/webhooks/1501895480781705349/Tv_6YmCQQs3Vwaf1ItzJ6JhbWrh_HAofwqyKtrLMAG5_z96HpHtJDR0ti14arSnPONZw"

# LEADERBOARD WEBHOOK
LEADERBOARD_WEBHOOK = "https://discord.com/api/webhooks/1502736708913987666/q72328syYAXzJjdItx-A0-sx66UGtBp-iEUYqJ6o797trdybQbmx4jWCaRwXhA7K0-H3"


BELL_TIME = 15
GRACE = 10

last_leaderboard_date = ""


class Command(BaseCommand):

    help = "Duty background worker"

    def handle(self, *args, **kwargs):

        self.stdout.write(
            self.style.SUCCESS("Worker Started")
        )

        while True:

            # BANGLADESH TIME
            bd = datetime.now(
                ZoneInfo("Asia/Dhaka")
            )

            # SEND LEADERBOARD AT 12:00 AM
            if bd.hour == 0 and bd.minute == 0:

                send_daily_leaderboard()

            users = Duty.objects.all()

            for u in users:

                if not u.is_on_duty or not u.start_time:
                    continue

                diff = int(
                    (
                        timezone.now() - u.start_time
                    ).total_seconds()
                )

                # BELL TRIGGER
                cycles = diff // BELL_TIME

                if cycles > u.last_cycle:

                    u.last_cycle = cycles

                    u.bell_required = True

                    u.last_bell = timezone.now()

                    u.save()

                    print(
                        f"Bell Required For {u.user_id}"
                    )

                # AUTO OFF DUTY
                if u.bell_required and u.last_bell:

                    grace = int(
                        (
                            timezone.now() - u.last_bell
                        ).total_seconds()
                    )

                    print(f"Grace: {grace}")

                    if grace >= GRACE:

                        off_user(u)

            time.sleep(1)


def off_user(u):

    session = 0

    if u.start_time:

        session = int(
            (
                timezone.now() - u.start_time
            ).total_seconds()
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


# DAILY LEADERBOARD
def send_daily_leaderboard():

    global last_leaderboard_date

    bd = datetime.now(
        ZoneInfo("Asia/Dhaka")
    )

    today = bd.strftime("%Y-%m-%d")

    # PREVENT MULTIPLE SENDS
    if last_leaderboard_date == today:
        return

    users = Duty.objects.all().order_by(
        "-total_seconds"
    )

    leaderboard = ""

    rank = 1

    for u in users:

        if u.total_seconds <= 0:
            continue

        hours = u.total_seconds // 3600

        minutes = (
            u.total_seconds % 3600
        ) // 60

        medal = "🏅"

        if rank == 1:
            medal = "🥇"

        elif rank == 2:
            medal = "🥈"

        elif rank == 3:
            medal = "🥉"

        leaderboard += (
            f"{medal} {rank}. "
            f"<@{u.user_id}>\n"
            f"⏱ {hours}h {minutes}m\n\n"
        )

        rank += 1

    if leaderboard == "":
        return

    data = {

        "username": "🔥 Duty System",

        "embeds": [
            {
                "title":
                "🏆 Daily Duty Leaderboard",

                "description":
                leaderboard,

                "color": 0xf59e0b,

                "footer": {
                    "text":
                    "Duty System PRO"
                },

                "timestamp":
                datetime.utcnow().isoformat()
            }
        ]
    }

    try:

        requests.post(
            LEADERBOARD_WEBHOOK,
            json=data
        )

        print("Leaderboard Sent")

        last_leaderboard_date = today

        # RESET ALL USERS
        for u in users:

            u.total_seconds = 0

            u.last_reset = today

            u.save()

    except Exception as e:

        print(e)