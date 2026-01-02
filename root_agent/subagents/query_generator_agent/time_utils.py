from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import re
import dateparser

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20
}

def normalize_number_words(text: str) -> str:
    for word, number in NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", str(number), text)
    return text

def _to_utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc).replace(tzinfo=timezone.utc)

def _parse_any_datetime(text: str) -> Optional[datetime]:
    dt = dateparser.parse(text, settings={
        "RETURN_AS_TIMEZONE_AWARE": True,
        "TIMEZONE": "UTC",
        "TO_TIMEZONE": "UTC",
        "PREFER_DATES_FROM": "past"
    })
    return _to_utc(dt) if dt else None

def to_utc_from_string(datetime_str: str) -> Optional[str]:
    dt = _parse_any_datetime(datetime_str)
    if dt:
        return dt.isoformat()
    return None

def parse_time_expression(expression: str) -> Optional[Dict[str, Dict[str, datetime]]]:
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    expression = normalize_number_words(expression.strip().lower())
    filters = {}
    expression = expression.strip().lower()

    if expression == "today":
        filters = {"$gte": today_start, "$lt": today_start + timedelta(days=1)}

    elif expression in ["past week", "this week"]:
        start_of_week = today_start - timedelta(days=today_start.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        filters = {"$gte": start_of_week, "$lt": end_of_week}

    elif expression == "this month":
        start_of_month = today_start.replace(day=1)
        next_month = (start_of_month.replace(month=1, year=start_of_month.year + 1)
                      if start_of_month.month == 12
                      else start_of_month.replace(month=start_of_month.month + 1))
        filters = {"$gte": start_of_month, "$lt": next_month}

    elif expression == "yesterday":
        filters = {"$gte": today_start - timedelta(days=1), "$lt": today_start}

    elif expression in ["before today", "till yesterday"]:
        filters = {"$lt": today_start}

    elif expression in ["this year", "current year"]:
        start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
        end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        filters = {"$gte": start, "$lt": end}

    elif expression == "since yesterday":
        filters = {"$gte": today_start - timedelta(days=1)}

    elif match := re.match(r"last\s+(\d+)\s*(hours|hour)", expression):
        filters = {"$gte": now - timedelta(hours=int(match.group(1)))}

    elif match := re.match(r"last\s+(\d+)\s*(days|day)", expression):
        filters = {"$gte": now - timedelta(days=int(match.group(1)))}

    elif match := re.match(r"since\s+(\d+)\s*(days|day)", expression):
        filters = {"$gte": now - timedelta(days=int(match.group(1)))}

    elif match := re.match(r"from\s+(.+?)\s+to\s+(.+)", expression):
        start, end = _parse_any_datetime(match.group(1)), _parse_any_datetime(match.group(2))
        if start and end:
            filters = {"$gte": start, "$lt": end}

    elif match := re.match(r"from\s+(.+)", expression):
        start = _parse_any_datetime(match.group(1))
        if start:
            filters = {"$gte": start}

    elif match := re.match(r"(before|till)\s+(.+)", expression):
        end = _parse_any_datetime(match.group(2))
        if end:
            filters = {"$lt": end}

    else:
        single = _parse_any_datetime(expression)
        if single:
            start = single.replace(hour=0, minute=0, second=0, microsecond=0)
            filters = {"$gte": start, "$lt": start + timedelta(days=1)}

    return {"start_time": filters} if filters else None
