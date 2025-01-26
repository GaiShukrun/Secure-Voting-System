import random
import math

class DynamicGraphVerification:
    def __init__(self, num_nodes=10, connectivity_ratio=0.4):
        """
        Generate a random graph with consistent structural properties
        
        :param num_nodes: Number of nodes in graph
        :param connectivity_ratio: Proportion of possible edges to include
        """
        self.original_graph = self.generate_graph(num_nodes, connectivity_ratio)
    
    def generate_graph(self, num_nodes, connectivity_ratio):
        """Generate a structurally consistent random graph"""
        # Create nodes with coordinates in a circle
        nodes = [
            {
                'id': i+1, 
                'label': chr(65 + i),  # A, B, C...
                'x': 200 + 120 * math.cos(-math.pi/2 + i*2*math.pi/num_nodes),
                'y': 150 + 170 * math.sin(-math.pi/2 + i*2*math.pi/num_nodes)
            } 
            for i in range(num_nodes)
        ]
        
        # Generate edges with controlled randomness
        edges = []
        possible_edges = [
            {'from': i+1, 'to': j+1} 
            for i in range(num_nodes) 
            for j in range(num_nodes) 
            if i != j
        ]
        
        # Ensure graph is connected
        for i in range(1, num_nodes):
            edges.append({'from': i, 'to': i+1})
        
        # Add additional random edges based on connectivity ratio
        additional_edges = random.sample(
            [edge for edge in possible_edges if edge not in edges], 
            k=int(len(possible_edges) * connectivity_ratio)
        )
        edges.extend(additional_edges)
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def verify_graph_properties(self):
        """Verify graph maintains key structural properties"""
        nodes = self.original_graph['nodes']
        edges = self.original_graph['edges']
        
        # Check node count
        assert len(nodes) > 5, "Graph must have sufficient nodes"
        
        # Check edge connectivity
        node_connections = {node['id']: 0 for node in nodes}
        for edge in edges:
            node_connections[edge['from']] += 1
            node_connections[edge['to']] += 1
        
        # Ensure most nodes have multiple connections
        connected_nodes = sum(1 for connections in node_connections.values() if connections > 1)
        assert connected_nodes > len(nodes) * 0.7, "Graph lacks sufficient connectivity"
        
        return True

    # Usage in voting system
    def create_voting_graphs(num_centers):
        """Create unique graphs for each voting center"""
        return {
            center_id: DynamicGraphVerification() 
            for center_id in range(1, num_centers + 1)
        }

    # Integration with existing verification
    def verify_center_graphs(center_graphs):
        """Verify graphs for all centers"""
        verification_results = {}
        for center_id, graph_verifier in center_graphs.items():
            try:
                verification_results[center_id] = graph_verifier.verify_graph_properties()
            except AssertionError as e:
                verification_results[center_id] = False
                print(f"Center {center_id} graph verification failed: {e}")
        
        return verification_results

    def get_adjacent_nodes(self, node_id, edges):
        """Get adjacent nodes for a given node"""
        adjacent_nodes = set()
        for edge in edges:
            if edge['from'] == node_id:
                adjacent_nodes.add(edge['to'])
            if edge['to'] == node_id:
                adjacent_nodes.add(edge['from'])
        return list(adjacent_nodes)

    def calculate_degree(self, node_id, edges):
        """Calculate degree of a node"""
        return len([edge for edge in edges 
                   if edge['from'] == node_id or edge['to'] == node_id])

    def check_adjacency_match(self, selected_node, matching_node, proof_graph, 
                            matched_nodes, matched_original_nodes):
        """Check if adjacency patterns match between original and proof graphs"""
        proof_adjacent = self.get_adjacent_nodes(selected_node, proof_graph['edges'])
        original_adjacent = self.get_adjacent_nodes(matching_node, self.original_graph['edges'])
        
        # Create mapping between matched nodes
        node_mapping = {}
        matched_nodes_list = list(matched_nodes)
        matched_original_list = list(matched_original_nodes)
        
        for i in range(len(matched_nodes_list)):
            node_mapping[matched_nodes_list[i]] = matched_original_list[i]
        
        # Check if already matched adjacent nodes have corresponding matches
        for proof_adj in proof_adjacent:
            if proof_adj in matched_nodes:
                original_matched_adj = node_mapping[proof_adj]
                if original_matched_adj not in original_adjacent:
                    return False
        return True

    def verify_node(self, selected_node, proof_graph, matched_nodes, matched_original_nodes):
        """Verify if a selected node matches with the original graph"""
        selected_degree = self.calculate_degree(selected_node, proof_graph['edges'])
        
        # Find matching nodes with same degree that haven't been matched yet
        potential_matches = [
            node for node in self.original_graph['nodes']
            if (self.calculate_degree(node['id'], self.original_graph['edges']) == selected_degree
                and node['id'] not in matched_original_nodes)
        ]

        if not potential_matches:
            return {
                'isValid': False,
                'message': 'No matching node found with the same degree',
                'successRate': len(matched_original_nodes) * 10
            }

        # Find a matching node that satisfies adjacency requirements
        matching_node = next(
            (node for node in potential_matches 
             if self.check_adjacency_match(
                 selected_node, node['id'], proof_graph, 
                 matched_nodes, matched_original_nodes)),
            None
        )

        if not matching_node:
            return {
                'isValid': False,
                'message': 'No matching node found with compatible adjacency pattern',
                'successRate': len(matched_original_nodes) * 10
            }

        new_success_rate = (len(matched_original_nodes) + 1) * 10
        remaining_nodes = len(self.original_graph['nodes']) - (len(matched_original_nodes) + 1)

        return {
            'isValid': True,
            'message': f"Match found! Progress: {new_success_rate}%",
            'matchedNode': matching_node['id'],
            'successRate': new_success_rate,
            'remainingNodes': remaining_nodes
        }