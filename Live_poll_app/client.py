import socket
import zmq
import threading
import json

TCP_HOST = '127.0.0.1'
TCP_PORT = 5000
ZMQ_SUB_PORT = 5555


def listen_live_results():
    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect(f"tcp://{TCP_HOST}:{ZMQ_SUB_PORT}")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    print("[CLIENT] Listening for live poll results...")
    while True:
        msg = sub_socket.recv_string()
        data = json.loads(msg)
        print("\n--- Live Poll Results ---")
        print(data["question"])
        for opt, count in data["results"].items():
            print(f"{opt}: {count}")
        print("------------------------\n")


def vote():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TCP_HOST, TCP_PORT))
        # Username prompt
        data = s.recv(1024)
        print(data.decode(), end="")
        username = input()
        s.sendall(username.encode())
        while True:
            data = s.recv(1024)
            if not data:
                break
            print(data.decode(), end="")
            if b"Enter your choice" in data:
                choice = input()
                s.sendall(choice.encode())
                # Print server response
                resp = s.recv(1024)
                print(resp.decode())
                break

if __name__ == "__main__":
    # Start live results listener in a separate thread
    threading.Thread(target=listen_live_results, daemon=True).start()
    # Vote via TCP
    vote()
    print("[CLIENT] You can keep this window open to see live results.")
    try:
        while True:
            pass  # Keep main thread alive
    except KeyboardInterrupt:
        print("\n[CLIENT] Exiting.") 