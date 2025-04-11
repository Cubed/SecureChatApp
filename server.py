# server.py
import socket
import threading

clients = []

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                client.close()
                if client in clients:
                    clients.remove(client)

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(4096)
            if message:
                broadcast(message, client_socket)
            else:
                # Connection closed
                client_socket.close()
                if client_socket in clients:
                    clients.remove(client_socket)
                break
        except Exception as e:
            print(f"Error handling client: {e}")
            client_socket.close()
            if client_socket in clients:
                clients.remove(client_socket)
            break

def main():
    host = "0.0.0.0"
    port = 5000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")
    
    while True:
        client_socket, addr = server.accept()
        print("New connection from", addr)
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    main()
