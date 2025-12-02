import logging
from typing import Dict, List
import os
import pandas as pd
import numpy as np
from config import Config
from commons.enums import (
    OptionType,
    ExpiryType,
    StandardSegment,
    TimeFrame,
)
from data import database
from data import metadata
from commons.constants import UNIVERSAL_NSE_INDEXES, VALID_INDEX_CASH_COLUMNS, VALID_INDEX_OPTIONS_COLUMNS
import numpy as np
from commons.constants import ONE_MINUTES_CANDLE_STAMPS

logger = logging.getLogger(__name__)



class Instrument:
    def __init__(self, token: str, option_type: OptionType, expiry: int, strike: float):
        self.token = token
        self.option_type = option_type
        self.expiry = expiry
        self.strike = strike


def adjust_exppiries() -> dict:
    for underlying in metadata.ar_expiries:
        for current_date in metadata.ar_expiries[underlying]:
            for expiry_type, expiry_value in metadata.ar_expiries[underlying][
                current_date
            ].items():
                if expiry_type == ExpiryType.ALL:
                    available_expiries = sorted(list(expiry_value))
                    weekly_expiry = available_expiries[0]
                    monthly_expiries = [
                        date
                        for date in available_expiries
                        if str(date)[2:4] == str(weekly_expiry)[2:4]
                    ]
            # Set the `weekly`, `next_weekly`, and `monthy`.
            metadata.ar_expiries[underlying][current_date][
                ExpiryType.WEEKLY
            ] = weekly_expiry
            metadata.ar_expiries[underlying][current_date][ExpiryType.NEXT_WEEKLY] = (
                available_expiries[1]
                if len(available_expiries) >= 2
                else available_expiries[0]
            )
            metadata.ar_expiries[underlying][current_date][ExpiryType.MONTHLY] = (
                monthly_expiries[-1]
            )



def validate_index_options(column_names: list) -> bool:
    if len(column_names) != 11:
        return 0

    if column_names != VALID_INDEX_OPTIONS_COLUMNS:
        return 0
    return 1

def validate_index_cash(column_names: list) -> bool:
    if len(column_names) != 7:
        return 0
    if column_names != VALID_INDEX_CASH_COLUMNS:
        return 0
    return 1

def is_valid_columns(column_names: list, is_index: bool, file_type: StandardSegment):
    if is_index:
        if (file_type == StandardSegment.CALL) or (file_type == StandardSegment.PUT):
            if not validate_index_options(column_names):
                return 0
        elif file_type == StandardSegment.CASH:
            if not validate_index_cash(column_names):
                return 0
        return 1
    else:
        # TODO: Data validation for equity is pending.
        # Thus returning zero as not validated data in the eq segment
        return 0

def resample_nested_array(arr: np.ndarray, n: int) -> np.ndarray:
    """
    Resample OHLC NumPy array by fixed number of rows (N per candle)
    arr: columns -> [index, time, open, high, low, close]
    n: number of rows to combine per candle
    """
    total = arr.shape[0]
    usable = total - (total % n)  # drop extra rows if not divisible
    reshaped = arr[:usable].reshape(-1, n, arr.shape[1])

    # Compute ohlc logic in one vectorized shot
    index = np.arange(len(reshaped))
    time = reshaped[:, 0, 1]
    open_ = reshaped[:, 0, 2]
    high = reshaped[:, :, 3].max(axis=1)
    low = reshaped[:, :, 4].min(axis=1)
    close = reshaped[:, -1, 5]

    # Handled, CE and PE both the cases here
    if arr.shape[1] == 6:
        return np.column_stack((index, time, open_, high, low, close))
    else:
        vol = reshaped[:, :, 6].sum(axis=1)
        oi = reshaped[:, -1, 7]
        return np.column_stack((index, time, open_, high, low, close, vol, oi))


