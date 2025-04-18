import socket
import threading
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Set to DEBUG mode.
DEBUG = True

def debug_print(*args):
    if DEBUG:
        print("[DEBUG]", *args)

KEY = b'This is a key123'  

def encrypt_message(message, key):
    debug_print("Original message:", message)
    
    # Generate a random IV for each message
    iv = get_random_bytes(16)
    debug_print("Generated IV (hex):", iv.hex())
    
    # Pad the plaintext message
    padded_message = pad(message.encode('utf-8'), AES.block_size)
    debug_print("Padded message (hex):", padded_message.hex())
    
    # Encrypt using AES in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct_bytes = cipher.encrypt(padded_message)
    debug_print("Ciphertext (hex):", ct_bytes.hex())
    
    # Prepend IV to ciphertext so the receiver can extract it
    encrypted_data = iv + ct_bytes
    debug_print("Final encrypted data (hex):", encrypted_data.hex())
    
    return encrypted_data

def decrypt_message(encrypted, key):
    debug_print("Received encrypted data (hex):", encrypted.hex())
    
    # Extract IV and ciphertext
    iv = encrypted[:16]
    ct = encrypted[16:]
    debug_print("Extracted IV (hex):", iv.hex())
    debug_print("Extracted ciphertext (hex):", ct.hex())
    
    # Decrypt the message
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_pt = cipher.decrypt(ct)
    debug_print("Decrypted padded plaintext (hex):", padded_pt.hex())
    
    # Unpad the plaintext
    pt = unpad(padded_pt, AES.block_size)
    debug_print("Unpadded plaintext:", pt.decode('utf-8'))
    
    return pt.decode('utf-8')

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096)
            if data:
                try:
                    message = decrypt_message(data, KEY)
                    print("\n[Received]", message)
                    print("You: ", end="", flush=True)
                except Exception as e:
                    print("\n[Error decrypting message]", e)
            else:
                print("Disconnected from server")
                break
        except Exception as e:
            print("Error receiving data:", e)
            break

def main():
    host = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
    port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print("Connected to chat server")
    thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    thread.start()
    
    try:
        while True:
            message = input("You: ")
            if message.lower() == "exit":
                break
            encrypted_message = encrypt_message(message, KEY)
            sock.send(encrypted_message)
    except KeyboardInterrupt:
        print("Exiting chat")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
