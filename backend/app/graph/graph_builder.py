"""
Graph builder to construct campus graph from database
"""
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models import Location, Route
import heapq

class CampusGraph:
    """
    Represents the campus as a graph with locations as nodes and routes as edges
    """
    
    def __init__(self):
        self.nodes: Dict[int, dict] = {}  # location_id -> location data
        self.edges: Dict[int, List[Tuple[int, dict]]] = {}  # from_id -> [(to_id, edge_data), ...]
        self.location_names: Dict[str, int] = {}  # name -> id mapping
    
    def add_node(self, location_id: int, location_data: dict):
        """Add a node (location) to the graph"""
        self.nodes[location_id] = location_data
        self.location_names[location_data['name'].lower()] = location_id
        if location_id not in self.edges:
            self.edges[location_id] = []
    
    def add_edge(self, from_id: int, to_id: int, edge_data: dict):
        """Add a route as a two-way edge in the graph."""
        if from_id not in self.edges:
            self.edges[from_id] = []
        self.edges[from_id].append((to_id, {
            **edge_data,
            "from_id": from_id,
            "to_id": to_id,
            "is_reverse_traversal": False,
        }))
        
        if to_id not in self.edges:
            self.edges[to_id] = []
        self.edges[to_id].append((from_id, {
            **edge_data,
            "from_id": to_id,
            "to_id": from_id,
            "is_reverse_traversal": True,
        }))
    
    def get_neighbors(self, node_id: int) -> List[Tuple[int, dict]]:
        """Get neighbors of a node"""
        return self.edges.get(node_id, [])
    
    def get_location_by_name(self, name: str) -> Optional[int]:
        """Get location ID by name"""
        return self.location_names.get(name.lower())
    
    def get_location(self, location_id: int) -> Optional[dict]:
        """Get location data"""
        return self.nodes.get(location_id)
    
    def is_valid_node(self, node_id: int) -> bool:
        """Check if node exists in graph"""
        return node_id in self.nodes


class GraphBuilder:
    """
    Builds the campus graph from database
    """
    
    @staticmethod
    def build_graph(db: Session) -> CampusGraph:
        """
        Build campus graph from database locations and routes
        """
        graph = CampusGraph()
        
        # Add all locations as nodes
        locations = db.query(Location).all()
        for location in locations:
            location_data = {
                'name': location.name,
                'category': location.category,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'is_accessible': location.is_accessible,
                'accessibility_score': location.accessibility_score,
                'description': location.description
            }
            graph.add_node(location.id, location_data)
        
        # Add all routes as edges
        routes = db.query(Route).filter(Route.is_closed == False).all()
        for route in routes:
            edge_data = {
                'distance': route.distance,
                'walking_time': route.walking_time,
                'route_type': route.route_type,
                'accessibility_score': route.accessibility_score,
                'crowdedness_score': route.crowdedness_score,
                'is_blocked': route.is_blocked,
                'blocked_reason': route.blocked_reason,
                'has_stairs': route.has_stairs,
                'has_slope': route.has_slope,
                'is_wheelchair_accessible': route.is_wheelchair_accessible,
                'route_id': route.id,
                'entered_source_id': route.source_id,
                'entered_destination_id': route.destination_id,
            }
            
            if not route.is_blocked:
                graph.add_edge(route.source_id, route.destination_id, edge_data)
        
        return graph
    
    @staticmethod
    def build_graph_by_mode(db: Session, mode: str = "fastest") -> CampusGraph:
        """
        Build graph with edge weights based on routing mode
        Available modes: fastest, shortest, accessible, low_crowd
        """
        graph = GraphBuilder.build_graph(db)
        # Weights will be calculated per mode in the routing algorithms
        return graph
