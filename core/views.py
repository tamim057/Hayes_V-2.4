from zoneinfo import ZoneInfo
from datetime import datetime
from django.shortcuts import render
import json
import logging
import os
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Duty

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

WEBHOOK = os.getenv('DISCORD_WEBHOOK_URL', '')
BELL_TIME = int(os.getenv('BELL_TIME', '15'))
GRACE = int(os.getenv('GRACE_PERIOD', '10'))


def get_user(user_id):

    user, _ = Duty.objects.get_or_create(user_id=user_id)

    check_daily_reset(user)

    return user

def safe_json(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON received: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing request body: {e}")
        return None


# LOGIN
@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    data = safe_json(request)
    if not data:
        return JsonResponse({"error": "invalid json"}, status=400)

    get_user(data["user_id"])
    return JsonResponse({"ok": True})


# ON DUTY
@csrf_exempt
def on_duty(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    data = safe_json(request)
    if not data:
        return JsonResponse({"error": "invalid json"}, status=400)

    u = get_user(data["user_id"])

    # ALREADY ON DUTY
    if u.is_on_duty:

        return JsonResponse({
        "status": "already_on"
    })

    u.is_on_duty = True

    u.start_time = timezone.now()

    u.bell_required = False

    u.last_cycle = 0

    u.save()

    send_webhook(
        u.user_id,
        "🟢 ON DUTY STARTED",
        0,
        u.total_seconds
    )

    return JsonResponse({"status": "on"})


# OFF DUTY
@csrf_exempt
def off_duty(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    data = safe_json(request)
    if not data:
        return JsonResponse({"error": "invalid json"}, status=400)

    u = get_user(data["user_id"])
    # ALREADY OFF DUTY
    if not u.is_on_duty:

        return JsonResponse({
            "status": "already_off"
        })

    session_seconds = 0

    if u.start_time:
        session_seconds = int((timezone.now() - u.start_time).total_seconds())

        u.total_seconds += session_seconds

    u.is_on_duty = False
    u.start_time = None
    u.bell_required = False
    u.save()

    send_webhook(
    u.user_id,
    "🔴 OFF DUTY",
    session_seconds,
    u.total_seconds
    )

    return JsonResponse({"status": "off"})


# BELL
@csrf_exempt
def bell(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    data = safe_json(request)
    if not data:
        return JsonResponse({"error": "invalid json"}, status=400)

    u = get_user(data["user_id"])

    u.bell_required = False
    u.last_bell = timezone.now()
    u.save()
    
    return JsonResponse({"status": "bell_ok"})


# WEBHOOK FUNCTION



def format_time(seconds):

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    return f"{h}h {m}m {s}s"


def send_webhook(user_id, action, session_seconds=0, total_seconds=0):

    session_text = format_time(session_seconds)
    total_text = format_time(total_seconds)

    mention = f"<@{user_id}>"

    color = 0xff0000

    if "ON DUTY" in action:
        color = 0x00ff00

    elif "BELL" in action:
        color = 0xf59e0b

    data = {

        "content": mention,

        "username": "🔥 Duty System",

        "embeds": [
            {
                "title": "📊 Duty Report",

                "color": color,

                "fields": [

                    {
                        "name": "👤 Member",
                        "value": mention,
                        "inline": True
                    },

                    {
                        "name": "⚡ Action",
                        "value": action,
                        "inline": True
                    },

                    {
                        "name": "⏱ Session",
                        "value": session_text,
                        "inline": True
                    },

                    {
                        "name": "📅 Today Total",
                        "value": total_text,
                        "inline": False
                    }

                ],

                "footer": {
                    "text": "Duty System PRO"
                },

                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }

    if not WEBHOOK:
        logger.warning("Discord webhook URL not configured. Skipping webhook.")
        return

    try:
        response = requests.post(WEBHOOK, json=data, timeout=5)
        response.raise_for_status()
        logger.debug(f"Webhook sent successfully for user {user_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send webhook for user {user_id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending webhook: {e}")

def home(request):
    return render(request, "index.html")





#12AM RESET 
def check_daily_reset(user):

    bd_time = datetime.now(ZoneInfo("Asia/Dhaka"))

    today = bd_time.strftime("%Y-%m-%d")

    if user.last_reset != today:

        user.total_seconds = 0

        user.last_reset = today

        user.save()


#reset 
@csrf_exempt
def status(request):

    user_id = request.GET.get("user_id")

    if not user_id:
        return JsonResponse({"error": "missing user"})

    u = get_user(user_id)

    session = 0

    if u.start_time:
        session = int(
            (timezone.now() - u.start_time).total_seconds()
        )

    grace = 0

    if u.bell_required and u.last_bell:

        grace = GRACE - int(
            (timezone.now() - u.last_bell).total_seconds()
        )

        if grace < 0:
            grace = 0

    return JsonResponse({

        "is_on_duty": u.is_on_duty,

        "session": session,

        "bell_required": u.bell_required,

        "grace": grace,

        "total": u.total_seconds
    })