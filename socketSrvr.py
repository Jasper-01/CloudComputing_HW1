from socket import *
import threading
import os

port = 80
# host = gethostname()
host = 'localhost'

def srvr(client_socket):
    data = client_socket.recv(1024).decode()

    if not data:
        client_socket.close()
        return

    request_lines = data.split("\n")
    request_line = request_lines[0]

    method, path, _ = request_line.split()

    if method == "GET":
        if path == "/dynamic":
            response_body = f"<h1>Dynamic Content</h1><p>The current directory has {os.listdir()}</p>"
        else:
            file_path = f"web\\{path[1:]}.html"  # Remove the leading '/' and add '.html' to the path
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    response_body = file.read()
            elif path == "/":
                with open("web\\index.html", "r") as file:
                    response_body = file.read()
            else:
                with open("web\\error404.html", "r") as file:
                    response_body = file.read()

        response_headers = "HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: {}\n\n".format(len(response_body))

        response = response_headers + response_body
        client_socket.sendall(response.encode())

    elif method == "POST":
        content_length = int([line.split(':')[1] for line in request_lines if 'Content-Length' in line][0])
        post_data = client_socket.recv(content_length).decode()

        response_body = f"<h1>Received POST Data</h1><p>{post_data}</p>"
        response_headers = "HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: {}\n\n".format(len(response_body))

        response = response_headers + response_body
        client_socket.sendall(response.encode())
    else:
        response = "HTTP/1.1 405 Method Not Allowed\n\n<h1>405 Method Not Allowed</h1>"
        client_socket.sendall(response.encode())

    client_socket.close()


if __name__ == '__main__':
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            client_handler = threading.Thread(target=srvr, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        server_socket.close()
