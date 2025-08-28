"""Graph visualization tool for the data graph multi-agent system."""

import json
import logging
import tempfile
import os
from typing import Dict, Any, Optional
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

logger = logging.getLogger(__name__)

def visualize_graph(graph_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Visualizes a graph from structured JSON data and saves it as an image.
    
    Args:
        graph_data: A dictionary containing nodes, edges, and metadata for the graph
        output_path: Optional path to save the visualization. If not provided, a temporary file will be created.
        
    Returns:
        The path to the saved visualization image
    """
    logger.info("Visualizing graph from JSON data")
    
    # Parse the graph data
    if isinstance(graph_data, str):
        try:
            graph_data = json.loads(graph_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse graph data as JSON: {e}")
            raise ValueError(f"Invalid JSON data: {e}")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    node_types = {}
    for node in graph_data.get("nodes", []):
        node_id = node.get("id")
        node_label = node.get("label", node_id)
        node_type = node.get("type", "Unknown")
        
        G.add_node(node_id, label=node_label)
        node_types[node_id] = node_type
    
    # Add edges with attributes
    for edge in graph_data.get("edges", []):
        source = edge.get("source")
        target = edge.get("target")
        label = edge.get("label", "")
        
        if source in G.nodes and target in G.nodes:
            G.add_edge(source, target, label=label)
    
    # Create a color map for different node types
    unique_types = set(node_types.values())
    colors = plt.cm.tab10(range(len(unique_types)))
    type_to_color = {t: colors[i] for i, t in enumerate(unique_types)}
    
    node_colors = [type_to_color[node_types[node]] for node in G.nodes]
    
    # Create the visualization
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42)  # Consistent layout
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, arrows=True, arrowsize=15)
    
    # Draw node labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Draw edge labels
    edge_labels = {(u, v): G[u][v]['label'] for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Add a legend for node types
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=type_to_color[t], markersize=10, label=t)
                      for t in unique_types]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Add title with metadata summary if available
    if "metadata" in graph_data and "summary" in graph_data["metadata"]:
        plt.title(graph_data["metadata"]["summary"], fontsize=12)
    else:
        plt.title("Data Graph Visualization", fontsize=12)
    
    plt.axis('off')  # Turn off the axis
    
    # Save the visualization
    if not output_path:
        # Create a temporary file
        fd, output_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
    
    plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Graph visualization saved to {output_path}")
    return output_path
