# src/excel_handler.py
import pandas as pd
from typing import Tuple, List
import logging
import sys
sys.path.append('..')  # Add parent directory to Python path
from config import INPUT_SHEET_NAME, OUTPUT_SHEET_NAME, REQUIRED_COLUMNS


class ExcelHandler:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)

    def read_depot_data(self) -> pd.DataFrame:
        """Read depot data from Excel file."""
        try:
            df = pd.read_excel(self.file_path, sheet_name=INPUT_SHEET_NAME)
            self._validate_dataframe(df)
            return df
        except Exception as e:
            self.logger.error(f"Error reading Excel file: {e}")
            raise

    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """Validate that required columns exist in the dataframe."""
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

    def write_times_and_distances(self, times_and_distances_df: pd.DataFrame) -> None:
        """Write driving times and distances data to Excel file."""
        try:
            with pd.ExcelWriter(self.file_path, mode='a', if_sheet_exists='replace') as writer:
                times_and_distances_df.to_excel(writer, sheet_name=OUTPUT_SHEET_NAME, index=False)
        except Exception as e:
            self.logger.error(f"Error writing to Excel file: {e}")
            raise

