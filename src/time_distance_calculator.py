#src/time_calculator.py
#Consolidated code for calculating driving times and distances between pairs of depots using MapQuest or Google Maps APIs.
import requests
from typing import List, Dict, Tuple
import googlemaps
import pandas as pd
import itertools
import logging
from time import sleep
import sys
sys.path.append('..')  # Add parent directory to Python path



class TimeDistanceCalculator:
    def __init__(self, api_key: str, provider: str):
        """
        Initialize TimeDistanceCalculator with an API key and provider.
        
        Args:
            api_key: API key for the selected provider.
            provider: Either "mapquest" or "google".
        """
        self.logger = logging.getLogger(__name__)
        self.provider = provider.lower()
        
        if self.provider == "mapquest":
            self.mapquest_key = api_key
        elif self.provider == "google":
            self.gmaps = googlemaps.Client(key=api_key)
        else:
            raise ValueError("Unsupported provider. Choose 'mapquest' or 'google'.")
    
    def calculate_times_and_distances(self, depots_df: pd.DataFrame, test_limit: int = None) -> pd.DataFrame:
        """
        Calculate driving times and distances between all pairs of depots.
        
        Args:
            depots_df: DataFrame containing depot information.
            test_limit: Optional limit on number of pairs to process (for testing).
            
        Returns:
            DataFrame with driving times and distances between depot pairs.
        """
        depot_pairs = list(itertools.permutations(depots_df.index, 2))
        
        if test_limit is not None:
            depot_pairs = depot_pairs[:test_limit]
            self.logger.info(f"Running in test mode with {test_limit} depot pairs")
        
        times_distances_data = []
        
        for idx1, idx2 in depot_pairs:
            depot1 = depots_df.iloc[idx1]
            depot2 = depots_df.iloc[idx2]
            
            try:
                time, distance = self._get_driving_info(depot1["Depot Address"], 
                                                       depot2["Depot Address"])
                
                times_distances_data.append({
                    "Depot 1 Designation": depot1["Depot Designation"],
                    "Depot 1 Address": depot1["Depot Address"],
                    "Depot 2 Designation": depot2["Depot Designation"],
                    "Depot 2 Address": depot2["Depot Address"],
                    "Driving Time (minutes)": time,
                    "Driving Distance (miles)": distance
                })
                
                sleep(0.2)  # Delay to avoid hitting API rate limits
                
            except Exception as e:
                self.logger.error(f"Error calculating time and distance info between {depot1['Depot Designation']} and {depot2['Depot Designation']}: {e}")
        
        return pd.DataFrame(times_distances_data)
    
    # For backward compatibility
    def calculate_times(self, depots_df: pd.DataFrame, test_limit: int = None) -> pd.DataFrame:
        """
        Legacy method for calculating only driving times.
        
        Args:
            depots_df: DataFrame containing depot information.
            test_limit: Optional limit on number of pairs to process (for testing).
        """
        self.logger.warning("calculate_times is deprecated, use calculate_times_and_distances instead")
        df = self.calculate_times_and_distances(depots_df, test_limit)
        return df.drop(columns=["Driving Distance (miles)"])
    
    def _get_driving_info(self, origin: str, destination: str) -> Tuple[float, float]:
        """Get driving time and distance between two addresses using the selected provider."""
        if self.provider == "mapquest":
            return self._get_driving_info_mapquest(origin, destination)
        elif self.provider == "google":
            return self._get_driving_info_google(origin, destination)
        
    def _get_driving_info_mapquest(self, origin: str, destination: str) -> Tuple[float, float]:
        """Get driving time and distance using MapQuest API."""
        try:
            url = "http://www.mapquestapi.com/directions/v2/route"
            params = {
                "key": self.mapquest_key,
                "from": origin,
                "to": destination,
                "unit": "m", #miles
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
            
            # Return time in minutes and distance in miles
            time_minutes = data["route"]["time"] / 60.0
            distance_miles = data["route"]["distance"]
            
            return time_minutes, distance_miles
        
        except Exception as e:
            self.logger.error(f"Error calculating driving info (MapQuest): {e}")
            raise
    
    def _get_driving_info_google(self, origin: str, destination: str) -> Tuple[float, float]:
        """Get driving time and distance using Google Maps API."""
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
                # Return time in minutes and distance in miles
                time_minutes = result["rows"][0]["elements"][0]["duration"]["value"] / 60
                distance_miles = result["rows"][0]["elements"][0]["distance"]["value"] / 1609.34 # transform to miles
                
                return time_minutes, distance_miles
            else:
                raise ValueError(f"Could not calculate route info: {result['rows'][0]['elements'][0]['status']}")
        
        except Exception as e:
            self.logger.error(f"Error in Google Maps API call: {e}")
            raise