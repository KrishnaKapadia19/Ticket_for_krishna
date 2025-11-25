from enum import Enum


class Exchange(Enum):
    ARK = 0
    NSE = 1
    BSE = 2
    NFO = 3
    BFO = 5


class Segment(Enum):
    CM = 0
    FNO = 1
    CD = 2


class InstrumentType(Enum):
    EQ = 0
    FUTSTK = 1
    OPTSTK = 2
    FUTIDX = 3
    OPTIDX = 4


class OptionType(Enum):
    EQ = 0
    FUT = 1
    CE = 2
    PE = 3


class TimeFrame(Enum):
    ONE = 1
    THREE = 3
    FIVE = 5
    FIFTEEN = 15


class StandardSegment(Enum):
    CALL = "_call"
    PUT = "_put"
    CASH = "_cash"
    FUT = "_future"


class CashMetricType(Enum):
    CASH = "CASH"
    INDICATOR = "INDICATOR"


class ExpiryType(Enum):
    WEEKLY = "WEEKLY"
    NEXT_WEEKLY = "NEXT_WEEKLY"
    MONTHLY = "MONTHLY"
    ALL = "ALL"


class TargetSlType(Enum):
    UNDERLYING_POINT = "UNDERLYING_POINT"
    UNDERLYING_PERCENT = "UNDERLYING_PERCENT"
    INSTRUMENT_POINT = "INSTRUMENT_POINT"
    INSTRUMENT_PERCENT = "INSTRUMENT_PERCENT"


class ReEntryType(Enum):
    ASAP = "ASAP"
    ASAP_R = "ASAP_R"
    COST = "COST"
    COST_R = "COST_R"


class MomentumType(Enum):
    UNDERLYING_POINT = "UNDERLYING_POINT"
    UNDERLYING_PERCENT = "UNDERLYING_PERCENT"
    INSTRUMENT_POINT = "INSTRUMENT_POINT"
    INSTRUMENT_PERCENT = "INSTRUMENT_PERCENT"


class TrailingMoveType(Enum):
    POINT = "POINT"
    PERCENT = "PERCENT"


class TrailingMethod(Enum):
    ONCE = "ONCE"
    CONTINUOUS = "CONTINUOUS"


class PositionType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OptionType(Enum):
    CE = "CE"
    PE = "PE"


class OverallProfitLossType(Enum):
    MTM = "MTM"
    PERCENT = "PERCENT"


class StrategyType(Enum):
    GEN = 0


class ExecutionMode(Enum):
    BACKTEST = 0
    PAPER = 1
    LIVE = 2


class OrderType(Enum):
    MARKET = 0
    LIMIT = 1
    STOP_LIMIT = 2
    STOP_MARKET = 3


class ProductType(Enum):
    NRML = 0
    MIS = 1
    CNC = 2


class Side(Enum):
    BUY = 0
    SELL = 1


class InstrumentSelectionType(Enum):
    BY_NAME = 0
    BY_PREMIUM = 1
    BY_ATM_DISTANCE = 2


class LegExecutionStatus(Enum):
    CREATED = 0
    ENTRY_TRANSITION = 1
    ENTERED = 2
    EXIT_TRANSITION = 3
    EXITED = 4
    ERROR = 5


class IndicatorsType(Enum):
    SMA = "SMA"
    EMA = "EMA"
    RSI = "RSI"
    ORB_OPEN = "ORB_OPEN"
    ORB_HIGH = "ORB_HIGH"
    ORB_LOW = "ORB_LOW"
    ORB_CLOSE = "ORB_CLOSE"


class ArrayIndex(Enum):
    # index, time, o,h,l,c,v,o -> t-1, o-2, h-3, l-4, c-5
    OPEN = 2
    HIGH = 3
    LOW = 4
    CLOSE = 5


class BlockStatus(Enum):
    ENTRY_CHECKING = "ENTRY_CHECKING"
    EXIT_CHECKING = "EXIT_CHECKING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class StrategyExecutionStatus(Enum):
    CREATED = 0
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3
    COMPLETED = 4
    ERROR = 5


class OrderExecutionStatus(Enum):
    CREATED = 0
    SENT = 1
    PENDING = 2
    OPEN = 3
    FILLED = 4
    CANCELLED = 5
    REJECTED = 6
    ERROR = 7


class ExitReasonType(Enum):
    TARGET_HIT = "TARGET_HIT"
    STOPLOSS_HIT = "STOPLOSS_HIT"
    TIME_BASED_EXIT = "TIME_BASED_EXIT"
    BLOCK_EXIT_CONDITION = "BLOCK_EXIT_CONDITION"
