import pm4py
import pandas as pd
from core.logger_config import setup_logger

logger = setup_logger(__name__)


def load_xes_log(file_path: str) -> pd.DataFrame:
    try:
        event_log = pm4py.read_xes(file_path, variant="rustxes")
        return event_log
    except Exception as e:
        logger.error(f"Error loading event log from: {file_path}: {e}")
        return None
