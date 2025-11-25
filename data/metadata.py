from typing import Dict, List, Set

import numpy as np
from commons.enums import ExpiryType, OptionType, TimeFrame

class Instrument:
    def __init__(self, token: str, option_type: OptionType, expiry: int, strike: float):
        self.token = token
        self.option_type = option_type
        self.expiry = expiry
        self.strike = strike

class Quote:
    def __init__(
        self,
        instrument_id: str,
        open: float,
        high: float,
        low: float,
        close: float,
        oi: int = 0,
        volume: int = 0,
    ):
        self.instrument_id = instrument_id
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.oi = oi
        self.volume = volume

available_dates: Dict[str, Set[int]] = {}
available_expiries: Dict[str, Dict[int, List[int]]] = {}
available_instruments: Dict[str, List[Instrument]] = {}
cash_data: Dict[str, Dict[str, Quote]] = {}
call_data: Dict[str, Dict[str, Quote]] = {}
put_data: Dict[str, Dict[str, Quote]] = {}
put_data: Dict[str, Dict[str, Quote]] = {}
cd_data: Dict[str, Dict[str, Quote]] = {}

# expiry need something like index=>date=>expiry_type=>expiry_int_value
ar_expiries: Dict[str, Dict[int, Dict[ExpiryType, int]]] = {}

# available dates something like this symbol set(available dates)
ar_available_dates: Dict[str, Set[int]] = {}

# Strike need something like index=>date=>strikes
# ar_available_strikes: Dict[str, Dict[int, Set[float]]] = {}
# underlying.date.ce/pe.expiry -> set(strike)
ar_available_strikes: Dict[str, Dict[int, Dict[OptionType, Dict[int, Set[int]]]]] = {}
ar_instruments: Dict[
    int, Dict[int, Dict[str, Dict[OptionType, Dict[int, Dict[float, Instrument]]]]]
] = {}


# Note:- main arch for the arr
# Currently thinking the structure like symbol:date: trading_symbol:timeframe: arr of [index, date, time, open, high, low, close, volume or None, oi or None]
# Load this from the metadata.
# {index_name: {int_date: {trading_symbol: {timeframe: array_data}}}}
ar_day_quote: Dict[str, Dict[int, Dict[str, Dict[TimeFrame, np.ndarray]]]] = {}
# {index_name: {int_date: {trading_symbol: {indicator_name: {{timeframe: array_data}}}}}}
ar_day_indicators: Dict[
    str, Dict[int, Dict[str, Dict[str, Dict[TimeFrame, np.ndarray]]]]
] = {}
