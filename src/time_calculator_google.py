# src/time_calculator.py
import googlemaps
from typing import List, Dict, Tuple
import pandas as pd
import itertools
import logging
from time import sleep
import sys
sys.path.append('..')  # Add parent directory to Python path
###does not seem needed--- from config import GOOGLE_MAPS_API_KEY


class TimeCalculator:
    def __init__(self, api_key: str):
        self.gmaps = googlemaps.Client(key=api_key)
        self.logger = logging.getLogger(__name__)

    def calculate_times(self, depots_df: pd.DataFrame, test_limit: int = None) -> pd.DataFrame:
        """
        Calculate driving times between all pairs of depots.
        
        Args:
            depots_df: DataFrame containing depot information
            test_limit: Optional limit on number of pairs to process (for testing)
        """
        depot_pairs = list(itertools.combinations(depots_df.index, 2))
        
        # If test_limit is specified, take only the first n pairs
        if test_limit is not None:
            depot_pairs = depot_pairs[:test_limit]
            self.logger.info(f"Running in test mode with {test_limit} depot pairs")
        
        times_data = []

        for idx1, idx2 in depot_pairs:
            depot1 = depots_df.iloc[idx1]
            depot2 = depots_df.iloc[idx2]
            
            try:
                time = self._get_driving_time(depot1["Depot Address"], 
                                              depot2["Depot Address"])
                
                times_data.append({
                    "Depot 1 Designation": depot1["Depot Designation"],
                    "Depot 1 Address": depot1["Depot Address"],
                    "Depot 2 Designation": depot2["Depot Designation"],
                    "Depot 2 Address": depot2["Depot Address"],
                    "Driving Time": time
                })
                
                # Add a small delay to avoid hitting API rate limits
                sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error calculating time between {depot1['Depot Designation']} "
                                f"and {depot2['Depot Designation']}: {e}")

        return pd.DataFrame(times_data)

    def _get_driving_time(self, origin: str, destination: str) -> float:
        """Get driving time between two addresses using Google Maps API."""
        try:
            result = self.gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode="driving",
                #uncomment the following two lines for real-time driving times estimates
                #departure_time="now",
                #traffic_model="best_guess",
                units="metric"
            )

            if result["rows"][0]["elements"][0]["status"] == "OK":
                # Return time in minutes
                return result["rows"][0]["elements"][0]["duration"]["value"] / 60
            else:
                raise ValueError(f"Could not calculate time: {result['rows'][0]['elements'][0]['status']}")
                
        except Exception as e:
            self.logger.error(f"Error in Google Maps API call: {e}")
            raise

