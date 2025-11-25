
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] [%(threadName)s] : %(message)s",
)
logger = logging.getLogger(__name__)

from data import load_universal_metadata
load_universal_metadata()