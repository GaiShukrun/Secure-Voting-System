# server.py (Alice)
import socket
import pickle
from crypto_participant import CryptoParticipant

def start_server():
    print("\n" + "="*50)
    print("Starting Alice's Server")
    print("="*50)
    
    # Initialize Alice
    alice = CryptoParticipant("Alice")
    
    # Set up server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5000))
    server.listen(1)
    print("\nWaiting for Bob to connect...")

    client_socket, address = server.accept()
    print(f"\nConnection established with Bob at {address}")

    try:
        print("\n" + "="*50)
        print("Starting Key Exchange Protocol")
        print("="*50)
        
        # Exchange RSA keys
        public_key = {'e': alice.e, 'n': alice.n}
        client_socket.send(pickle.dumps(public_key))
        print("\nSent Alice's RSA public key to Bob")

        bob_public = pickle.loads(client_socket.recv(4096))
        print(f"\nReceived Bob's RSA public key:")
        print(f"e: {bob_public['e']}")
        print(f"n: {bob_public['n']}")

        # Send DH parameters
        dh_params = {'base': 5, 'modulus': 2357}
        client_socket.send(pickle.dumps(dh_params))
        print("\nSent DH parameters to Bob")
        
        # Setup DH
        alice.set_dh_parameters(dh_params['base'], dh_params['modulus'])
        alice.generate_dh_private()
        alice_public_dh = alice.calculate_dh_public()

        # Exchange encrypted DH values
        print("\n" + "="*50)
        print("Exchanging Encrypted DH Values")
        print("="*50)
        
        alice_encrypted = alice.rsa_encrypt(alice_public_dh, bob_public['e'], bob_public['n'])
        client_socket.send(pickle.dumps(alice_encrypted))
        print("\nSent encrypted DH public value to Bob")

        bob_encrypted = pickle.loads(client_socket.recv(4096))
        print("\nReceived Bob's encrypted DH public value")
        bob_public_dh = alice.rsa_decrypt(bob_encrypted)

        # Calculate final keys
        print("\n" + "="*50)
        print("Calculating Final Keys")
        print("="*50)
        
        shared_secret = alice.calculate_shared_secret(bob_public_dh)
        alice_aes = alice.derive_aes_key(shared_secret)

        print("\n" + "="*50)
        print("Secure Channel Established")
        print("="*50)
        print("\nYou can now start chatting with Bob")
        print("Type 'quit' to exit\n")

        while True:
            # Receive from Bob
            print("\nWaiting for Bob's message...")
            encrypted_message = pickle.loads(client_socket.recv(4096))
            if not encrypted_message:
                break
                
            # Decrypt and show all steps
            message = alice.aes_decrypt(encrypted_message)
            print(f"\nDecrypted message from Bob: {message}")

            # Get Alice's response
            response = input("\nAlice: ")
            if response.lower() == 'quit':
                break

            # Encrypt and send
            encrypted_response = alice.aes_encrypt(response)
            client_socket.send(pickle.dumps(encrypted_response))

    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        client_socket.close()
        server.close()
        print("\nServer shut down")

if __name__ == "__main__":
    start_server()