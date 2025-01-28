
from flask import Flask, request, jsonify
from pymongo import MongoClient
from zkp_logic import GraphVerification
from aes import AES
from datetime import datetime
from bson.json_util import dumps
from crypto_participant import CryptoParticipant

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://vladik753:G8JOVgSLas5m48yp@myshop.uhaqamv.mongodb.net/")
db = client['voting_system']




class VotingCenter:
    def __init__(self, id):
        self.id = id
        self.verifier = GraphVerification()
        self.authenticated_voters = set()
        self.load_existing_voters()
        self.aes = AES() 

        self.crypto = CryptoParticipant(f"Center_{id}")
        self.dh_base = 2  # Generator (g)
        self.dh_modulus = self.crypto._generate_prime(1000, 10000)  # Prime (p)
        self.crypto.set_dh_parameters(self.dh_base, self.dh_modulus)
        self.aes_keys = {}  # Store AES keys per voter

    
    def handle_dh_exchange(self, voter_id, client_public):
        """Process DH key exchange and derive AES key."""
        self.crypto.generate_dh_private()
        server_public = self.crypto.calculate_dh_public()
        shared_secret = self.crypto.calculate_shared_secret(client_public)
        aes_key = self.crypto.derive_aes_key(shared_secret)
        self.aes_keys[voter_id] = aes_key
        return server_public
    
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
    
    def accept_vote(self, voter_id, encrypted_vote_hex, token):
        """Decrypt and store the vote."""
        if voter_id not in self.authenticated_voters:
            return False, "Voter not authenticated"
        
        if not self.verify_token(token):
            return False, "Token already used"
        
        aes_key = self.aes_keys.get(voter_id)
        if not aes_key:
            return False, "AES key not found"
        
        try:
            encrypted_vote = bytes.fromhex(encrypted_vote_hex)
            # Temporarily set AES key for decryption
            original_key = self.crypto.aes_key
            self.crypto.aes_key = aes_key
            decrypted_vote = self.crypto.aes_decrypt(encrypted_vote)
            self.crypto.aes_key = original_key  # Restore original key
            
            db.tokens.insert_one({
                "token": token,
                "voter_id": voter_id,
                "center_id": self.id,
                "timestamp": datetime.now()
            })

            # Store the decrypted vote
            db.centers.update_one(
                {"center_id": self.id},
                {"$push": {"votes": decrypted_vote}}
            )
            return True, "Vote accepted"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_votes(self):
        """Retrieve votes for this center"""
        center = db.centers.find_one({"center_id": self.id})
        return center.get('votes', [])




@app.route('/dh_params/<int:center_id>', methods=['GET'])
def get_dh_params(center_id):
    center = centers[center_id]
    return jsonify({
        'base': center.dh_base,
        'modulus': center.dh_modulus
    })

@app.route('/dh_exchange/<int:center_id>/<voter_id>', methods=['POST'])
def dh_exchange(center_id, voter_id):
    data = request.json
    client_public = data['public_key']
    center = centers[center_id]
    server_public = center.handle_dh_exchange(voter_id, client_public)
    return jsonify({'server_public': server_public})


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
        if not center:
            return {"error": f"Center {i} not found"}, 404
        return center
    except ValueError:
        return {"error": "Invalid center ID"}, 400
    
@app.route('/voters', methods=['GET'])
def get_voters():
    try:
        voters = list(db.tokens.find({}, {"_id": 0}))
        if not voters:
            print("No voters found")
        return voters
    except ValueError:
        return {"error": "Invalid "}, 400



if __name__ == '__main__':
    app.run(port=5000)