def reload_metadata(
    is_index: bool, file_type: StandardSegment, query_result: List[tuple], index: str
):
    """
    updating metadata when it is necessary.
    1) update ar_day_quote
    2) upload another ar things
    3) also there is the code related to the future.
    """

    # {Date->{symbol: [[],[],[]]}}
    symbol_wise_data_mapping: Dict[int, Dict[str, List]] = {}
    expiry_mapper = {}

    for i, single_row in enumerate(query_result):
        row_time = single_row[1]

        # Extra checks as db having no longer goon cleaned data
        # Issue is same instrument has more than 1000 record for the day,
        # twice record for same time, duplicate entries
        if row_time not in ONE_MINUTES_CANDLE_STAMPS:
            continue

        date = single_row[0]
        trading_symbol = single_row[2]

        if index not in metadata.ar_day_quote:
            metadata.ar_day_quote[index] = {}

        if date not in metadata.ar_day_quote[index]:
            metadata.ar_day_quote[index][date] = {}
        if date not in symbol_wise_data_mapping:
            symbol_wise_data_mapping[date] = {}

        if trading_symbol not in metadata.ar_day_quote[index][date]:
            metadata.ar_day_quote[index][date][trading_symbol] = {}
        if trading_symbol not in symbol_wise_data_mapping[date]:
            symbol_wise_data_mapping[date][trading_symbol] = []

        if TimeFrame.ONE not in metadata.ar_day_quote[index][date][trading_symbol]:
            # TODO: Confirm the type-annotationn for arr.
            metadata.ar_day_quote[index][date][trading_symbol][TimeFrame.ONE] = []

        if (file_type == StandardSegment.CALL) or (file_type == StandardSegment.PUT):

            # Loading strike details in nested form.
            # -> index_name:date:ce/pe:expiry:set(strike)
            strike = single_row[3]
            if index not in metadata.ar_available_strikes:
                metadata.ar_available_strikes[index] = {}
            if date not in metadata.ar_available_strikes[index]:
                metadata.ar_available_strikes[index][date] = {}
            option_type = (
                OptionType.CE
                if file_type == StandardSegment.CALL
                else OptionType.PE if file_type == StandardSegment.PUT else None
            )
            if option_type not in metadata.ar_available_strikes[index][date]:
                metadata.ar_available_strikes[index][date][option_type] = {}
            if (
                single_row[4]
                not in metadata.ar_available_strikes[index][date][option_type]
            ):
                metadata.ar_available_strikes[index][date][option_type][
                    single_row[4]
                ] = set()
            metadata.ar_available_strikes[index][date][option_type][single_row[4]].add(
                strike
            )

            if index not in metadata.ar_expiries:
                metadata.ar_expiries[index] = {}
            if date not in metadata.ar_expiries[index]:
                metadata.ar_expiries[index][date] = {
                    ExpiryType.WEEKLY: None,
                    ExpiryType.NEXT_WEEKLY: None,
                    ExpiryType.MONTHLY: None,
                    ExpiryType.ALL: set(),
                }

            # Loading instrument details in nested form
            # -> date:time:underlying:ce/pe:expiry
            if date not in metadata.ar_instruments:
                metadata.ar_instruments[date] = {}
            if single_row[1] not in metadata.ar_instruments[date]:
                metadata.ar_instruments[date][single_row[1]] = {}
            if index not in metadata.ar_instruments[date][single_row[1]]:
                metadata.ar_instruments[date][single_row[1]][index] = {}
            if option_type not in metadata.ar_instruments[date][single_row[1]][index]:
                metadata.ar_instruments[date][single_row[1]][index][option_type] = {}
            if (
                single_row[4]
                not in metadata.ar_instruments[date][single_row[1]][index][option_type]
            ):
                metadata.ar_instruments[date][single_row[1]][index][option_type][
                    single_row[4]
                ] = {}
                metadata.ar_expiries[index][date][ExpiryType.ALL].add(single_row[4])
            if (
                strike
                not in metadata.ar_instruments[date][single_row[1]][index][option_type][
                    single_row[4]
                ]
            ):
                metadata.ar_instruments[date][single_row[1]][index][option_type][
                    single_row[4]
                ][strike] = Instrument(
                    single_row[2], option_type, single_row[4], single_row[3]
                )

            # index, time, o, h, l, c, vol, oi
            # strike on 3
            # Expiry on 4
            # instrument name on 2
            filtered_row = [
                i,
                single_row[1],
                single_row[5],
                single_row[6],
                single_row[7],
                single_row[8],
                single_row[9],
                single_row[10],
            ]
        elif file_type == StandardSegment.CASH:
            # available dates something like this symbol set(available dates)
            # index, time, o, h, l, c
            filtered_row = [
                i,
                single_row[1],
                single_row[3],
                single_row[4],
                single_row[6],
                single_row[5],
            ]
        symbol_wise_data_mapping[date][trading_symbol].append(filtered_row)

    logger.info("Started loading metadata and resampling arrays.")
    for symbol_wise_date in symbol_wise_data_mapping:
        for trading_instrument in symbol_wise_data_mapping[symbol_wise_date]:
            nested_arr = np.array(
                symbol_wise_data_mapping[symbol_wise_date][trading_instrument],
                dtype=np.float64,
            )
            # Sorting by time.
            nested_arr = nested_arr[nested_arr[:, 1].argsort()]
            # Adding whole day's unique symbol data to the mapper via array(min based).
            metadata.ar_day_quote[index][symbol_wise_date][trading_instrument][
                TimeFrame.ONE
            ] = nested_arr

            # TODO: Modify this check to only resample cash data.
            # Currently only working for the banknifty manually.
            if trading_instrument == ["BANKNIFTY"]:
                if (
                    TimeFrame.THREE
                    not in metadata.ar_day_quote[index][symbol_wise_date][
                        trading_instrument
                    ]
                ):
                    metadata.ar_day_quote[index][symbol_wise_date][trading_instrument][
                        TimeFrame.THREE
                    ] = []
                if (
                    TimeFrame.FIVE
                    not in metadata.ar_day_quote[index][symbol_wise_date][
                        trading_instrument
                    ]
                ):
                    metadata.ar_day_quote[index][symbol_wise_date][trading_instrument][
                        TimeFrame.FIVE
                    ] = []
                if (
                    TimeFrame.FIFTEEN
                    not in metadata.ar_day_quote[index][symbol_wise_date][
                        trading_instrument
                    ]
                ):
                    metadata.ar_day_quote[index][symbol_wise_date][trading_instrument][
                        TimeFrame.FIFTEEN
                    ] = []
                # Adding whole day's unique symbol data to the mapper via array(3/5/15min based).
                three_min_arr = resample_nested_array(nested_arr, 3)
                five_min_arr = resample_nested_array(nested_arr, 5)
                fifteen_min_arr = resample_nested_array(nested_arr, 15)
                metadata.ar_day_quote[index][symbol_wise_date][trading_instrument][
                    TimeFrame.THREE
                ] = three_min_arr
                metadata.ar_day_quote[index][symbol_wise_date][trading_instrument][
                    TimeFrame.FIVE
                ] = five_min_arr
                metadata.ar_day_quote[index][symbol_wise_date][trading_instrument][
                    TimeFrame.FIFTEEN
                ] = fifteen_min_arr
    logger.info("Completed loading metadata and resampling arrays.")


