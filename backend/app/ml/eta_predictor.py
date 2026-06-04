"""
ETA (Estimated Time of Arrival) prediction model
Uses Dijkstra, A*, crowdedness, and weather data
"""
import numpy as np
from typing import Dict, Optional, List
import warnings

warnings.filterwarnings('ignore')

class ETAPredictor:
    """
    Predicts estimated time of arrival considering:
    - Distance
    - Crowdedness
    - Weather conditions
    - Route complexity
    """
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.base_walking_speed = 1.4  # m/s
    
    def predict_eta(
        self,
        distance: float,
        crowdedness: float = 0.0,
        weather: str = "clear",
        accessibility_mode: bool = False,
        route_complexity: int = 1
    ) -> Dict:
        """
        Predict ETA for a route
        
        Args:
            distance: Route distance in meters
            crowdedness: Crowdedness score (0-1)
            weather: Weather condition
            accessibility_mode: Whether using accessible route
            route_complexity: Number of turns/complexity (1-5)
        
        Returns:
            ETA in seconds and confidence
        """
        # Calculate base time
        walking_speed = self._get_walking_speed(
            accessibility_mode,
            weather,
            crowdedness
        )
        
        base_time = distance / walking_speed
        
        # Apply adjustments
        adjustment_factors = {
            'crowdedness': self._crowdedness_factor(crowdedness),
            'weather': self._weather_factor(weather),
            'complexity': self._complexity_factor(route_complexity)
        }
        
        # Calculate total ETA
        eta = base_time
        for factor in adjustment_factors.values():
            eta *= factor
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            distance,
            crowdedness,
            weather,
            route_complexity
        )
        
        return {
            "estimated_time_seconds": eta,
            "estimated_time_minutes": eta / 60,
            "estimated_time_formatted": self._format_time(eta),
            "distance": distance,
            "average_speed": distance / eta if eta > 0 else 0,
            "crowdedness_impact": adjustment_factors['crowdedness'],
            "weather_impact": adjustment_factors['weather'],
            "confidence": confidence,
            "details": {
                "base_time": base_time,
                "adjustments": adjustment_factors
            }
        }
    
    def predict_eta_batch(
        self,
        routes: List[Dict]
    ) -> List[Dict]:
        """
        Predict ETA for multiple routes
        Each route should have: distance, crowdedness, etc.
        """
        predictions = []
        
        for route in routes:
            pred = self.predict_eta(
                distance=route.get('distance'),
                crowdedness=route.get('crowdedness', 0),
                weather=route.get('weather', 'clear'),
                accessibility_mode=route.get('accessibility_mode', False),
                route_complexity=route.get('complexity', 1)
            )
            predictions.append(pred)
        
        return predictions
    
    def _get_walking_speed(
        self,
        accessibility_mode: bool,
        weather: str,
        crowdedness: float
    ) -> float:
        """
        Calculate adjusted walking speed in m/s
        """
        speed = self.base_walking_speed
        
        # Accessibility reduces speed
        if accessibility_mode:
            speed *= 0.7
        
        # Weather impacts speed
        weather_multipliers = {
            "clear": 1.0,
            "cloudy": 0.95,
            "rainy": 0.8,
            "snow": 0.6,
            "sunny": 1.05
        }
        speed *= weather_multipliers.get(weather.lower(), 1.0)
        
        # Crowdedness reduces speed
        speed *= (1 - crowdedness * 0.4)
        
        return speed
    
    def _crowdedness_factor(self, crowdedness: float) -> float:
        """
        Factor to apply based on crowdedness
        Higher crowdedness = longer time
        """
        return 1.0 + (crowdedness * 0.5)
    
    def _weather_factor(self, weather: str) -> float:
        """
        Factor to apply based on weather
        """
        weather_factors = {
            "clear": 1.0,
            "cloudy": 1.02,
            "rainy": 1.3,
            "snow": 1.5,
            "sunny": 0.98
        }
        return weather_factors.get(weather.lower(), 1.0)
    
    def _complexity_factor(self, complexity: int) -> float:
        """
        Factor based on route complexity (turns, intersections)
        Complexity 1-5, each level adds ~5% overhead
        """
        return 1.0 + (complexity - 1) * 0.05
    
    def _calculate_confidence(
        self,
        distance: float,
        crowdedness: float,
        weather: str,
        route_complexity: int
    ) -> float:
        """
        Calculate confidence score (0-1) for the ETA
        Lower confidence when unpredictable factors are high
        """
        confidence = 0.85
        
        # Lower confidence for longer routes
        if distance > 2000:
            confidence -= 0.1
        
        # Lower confidence in crowded conditions
        confidence -= crowdedness * 0.15
        
        # Lower confidence in bad weather
        if weather.lower() in ["rainy", "snow"]:
            confidence -= 0.1
        
        # Lower confidence for complex routes
        if route_complexity > 3:
            confidence -= 0.05
        
        return max(0.0, min(1.0, confidence))
    
    def _format_time(self, seconds: float) -> str:
        """
        Format time in human readable format
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
