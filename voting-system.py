
from flask import Flask, request, jsonify
from pymongo import MongoClient
from zkp_logic import GraphVerification
from aes import AES
from datetime import datetime
from bson.json_util import dumps

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://GaiS:.gCa#6#zmQHC8nn@atlascluster.2oykxnx.mongodb.net/")
db = client['voting_system']




class VotingCenter:
    def __init__(self, id):
        self.id = id
        self.verifier = GraphVerification()
        self.authenticated_voters = set()
        self.load_existing_voters()
        self.aes = AES() 
    
    def load_existing_voters(self):
        # Load the 10 voters that already voted from MongoDB
        voters = db.voters.find({'voted_center': self.id})
        for voter in voters:
            self.authenticated_voters.add(voter['voter_id'])
    
    def verify_voter(self, voter_id, selected_node, proof_graph, matched_nodes, matched_original_nodes):
        """Verify a voter using graph isomorphism"""
        result = self.verifier.verify_node(
            selected_node,
            proof_graph,
            matched_nodes,
            matched_original_nodes
        )
        
        # If voter reaches 90% success rate, authenticate them
        if result['successRate'] >= 90:
            self.authenticated_voters.add(voter_id)
            result['authenticated'] = True
            
        return result

    def verify_token(self, token):
        """Check if token exists in tokens collection"""
        try:
            # Check if token exists in tokens collection
            existing_token = db.tokens.find_one({"token": token})
            return existing_token is None  # Return True if token not found (valid)
        except Exception as e:
            print(f"Token verification error: {e}")
            return False
    
    def accept_vote(self, voter_id, vote, token):
        """Accept a vote from an authenticated voter"""
        if voter_id not in self.authenticated_voters:
            return False, "Voter not authenticated"
            
        # Check if token has been used
        if not self.verify_token(token):
            return False, "Token already used"
            
        try:
            # Add token to tokens collection
            db.tokens.insert_one({
                "token": token,
                "voter_id": voter_id,
                "center_id": self.id,
                "timestamp": datetime.now()
            })
            
            # Add vote to center's votes array
            center = db.centers.find_one({"center_id": self.id})
            next_index = len(center.get('votes', []))
            
            # Update votes array using positional operator
            db.centers.update_one(
                {"center_id": self.id},
                {"$set": {
                    f"votes.{next_index}": vote  # Just store the vote value directly
                }}
            )
            
            return True, "Vote accepted"
            
        except Exception as e:
            print(f"Error storing vote: {e}")
            return False, "Error processing vote"

    def get_votes(self):
        """Retrieve votes for this center"""
        center = db.centers.find_one({"center_id": self.id})
        return center.get('votes', [])


# Create centers
centers = {i: VotingCenter(i) for i in range(1, 4)}

@app.route('/verify/<int:center_id>/<voter_id>/<int:node_id>', methods=['POST'])
def verify_voter(center_id, voter_id, node_id):
    try:
        data = request.json
        center = centers[center_id]
        result = center.verify_voter(
            voter_id,
            node_id,
            data['proof_graph'],
            set(data['matched_nodes']),
            set(data['matched_original_nodes'])
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'isValid': False,
            'message': str(e),
            'successRate': 0
        })

@app.route('/vote/<int:center_id>/<voter_id>', methods=['POST'])
def vote(center_id, voter_id):
    try:
        data = request.json
        center = centers[center_id]
        success, message = center.accept_vote(voter_id, data['vote'], data['token'])
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    


@app.route('/center/<i>', methods=['GET'])
def get_center(i):
    try:
        i = int(i)
        center = db.centers.find_one({"center_id": i}, {"_id": 0})
        print(center)
        if not center:
            return {"error": f"Center {i} not found"}, 404
        return center
    except ValueError:
        return {"error": "Invalid center ID"}, 400
    
@app.route('/voters', methods=['GET'])
def get_voters():
    try:
        voters = list(db.voters.find({}, {"_id": 0}))
        if not voters:
            print("No voters found")
        return voters
    except ValueError:
        return {"error": "Invalid "}, 400



if __name__ == '__main__':
    app.run(port=5000)