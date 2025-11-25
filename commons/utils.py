def round_to(n: float, precision: float):
    correction = 0.5 if n >= 0 else -0.5
    return round(int(n / (precision) + correction) * precision, 16)


from commons.constants import (
    THREE_MINUTES_CANDLE_STAMPS,
    FIVE_MINUTE_CANDLE_STAMPS,
    FIFTEEN_MINUTE_CANDLE_STAMP,
)
from commons.enums import TimeFrame
from datetime import datetime, timedelta
from commons.constants import ENTRY_DATE_GREATER_ERROR, INVALID_DATE


def is_valid_entry_time(time_frame: TimeFrame, current_time: int) -> bool:
    if time_frame == TimeFrame.ONE:
        return True

    elif time_frame == TimeFrame.THREE:
        if current_time in THREE_MINUTES_CANDLE_STAMPS:
            return True
        else:
            return False

    elif time_frame == TimeFrame.FIVE:
        if current_time in FIVE_MINUTE_CANDLE_STAMPS:
            return True
        else:
            return False

    elif time_frame == TimeFrame.FIFTEEN:
        if current_time in FIFTEEN_MINUTE_CANDLE_STAMP:
            return True
        else:
            return False


def valid_date_time(number: int, number_as_date: bool = True) -> bool:
    fmt = "%y%m%d" if number_as_date else "%H:%M:%S"
    datetime_obj = number if number_as_date else timedelta(seconds=number)
    try:
        datetime.strptime(str(datetime_obj), fmt)
        # Extra validations for time.
        if not number_as_date:
            if not str(datetime_obj).endswith(":00"):
                return 0
        return 1
    except:
        return 0

def validate_entry_exit_params(
    entry_date, exit_date
):
    if (not valid_date_time(entry_date)) or (not valid_date_time(exit_date)):
        return INVALID_DATE
    if entry_date > exit_date:
        return ENTRY_DATE_GREATER_ERROR
