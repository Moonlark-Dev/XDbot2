import datetime
from ._utils import *

def calculate_percentage_of_year() -> float:
    """
    Calculate the percentage of the current year that has passed, considering leap years.
    
    Returns:
        float: The percentage of the year completed.
    """
    current_datetime = datetime.datetime.now()
    start_of_year = datetime.datetime(current_datetime.year, 1, 1)
    if current_datetime.year % 4 == 0 and (current_datetime.year % 100 != 0 or current_datetime.year % 400 == 0):
        total_seconds_in_year = 31622400  # Leap year (366 days)
    else:
        total_seconds_in_year = 31536000  # Non-leap year (365 days)
    elapsed_seconds = (current_datetime - start_of_year).total_seconds()
    percentage_complete = round((elapsed_seconds / total_seconds_in_year) * 100, 3)
    return percentage_complete

def calculate_percentage_of_month() -> float:
    """
    Calculate the percentage of the current month that has passed.

    Returns:
        float: The percentage of the month completed.
    """
    current_datetime = datetime.datetime.now()
    start_of_month = datetime.datetime(current_datetime.year, current_datetime.month, 1)
    if current_datetime.month == 12:
        next_month = datetime.datetime(current_datetime.year + 1, 1, 1)
    else:
        next_month = datetime.datetime(current_datetime.year, current_datetime.month + 1, 1)
    days_in_month = (next_month - start_of_month).days
    total_seconds_in_month = days_in_month * 24 * 60 * 60
    elapsed_seconds = (current_datetime - start_of_month).total_seconds()
    percentage_complete = round((elapsed_seconds / total_seconds_in_month) * 100, 3)
    return percentage_complete


def calculate_percentage_of_day() -> float:
    """
    Calculate the percentage of the current day that has passed.

    Returns:
        float: The percentage of the day completed.
    """
    current_datetime = datetime.datetime.now()
    start_of_day = datetime.datetime(current_datetime.year, current_datetime.month, current_datetime.day)
    total_seconds_in_day = 24 * 60 * 60
    elapsed_seconds = (current_datetime - start_of_day).total_seconds()
    percentage_complete = round((elapsed_seconds / total_seconds_in_day) * 100, 3)
    return percentage_complete

@create_command("progress-year", {"prog-y", "progress-y"})
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    await finish("progress.year", [datetime.datetime.now().year, calculate_percentage_of_year()], event.user_id)

@create_command("progress-month", {"prog-m", "progress-m"})
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    await finish("progress.mon", [
        (current_datetime := datetime.datetime.now()).year,
        current_datetime.month,
        calculate_percentage_of_month()
    ], event.user_id)

@create_command("progress-day", {"prog-d", "progress-d"})
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    await finish("progress.day", [
        (current_datetime := datetime.datetime.now()).year,
        current_datetime.month,
        current_datetime.day,
        calculate_percentage_of_day()  # Fixed the function to use calculate_percentage_of_day
    ], event.user_id)
