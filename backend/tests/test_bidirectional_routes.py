from app.graph.dijkstra import DijkstraRouter
from app.graph.graph_builder import CampusGraph


def test_single_entered_route_can_be_used_in_reverse():
    graph = CampusGraph()
    graph.add_node(1, {"name": "A", "latitude": 0, "longitude": 0})
    graph.add_node(2, {"name": "B", "latitude": 0, "longitude": 1})
    graph.add_edge(
        2,
        1,
        {
            "route_id": 42,
            "distance": 100,
            "walking_time": 80,
            "effective_walking_time": 80,
            "is_blocked": False,
            "is_wheelchair_accessible": True,
            "accessibility_score": 1,
        },
    )

    result = DijkstraRouter(graph).find_path(1, 2, weight_key="walking_time")

    assert result["path"] == [1, 2]
    assert result["distance"] == 100
    assert result["walking_time"] == 80
    assert result["route_ids"] == [42]
