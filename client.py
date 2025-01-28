# client.py (Bob)
import socket
import pickle
from crypto_participant import CryptoParticipant

def start_client():
    print("\n" + "="*50)
    print("Starting Bob's Client")
    print("="*50)
    
    # Initialize Bob
    bob = CryptoParticipant("Bob")
    
    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("\nConnecting to Alice's server...")
    client.connect(('localhost', 5000))
    print("Connected!")

    try:
        print("\n" + "="*50)
        print("Starting Key Exchange Protocol")
        print("="*50)

        # Exchange RSA keys
        alice_public = pickle.loads(client.recv(4096))
        print(f"\nReceived Alice's RSA public key:")
        print(f"e: {alice_public['e']}")
        print(f"n: {alice_public['n']}")

        public_key = {'e': bob.e, 'n': bob.n}
        client.send(pickle.dumps(public_key))
        print("\nSent Bob's RSA public key to Alice")

        # Get DH parameters
        dh_params = pickle.loads(client.recv(4096))
        print("\nReceived DH parameters from Alice:")
        print(f"base: {dh_params['base']}")
        print(f"modulus: {dh_params['modulus']}")
        
        # Setup DH
        bob.set_dh_parameters(dh_params['base'], dh_params['modulus'])
        bob.generate_dh_private()
        bob_public_dh = bob.calculate_dh_public()

        # Exchange encrypted DH values
        print("\n" + "="*50)
        print("Exchanging Encrypted DH Values")
        print("="*50)

        alice_encrypted = pickle.loads(client.recv(4096))
        print("\nReceived Alice's encrypted DH public value")
        alice_public_dh = bob.rsa_decrypt(alice_encrypted)

        bob_encrypted = bob.rsa_encrypt(bob_public_dh, alice_public['e'], alice_public['n'])
        client.send(pickle.dumps(bob_encrypted))
        print("\nSent encrypted DH public value to Alice")

        # Calculate final keys
        print("\n" + "="*50)
        print("Calculating Final Keys")
        print("="*50)
        
        shared_secret = bob.calculate_shared_secret(alice_public_dh)
        bob_aes = bob.derive_aes_key(shared_secret)

        print("\n" + "="*50)
        print("Secure Channel Established")
        print("="*50)
        print("\nYou can now start chatting with Alice")
        print("Type 'quit' to exit\n")

        while True:
            # Get Bob's message
            message = input("\nBob: ")
            if message.lower() == 'quit':
                break

            # Encrypt and send
            encrypted_message = bob.aes_encrypt(message)
            client.send(pickle.dumps(encrypted_message))

            # Wait for Alice's response
            print("\nWaiting for Alice's response...")
            encrypted_response = pickle.loads(client.recv(4096))
            if not encrypted_response:
                break
                
            # Decrypt and show all steps
            response = bob.aes_decrypt(encrypted_response)
            print(f"\nDecrypted message from Alice: {response}")

    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        client.close()
        print("\nClient shut down")

if __name__ == "__main__":
    start_client()