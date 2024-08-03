from datetime import (
    date,
    datetime,
)
from typing import Optional


def get_date_diff_year_and_month(start_date: date, end_date: Optional[date] = None) -> tuple[int, int]:
    now_date = datetime.now().date()
    years = (end_date and end_date.year or now_date.year) - start_date.year
    months = (end_date and end_date.month or now_date.month) - start_date.month
    if months < 0:
        years -= 1
        months += 12
    return years, months
