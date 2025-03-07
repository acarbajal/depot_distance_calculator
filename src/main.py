# src/main.py
import logging
from src.excel_handler import ExcelHandler
from src.time_calculator import TimeCalculator
import sys
sys.path.append('..')
from config import GOOGLE_MAPS_API_KEY, MAPQUEST_API_KEY
import argparse


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('depot_distances.log')
        ]
    )

def main(excel_file_path: str, test_limit: int = None):
    """
    Main function to orchestrate the distance calculation process.
    
    Args:
        excel_file_path: Path to the Excel file
        test_limit: Optional limit on number of pairs to process (for testing)
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        
        # Verify API keys are available
        if not MAPQUEST_API_KEY:
            raise ValueError("MapQuest API key is not configured. Please check your .env file.")
        
        # Initialize handlers
        excel_handler = ExcelHandler(excel_file_path)
        #time_calculator = TimeCalculator(MAPQUEST_API_KEY, "mapquest")
        time_calculator = TimeCalculator(GOOGLE_MAPS_API_KEY, "google")
        
        # Read depot data
        logger.info("Reading depot data from Excel file...")
        depots_df = excel_handler.read_depot_data()
        
        # Calculate times
        logger.info(f"Calculating driving times between depots{' (TEST MODE)' if test_limit else ''}...")
        times_df = time_calculator.calculate_times(depots_df, test_limit=test_limit)
        
        
        # Write results
        logger.info("Writing results to Excel file...")
        excel_handler.write_times(times_df)
        
        logger.info("Process completed successfully!")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate driving times between depots')
    parser.add_argument('excel_file', help='Path to the Excel file')
    parser.add_argument('--test', type=int, help='Number of depot pairs to process (for testing)')
    
    args = parser.parse_args()
    main(args.excel_file, test_limit=args.test)