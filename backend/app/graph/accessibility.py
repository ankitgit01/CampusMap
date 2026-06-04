"""
Accessibility routing and scoring
"""
from typing import Dict, List, Optional
from app.graph.graph_builder import CampusGraph

class AccessibilityRouter:
    """
    Handles accessibility-aware routing
    """
    
    def __init__(self, graph: CampusGraph):
        self.graph = graph
    
    def calculate_accessibility_score(
        self,
        has_stairs: bool,
        has_slope: bool,
        slope_percentage: float,
        is_wheelchair_accessible: bool,
        has_ramp: bool,
        has_elevator: bool,
        width: float = None
    ) -> float:
        """
        Calculate accessibility score for a path
        """
        score = 0.5  # Base score
        
        # Negative factors
        if has_stairs:
            score -= 0.5
        
        if has_slope:
            slope_factor = min(slope_percentage / 100, 1.0)
            score -= 0.2 * slope_factor
        
        # Positive factors
        if is_wheelchair_accessible:
            score += 0.8
        
        if has_ramp:
            score += 0.5
        
        if has_elevator:
            score += 0.6
        
        if width and width >= 2.0:
            score += 0.3
        
        return max(0.0, min(1.0, score))
    
    def get_accessibility_index(
        self,
        location_id: int,
        accessibility_requirements: Dict = None
    ) -> Dict:
        """
        Calculate accessibility index for a location
        """
        location = self.graph.get_location(location_id)
        if not location:
            return {"error": "Location not found"}
        
        index = {
            "location_id": location_id,
            "location_name": location['name'],
            "overall_accessibility": location.get('accessibility_score', 0),
            "is_accessible": location.get('is_accessible', False),
            "details": {
                "wheelchair_accessible": location.get('accessibility_score', 0) > 0.7,
                "has_elevator": False,  # Would need to check from DB
                "has_ramp": False,
                "has_stairs": False,
                "ground_level_accessible": False
            }
        }
        
        return index
    
    def find_accessible_locations(
        self,
        category: str = None,
        min_accessibility_score: float = 0.6
    ) -> List[Dict]:
        """
        Find all accessible locations matching criteria
        """
        accessible_locations = []
        
        for location_id, location in self.graph.nodes.items():
            if location.get('accessibility_score', 0) >= min_accessibility_score:
                if category is None or location.get('category', '') == category:
                    accessible_locations.append({
                        "id": location_id,
                        "name": location['name'],
                        "category": location.get('category'),
                        "accessibility_score": location.get('accessibility_score', 0)
                    })
        
        return sorted(
            accessible_locations,
            key=lambda x: x['accessibility_score'],
            reverse=True
        )
    
    def get_accessibility_metrics(self) -> Dict:
        """
        Get overall campus accessibility metrics
        """
        total_locations = len(self.graph.nodes)
        total_routes = sum(len(neighbors) for neighbors in self.graph.edges.values())
        
        accessible_locations = [
            loc for loc in self.graph.nodes.values()
            if loc.get('is_accessible', False) or loc.get('accessibility_score', 0) > 0.6
        ]
        
        return {
            "total_locations": total_locations,
            "accessible_locations": len(accessible_locations),
            "accessibility_coverage": len(accessible_locations) / max(total_locations, 1),
            "total_routes": total_routes // 2,  # Avoid double counting
            "campus_accessibility_index": sum(
                loc.get('accessibility_score', 0) for loc in self.graph.nodes.values()
            ) / max(total_locations, 1)
        }
