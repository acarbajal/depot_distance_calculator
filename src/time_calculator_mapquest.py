#src/time_calculator.py
# time calculator using MapQuest 
import requests
from typing import List, Dict, Tuple
import pandas as pd
import itertools
import logging
from time import sleep
import sys
sys.path.append('..')  # Add parent directory to Python path

class TimeCalculator:
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        self.mapquest_key = api_key
        
    def calculate_times(self, depots_df: pd.DataFrame, test_limit: int = None) -> pd.DataFrame:
        """
        Calculate driving times between all pairs of depots.
        
        Args:
            depots_df: DataFrame containing depot information
            test_limit: Optional limit on number of pairs to process (for testing)
        """
        depot_pairs = list(itertools.permutations(depots_df.index, 2))
        
        if test_limit is not None:
            depot_pairs = depot_pairs[:test_limit]
            self.logger.info(f"Running in test mode with {test_limit} depot pairs")
        
        times_data = []
        
        for idx1, idx2 in depot_pairs:
            depot1 = depots_df.iloc[idx1]
            depot2 = depots_df.iloc[idx2]
            
            try:
                time = self._get_driving_time(
                    depot1["Depot Address"],
                    depot2["Depot Address"]
                )
                
                times_data.append({
                    "Depot 1 Designation": depot1["Depot Designation"],
                    "Depot 1 Address": depot1["Depot Address"],
                    "Depot 2 Designation": depot2["Depot Designation"],
                    "Depot 2 Address": depot2["Depot Address"],
                    "Driving Time (minutes)": time
                })
                
                # Add a small delay to avoid hitting API rate limits
                sleep(0.2)
                
            except Exception as e:
                self.logger.error(f"Error calculating time between {depot1['Depot Designation']} "
                                f"and {depot2['Depot Designation']}: {e}")
        
        return pd.DataFrame(times_data)
    
    def _get_driving_time(self, origin: str, destination: str) -> float:
        """Get driving time between two addresses using MapQuest Directions API."""
        try:
            url = "http://www.mapquestapi.com/directions/v2/route"
            params = {
                "key": self.mapquest_key,
                "from": origin,
                "to": destination,
                "unit": "m",  # miles
                "routeType": "fastest",
                "doReverseGeocode": False,  # Don't need reverse geocoding
                "narrativeType": "none",  # Don't need turn-by-turn directions
                "enhanced": False,  # Don't need enhanced narrative
                "fullShape": False  # Don't need the route shape
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("info", {}).get("statuscode") != 0:
                raise ValueError(f"MapQuest API error: {data['info']['messages']}")
            
            # Return time in minutes (original response is in seconds)
            return data["route"]["time"] / 60.0
            
        except Exception as e:
            self.logger.error(f"Error calculating driving time: {e}")
            raise