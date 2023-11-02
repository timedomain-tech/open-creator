import datetime
import time


def get_system_timezone():
    """
    This function returns the offset and name of the system's current timezone.
    It takes into account whether the system is currently observing daylight saving time.
    """
    # Get the offset of the current timezone
    offset = time.timezone

    # If it is currently daylight saving time, consider the offset of daylight saving time
    if time.daylight:
        offset = time.altzone

    # Convert the offset to a time difference string
    hours, remainder = divmod(abs(offset), 3600)
    minutes, _ = divmod(remainder, 60)
    tz_offset = ("+" if offset < 0 else "-") + f"{hours:02}:{minutes:02}"

    # Get the name of the timezone
    tz_name = time.tzname[0] if not time.daylight or time.localtime().tm_isdst == 0 else time.tzname[1]

    return tz_offset, tz_name


def get_local_time():
    """
    Get local time.
    First, get the current time in UTC.
    Then, convert the UTC time to the system's current timezone.
    Finally, format the time as "%Y-%m-%d %I:%M:%S %p %Z%z".
    """
    # Get the current time in UTC
    current_time_utc = datetime.datetime.now(datetime.timezone.utc)

    # Get the system's current timezone
    tz_offset, tz_name = get_system_timezone()
    system_tz = datetime.timezone(datetime.timedelta(hours=int(tz_offset[:3]), minutes=int(tz_offset[4:])), tz_name)

    # Convert to the system's current timezone
    local_time = current_time_utc.astimezone(system_tz)

    # Format the time as desired, including AM/PM
    formatted_time = local_time.strftime("%Y-%m-%d %I:%M:%S %p %Z%z")

    return formatted_time
