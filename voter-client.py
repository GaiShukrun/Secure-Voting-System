import requests
import random
import math
from aes import AES
from zkp_logic_stakeholder import GraphVerification
import hashlib
import json

class Voter:
    def __init__(self, voter_id):
        self.id = voter_id
        self.authenticated = False
        self.matched_nodes = set()
        self.matched_original_nodes = set()
        self.Voted = False 
        self.aes = AES()
        self.token = self.generate_token()

        # Create proof graph with different layout but same structure
        self.proof_graph = {
            'nodes': [
                {'id': i, 'label': str(i), 
                 'x': 200 + 120 * math.cos(-math.pi/2 + i*2*math.pi/10),
                 'y': 150 + 170 * math.sin(-math.pi/2 + i*2*math.pi/10)} 
                for i in range(1, 11)
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
    def generate_token(self):
        """Generate unique token using AES encryption"""
        # Create initial state matrix (4x4 of bytes)
        state = [[random.randint(0, 255) for _ in range(4)] for _ in range(4)]
        
        # Generate random 16-byte key
        key = [random.randint(0, 255) for _ in range(16)]
        
        # Encrypt state to create token
        encrypted_state = self.aes.encrypt(state, key)
        
        # Convert to hex string
        token = ''.join([format(b, '02x') for row in encrypted_state for b in row])
        print(f"Generated token for {self.id}: {token[:16]}...") # Print first 16 chars
        return token
    
    def attempt_verify_node(self, center_id, node_id):
        """Try to verify a single node with the center"""
        if node_id in self.matched_nodes:  # Skip if already matched
            return None
            
        try:
            response = requests.post(
                f'http://localhost:5000/verify/{center_id}/{self.id}/{node_id}',
                json={
                    'proof_graph': self.proof_graph,
                    'matched_nodes': list(self.matched_nodes),
                    'matched_original_nodes': list(self.matched_original_nodes)
                }
            )
            result = response.json()
            
            if result['isValid']:
                self.matched_nodes.add(node_id)
                self.matched_original_nodes.add(result['matchedNode'])
                if result.get('authenticated'):
                    self.authenticated = True
                    
            return result
            
        except Exception as e:
            print(f"Verification error: {e}")
            return None
    
    def attempt_authentication(self, center_id):
        """Try to authenticate by matching all nodes"""
        if self.authenticated:
            print(f"Voter {self.id} is already authenticated!")
            return True
            
        print(f"Voter {self.id} attempting authentication...")
        
        for node_id in range(1, 11):
            if node_id not in self.matched_nodes:
                result = self.attempt_verify_node(center_id, node_id)
                if result:
                    print(f"Node {node_id}: {result['message']}")
                    if self.authenticated:
                        print("Authentication successful!")
                        return True
        
        print("Failed to authenticate")
        return False

    def vote(self, center_id):
        """Cast a vote if authenticated"""
        if not self.authenticated:
            print("Must authenticate before voting")
            return False
        
        try:
            vote_choice = random.choice(['red', 'blue'])
            response = requests.post(
                f'http://localhost:5000/vote/{center_id}/{self.id}',
                json={'vote': vote_choice,
                      'token': self.token  }
            )
            result = response.json()
            if (result['success'] == False):
                print(result['message'])
            else:
                print(f"Voted {vote_choice}: {result['message']}")
            self.Voted = True
            return result['success']
            
        except Exception as e:
            print(f"Voting error: {e}")
            return False


class VotingResultVerifier:
    def __init__(self, centers, voters):
        self.centers = centers
        self.voters = voters

    def compute_total_votes_from_centers(self):
        """Aggregate votes from all centers"""
        result = 0
        total_votes = {'red': 0, 'blue': 0}
        for center_id, center in self.centers.items():
            votes = center.get('votes', [])
            for vote in votes:
                total_votes[vote] += 1
            result += len(votes)
        return result
    

    # def generate_verification_hash(self, total_votes):
    #     """Create a cryptographic hash of voting results"""
    #     # Convert votes to a deterministic, sorted JSON string
    #     votes_json = json.dumps(total_votes, sort_keys=True)
    #     return hashlib.sha256(votes_json.encode()).hexdigest()

    # def cross_center_verification(self):
    #     """Verify results across multiple centers"""
    #     # Collect votes and hashes from each center
    #     center_results = {}
    #     for center_id, center in self.centers.items():
    #         center_votes = center.get('votes', [])
    #         center_hash = hashlib.sha256(json.dumps(center_votes, sort_keys=True).encode()).hexdigest()
    #         center_results[center_id] = {
    #             'votes': center_votes,
    #             'hash': center_hash
    #         }

    #     # Compare hashes to detect inconsistencies
    #     unique_hashes = set(result['hash'] for result in center_results.values())
    #     if len(unique_hashes) > 1:
    #         raise ValueError("Inconsistent votes detected across centers")

    #     return center_results

    def verify_result(self):
        """Comprehensive verification process"""
        try:        
            # Compute total votes
            total_votes_from_centers = self.compute_total_votes_from_centers()
            total_votes_from_voters = len(self.voters)

            if int(total_votes_from_centers) == int(total_votes_from_voters):
                return {
                    'total_votes': total_votes_from_centers,
                    'verified': True
                }
            else:
                return {
                    'error': "Votes do not match",
                    'verified': False
                }
        except Exception as e:
            return {
                'error': str(e),
                'verified': False
            }


def get_centers():
    centers = {}
    for i in range(1, 4):
        try:
            response = requests.get(f'http://localhost:5000/center/{i}')
            response.raise_for_status()  # Raise an error for HTTP issues
            centers[i] = response.json()  # Add the clean JSON data to the dictionary
        except requests.exceptions.HTTPError:
            print(f"Center {i} not found.")
        except requests.RequestException as e:
            print(f"Error fetching center {i}: {e}")
    return centers

def get_voters():
    try:
        response = requests.get(f'http://localhost:5000/voters')
        response.raise_for_status()  # Raise an error for HTTP issues
        voters = response.json()
    except requests.exceptions.HTTPError:
        print(f"Voters not found.")
    return voters








def main():
    # Create 5 voters total
    # for i in range(5):
    #     print("-" * 50)
    #     voter_id = f"new_voter_{i+1}"
    #     voter = Voter(voter_id)
    #     # Randomly choose a center (1, 2, or 3)
    #     center_id = random.randint(1, 3)
    #     print(f"\nVoter {voter_id} attempting to vote at Center {center_id}")
        
    #     if voter.attempt_authentication(center_id):
    #         voter.vote(center_id)
        
        
        # if voter.attempt_authentication(2):
        #     voter.vote(2)  
        # 
 
    centers = get_centers()
    voters = get_voters()

    verifier = VotingResultVerifier(centers,voters)
    verification_result = verifier.verify_result()
    print(verification_result)
    print("-" * 50)

if __name__ == "__main__":
    main()