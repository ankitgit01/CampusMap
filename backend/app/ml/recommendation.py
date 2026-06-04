"""
Route recommendation engine based on user history and preferences
"""
from typing import Dict, List
from collections import Counter

class RecommendationEngine:
    """
    Recommends routes based on:
    - User navigation history
    - Frequently visited locations
    - Preferred routing modes
    """
    
    def __init__(self):
        self.recommendation_history = {}
    
    def get_recommendations(
        self,
        user_id: int,
        history: List[Dict],
        current_location: str,
        destination: str = None,
        num_recommendations: int = 3
    ) -> List[Dict]:
        """
        Generate route recommendations for a user
        
        Args:
            user_id: User ID
            history: List of navigation history objects
            current_location: Current location name
            destination: Destination (optional, for context)
            num_recommendations: Number of recommendations
        
        Returns:
            List of recommended routes with reasoning
        """
        recommendations = []

        # Find frequently visited destinations
        frequent_destinations = self._get_frequent_destinations(history)
        
        # Get preferred routing modes
        preferred_modes = self._get_preferred_modes(history)
        
        # Generate recommendations
        for i, destination in enumerate(frequent_destinations[:num_recommendations]):
            if destination != current_location:
                recommendation = {
                    "destination": destination,
                    "suggested_routing_mode": preferred_modes.get(destination, "fastest"),
                    "reasoning": "Recommended from your frequently visited locations",
                    "frequency": self._get_visit_frequency(destination, history),
                    "rank": i + 1,
                }
                recommendations.append(recommendation)
        
        return recommendations[:num_recommendations]
    
    def get_frequently_used_routes(
        self,
        user_id: int,
        history: List[Dict],
        limit: int = 5
    ) -> List[Dict]:
        """
        Get most frequently used routes by a user
        """
        route_pairs = []
        
        for entry in history:
            if entry.get('completed', False):
                route_pair = (
                    entry.get('source_location'),
                    entry.get('destination_location')
                )
                route_pairs.append(route_pair)
        
        # Count frequencies
        counter = Counter(route_pairs)
        
        routes = []
        for (source, destination), count in counter.most_common(limit):
            routes.append({
                "source": source,
                "destination": destination,
                "usage_count": count,
                "preferred_mode": self._get_most_used_mode_for_route(
                    source, destination, history
                )
            })
        
        return routes
    
    def get_similar_users(
        self,
        user_id: int,
        all_users_history: Dict,
        similarity_threshold: float = 0.6
    ) -> List[Dict]:
        """
        Find users with similar navigation patterns
        """
        user_history = all_users_history.get(user_id, [])
        user_destinations = set(h.get('destination_location') for h in user_history)
        
        similar_users = []
        
        for other_user_id, other_history in all_users_history.items():
            if other_user_id == user_id:
                continue
            
            other_destinations = set(h.get('destination_location') for h in other_history)
            
            # Calculate Jaccard similarity
            intersection = len(user_destinations & other_destinations)
            union = len(user_destinations | other_destinations)
            
            if union > 0:
                similarity = intersection / union
                
                if similarity >= similarity_threshold:
                    similar_users.append({
                        "user_id": other_user_id,
                        "similarity_score": similarity
                    })
        
        return sorted(similar_users, key=lambda x: x['similarity_score'], reverse=True)
    
    def _get_frequent_destinations(
        self,
        history: List[Dict],
        limit: int = 10
    ) -> List[str]:
        """
        Get most frequent destinations
        """
        destinations = [h.get('destination_location') for h in history if h.get('completed')]
        counter = Counter(destinations)
        return [dest for dest, count in counter.most_common(limit)]
    
    def _get_preferred_modes(self, history: List[Dict]) -> Dict[str, str]:
        """
        Get preferred routing modes for each destination
        """
        mode_preferences = {}
        
        for entry in history:
            destination = entry.get('destination_location')
            mode = entry.get('routing_mode', 'fastest')
            
            if destination not in mode_preferences:
                mode_preferences[destination] = []
            
            mode_preferences[destination].append(mode)
        
        # Convert to most common mode
        for destination in mode_preferences:
            modes = mode_preferences[destination]
            counter = Counter(modes)
            mode_preferences[destination] = counter.most_common(1)[0][0]
        
        return mode_preferences
    
    def _get_visit_frequency(self, destination: str, history: List[Dict]) -> int:
        """
        Get visit frequency for a destination
        """
        count = sum(
            1 for h in history
            if h.get('destination_location') == destination and h.get('completed')
        )
        return count
    
    def _get_most_used_mode_for_route(
        self,
        source: str,
        destination: str,
        history: List[Dict]
    ) -> str:
        """
        Get most used routing mode for a specific route
        """
        modes = [
            h.get('routing_mode', 'fastest')
            for h in history
            if h.get('source_location') == source and h.get('destination_location') == destination
        ]
        
        if not modes:
            return "fastest"
        
        counter = Counter(modes)
        return counter.most_common(1)[0][0]
