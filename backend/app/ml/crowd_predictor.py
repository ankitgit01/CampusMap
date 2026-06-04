"""
Crowd prediction model using XGBoost and Random Forest
"""
import joblib
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

class CrowdPredictor:
    """
    Predicts crowdedness levels on routes based on explicit events and weather.
    Uses ensemble methods (XGBoost, Random Forest)
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        self.is_trained = False
        
        # Try to load pre-trained model
        if model_path:
            try:
                self.model = joblib.load(model_path)
                self.is_trained = True
            except:
                self.is_trained = False
    
    def predict_crowdedness(
        self,
        route_id: int,
        has_event: bool = False,
        event_type: str = None,
        weather: str = "clear"
    ) -> Dict:
        """
        Predict crowdedness for a specific route without time-of-day signals.
        
        Returns crowdedness score (0-1)
        """
        features = {}
        features['route_id'] = route_id
        features['has_event'] = int(has_event)
        features['weather'] = self._encode_weather(weather)
        features['event_type'] = self._encode_event_type(event_type)
        
        # If model is trained, use it
        if self.is_trained and self.model:
            feature_array = self._format_features(features)
            prediction = self.model.predict(feature_array)[0]
            crowdedness = float(prediction)
        else:
            # Fallback to heuristic prediction
            crowdedness = self._heuristic_predict(features)
        
        # Ensure crowdedness is between 0 and 1
        crowdedness = max(0.0, min(1.0, crowdedness))
        
        return {
            "route_id": route_id,
            "predicted_crowdedness": crowdedness,
            "crowdedness_level": self._get_crowdedness_level(crowdedness),
            "confidence": 0.7 if self.is_trained else 0.5
        }
    
    def predict_batch(
        self,
        routes: List[int],
        has_events: List[bool] = None
    ) -> List[Dict]:
        """
        Predict crowdedness for multiple routes
        """
        predictions = []
        
        if has_events is None:
            has_events = [False] * len(routes)
        
        for route_id, has_event in zip(routes, has_events):
            pred = self.predict_crowdedness(route_id, has_event)
            predictions.append(pred)
        
        return predictions
    
    def _heuristic_predict(self, features: Dict) -> float:
        """
        Heuristic-based crowdedness prediction
        Used when ML model is not trained
        """
        score = 0.2  # Base crowdedness
        
        # Increase for events
        if features['has_event']:
            score += 0.3
        
        # Weather effect
        if features['weather'] == 1:  # Rainy
            score -= 0.15
        
        return score
    
    def _get_crowdedness_level(self, score: float) -> str:
        """
        Convert crowdedness score to level
        """
        if score < 0.2:
            return "very_low"
        elif score < 0.4:
            return "low"
        elif score < 0.6:
            return "medium"
        elif score < 0.8:
            return "high"
        else:
            return "very_high"
    
    def _encode_weather(self, weather: str) -> int:
        """
        Encode weather condition
        """
        weather_map = {
            "clear": 0,
            "cloudy": 0,
            "rainy": 1,
            "sunny": 0
        }
        return weather_map.get(weather.lower(), 0)
    
    def _encode_event_type(self, event_type: Optional[str]) -> int:
        """
        Encode event type
        """
        if event_type:
            return 1
        return 0
    
    def _format_features(self, features: Dict) -> np.ndarray:
        """
        Format features for model input
        """
        feature_order = [
            'route_id', 'has_event', 'weather'
        ]
        
        values = [features.get(key, 0) for key in feature_order]
        return np.array(values).reshape(1, -1)
    
    def train_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        model_type: str = "xgboost"
    ) -> Dict:
        """
        Train a new crowdedness prediction model
        
        X_train: Feature array
        y_train: Target crowdedness scores
        model_type: 'xgboost' or 'random_forest'
        """
        try:
            if model_type == "xgboost":
                from xgboost import XGBRegressor
                self.model = XGBRegressor(
                    max_depth=5,
                    learning_rate=0.1,
                    n_estimators=100,
                    random_state=42
                )
            else:
                from sklearn.ensemble import RandomForestRegressor
                self.model = RandomForestRegressor(
                    max_depth=10,
                    n_estimators=100,
                    random_state=42
                )
            
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            return {
                "status": "success",
                "model_type": model_type,
                "message": "Model trained successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
