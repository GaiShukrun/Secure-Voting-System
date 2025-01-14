class GraphVerification:
    def __init__(self):
        # Original graph structure from your React component
        self.original_graph = {
            'nodes': [
                {'id': 1, 'label': 'A', 'x': 100, 'y': 100},
                {'id': 2, 'label': 'B', 'x': 200, 'y': 100},
                {'id': 3, 'label': 'C', 'x': 300, 'y': 100},
                {'id': 4, 'label': 'D', 'x': 100, 'y': 200},
                {'id': 5, 'label': 'E', 'x': 200, 'y': 200},
                {'id': 6, 'label': 'F', 'x': 300, 'y': 200},
                {'id': 7, 'label': 'G', 'x': 100, 'y': 300},
                {'id': 8, 'label': 'H', 'x': 200, 'y': 300},
                {'id': 9, 'label': 'I', 'x': 300, 'y': 300},
                {'id': 10, 'label': 'J', 'x': 400, 'y': 200}
            ],
            'edges': [
                {'from': 1, 'to': 2},
                {'from': 2, 'to': 3},
                {'from': 1, 'to': 4},
                {'from': 2, 'to': 5},
                {'from': 3, 'to': 6},
                {'from': 4, 'to': 7},
                {'from': 5, 'to': 8},
                {'from': 6, 'to': 9},
                {'from': 4, 'to': 5},
                {'from': 5, 'to': 6},
                {'from': 7, 'to': 8},
                {'from': 8, 'to': 9},
                {'from': 6, 'to': 10},
                {'from': 10, 'to': 3}
            ]
        }

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