def load_index_data():
    logger.info("trying to connect with mysql database")
    cursor = database.connection.cursor()
    logger.info("Connected to mysql database")

    for index in UNIVERSAL_NSE_INDEXES:
        for file_type in StandardSegment:
            if file_type in [StandardSegment.FUT]:
                # Currently issue in the same symbol name issue for all futures
                # Thus not loading the data for that cases.
                continue
            logger.info(
                f"started downloading for index:{index} and segment is {file_type}"
            )
            query = f"SELECT * FROM {index + file_type.value} where date >= {Config.DATA_FROM} and date <= {Config.DATA_TO};"
            cursor.execute(query)
            query_result = cursor.fetchall()
            print(query_result[1])
            column_names = [desc[0] for desc in cursor.description]
            print(column_names)

            # Validating data(By making sure all necessary column is present), based on its type
            is_valid = is_valid_columns(column_names, True, file_type)
            if not is_valid:
                logger.info(
                    f"Issue in validating column for index:{index} and segment is {file_type}."
                )
                continue

            # Poping fewtched data to the metadata.
            unique_result = list(set(query_result))
            reload_metadata(True, file_type, unique_result, index)
            adjust_exppiries()

            logger.info(
                f"finished downloading for index:{index} and segment is {file_type}"
            )


month_map = {"01": "JAN", "02": "FEB", "03": "MAR", "04": "APR", "05": "MAY", "06": "JUN",
             "07": "JUL", "08": "AUG", "09": "SEP", "10": "OCT", "11": "NOV", "12": "DEC"}
