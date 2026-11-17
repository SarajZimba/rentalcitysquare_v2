from datetime import datetime, time, timedelta
from pytz import timezone as pytz_timezone

KATHMANDU_TZ = pytz_timezone("Asia/Kathmandu")

def get_operational_datetime(now=None):
    """
    Returns datetime at 00:00 for operational date,
    stored in DB so that __date filter works without timezone conversion.
    """
    now = timezone.localtime(timezone.now())
    shift_cutoff = time(6, 0)
    # Compute operational date in Kathmandu
    ktm_now = now.astimezone(KATHMANDU_TZ)
    if ktm_now.time() < shift_cutoff:
        operational_date = ktm_now.date() - timedelta(days=1)
    else:
        operational_date = ktm_now.date()

    print(f"operational_date {operational_date}")
    # Combine date with 00:00
    op_dt = datetime.combine(operational_date, time.min)

    # Trick: convert to UTC so DB stores op_dt +5:45
    op_dt_utc = op_dt + timedelta(hours=5, minutes=45)  # shift back to UTC
    return op_dt_utc


from django.utils import timezone
def get_operational_date(now=None):
    """
    Returns the operational date according to night shift:
    - If current time < 6:00 AM → previous day
    - Else → today
    """
    if not now:
        now = timezone.localtime(timezone.now())

    shift_cutoff = time(6, 0)  # 6:00 AM

    if now.time() < shift_cutoff:
        return now.date() - timedelta(days=1)
    return now.date()


from datetime import datetime, time, timedelta
from django.utils import timezone

def parse_frontend_datetime(date_str, time_str):
    """
    date_str: 'YYYY-MM-DD'
    time_str: 'H:MM AM/PM'
    """
    combined_str = f"{date_str} {time_str}"
    dt = datetime.strptime(combined_str, "%Y-%m-%d %I:%M %p")

    # make timezone aware if your project uses TZ
    return timezone.make_aware(dt)


from datetime import time, timedelta

def get_operational_date_from_datetime(dt):
    """
    If time < 6:00 AM → previous day
    Else → same day
    Returns date as string: YYYY-MM-DD
    """
    shift_cutoff = time(6, 0)  # 6:00 AM

    if dt.time() < shift_cutoff:
        op_date = dt.date() - timedelta(days=1)
    else:
        op_date = dt.date()

    return op_date.strftime("%Y-%m-%d")