dataset_folder_name = os.path.normpath("dataset")
cwd = os.getcwd()
dataset_path = os.path.join(cwd, dataset_folder_name)

def load_mapper(
    maper_dict: Dict[int, Dict[str, List[float]]],  # date:symbol:list[data]

):
    logger.info("trying to connect with file structure")
    logger.info("Connected to file structure")
    for current_date in range(int(Config.DATA_FROM), int(Config.DATA_TO)+1 ):
        if current_date not in maper_dict:
            maper_dict[current_date] = {}
        for underlying_name in UNIVERSAL_NSE_INDEXES:
            for file_type in StandardSegment:
                if file_type in [StandardSegment.FUT]:
                # Currently issue in the same symbol name issue for all futures
                # Thus not loading the data for that cases.
                    continue
                

                # --- Build file path ---
                year = f"20{str(current_date)[:2]}"
                month = month_map[str(current_date)[2:4]]
                day = str(current_date)[4:]
                file_name = f"{underlying_name.lower()}{file_type.value}.feather"   
                file_path = os.path.join(dataset_path, year, month, day, file_name)
                logger.info(
                    f"started downloading for index:{file_name} and segment is {file_type}"
                )
                if not os.path.exists(file_path):
                    logger.warning(f"File not found: {file_path}")
                    continue

                try:
                    
                    df = pd.read_feather(file_path)
                    # if isinstance(df.columns, pd.MultiIndex):
                    #     new_col = []
                    #     for col in df.columns:
                    #         if col[0] != "":
                    #             new_col.append(col[0])
                    #         else:
                    #             new_col.append(col[1])
                    #     df.columns = new_col
                    re_ordered_data=['date', 'time', 'symbol', 'strike', 'expiry', 'open', 'high', 'low', 'close', 'volume', 'oi']
                    
                    existing_cols = []
                    for column in re_ordered_data:
                        if column in df.columns:
                            existing_cols.append(column)
                    df=df[existing_cols]
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
                column_names = df.columns.to_list()
                values=df.head(1)



                
                
                # Validating data(By making sure all necessary column is present), based on its type
                is_valid = is_valid_columns(column_names, True, file_type)
                if not is_valid:
                    logger.info(
                        f"Issue in validating column for index:{underlying_name} and segment is {file_type}."
                    )
                    break
                # --- Process each row ---
                if file_type == StandardSegment.CALL and file_type==StandardSegment.PUT:
                    for _, row in df.iterrows():
                        date = int(row["date"])
                        time = int(row["time"])
                        symbol = str(row["symbol"])
                        strike = float(row["strike"])
                        expiry = float(row["expiry"]) 
                        open = float(row["open"])
                        high = float(row["high"])
                        low = float(row["low"])
                        close = float(row["close"])
                        volume = float(row["volume"]) 
                        oi = float(row["oi"]) 

                        if symbol not in maper_dict[current_date]:
                            maper_dict[current_date][symbol] = []
                        maper_dict[current_date][symbol].append(
                            [date,time,symbol,strike,expiry, open, high, low, close,volume,oi]
                        )
                elif file_type == StandardSegment.CASH:
                    for _, row in df.iterrows():
                        date = int(row["date"])
                        time = int(row["time"])
                        symbol = str(row["symbol"])
                        open = float(row["open"])
                        high = float(row["high"])
                        low = float(row["low"])
                        close = float(row["close"])

                        if symbol not in maper_dict[current_date]:
                            maper_dict[current_date][symbol] = []
                        maper_dict[current_date][symbol].append(
                            [date,time,symbol, open, high, low, close]
                        )

                # --- Deduplicate and update metadata ---
                all_data = [
                    tuple(item)
                    for symbol_data in maper_dict[current_date].values()
                    for item in symbol_data
                ]
            
                # Poping fewtched data to the metadata.
                unique_result = list(set(all_data))
                reload_metadata(True, file_type, unique_result, underlying_name)
                adjust_exppiries()
                
                logger.info(
                f"finished downloading for index:{underlying_name} and segment is {file_type}   "
            )
        logger.info(f"File loading completed successfully.")
            # print("done for the filename, date", file_name, current_date)

maper_dict = {}
def load_universal_metadata():
    # load_index_data()
    load_mapper(maper_dict)

