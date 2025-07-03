import socket
import threading
import zmq
import json
import time

# Fixed poll
POLL_QUESTION = "En sevdiğin kedi türü hangisidir?"
POLL_OPTIONS = ["Jaguar", "Leopar", "Aslan", "Kaplan"]
results = {option: 0 for option in POLL_OPTIONS}
user_votes = {}  # username -> option

TCP_HOST = '127.0.0.1'
TCP_PORT = 5000
ZMQ_PUB_PORT = 5555
LOG_FILE = "poll_log.txt"

# ZeroMQ context and publisher
context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(f"tcp://*:{ZMQ_PUB_PORT}")

def broadcast_results():
    message = json.dumps({"question": POLL_QUESTION, "results": results})
    pub_socket.send_string(message)

def log_vote(username, option, event_type):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {username} voted for {option} ({event_type})\n")

def print_analytics():
    total_votes = sum(results.values())
    unique_users = len(user_votes)
    print("\n[ANALYTICS]")
    print(f"Total votes: {total_votes}")
    print(f"Different users: {unique_users}")
    for opt in POLL_OPTIONS:
        print(f"  {opt}: {results[opt]}")
    print("----------------------\n")

def handle_client(conn, addr):
    try:
        conn.sendall(b"Enter your username: ")
        username = conn.recv(1024).decode().strip()
        if not username:
            conn.sendall(b"Invalid username. Connection closed.\n")
            conn.close()
            return
        # Show poll
        conn.sendall(POLL_QUESTION.encode() + b'\n')
        for idx, opt in enumerate(POLL_OPTIONS):
            conn.sendall(f"{idx+1}. {opt}\n".encode())
        # Show previous vote if exists
        if username in user_votes:
            prev = user_votes[username]
            conn.sendall(f"You have already voted for: {prev}. You can change your vote.\n".encode())
        conn.sendall(b"Enter your choice (number): ")
        data = conn.recv(1024)
        if not data:
            conn.close()
            return
        try:
            choice = int(data.decode().strip())
            if 1 <= choice <= len(POLL_OPTIONS):
                selected = POLL_OPTIONS[choice-1]
                event_type = "first_vote"
                # If user has already voted, remove previous vote
                if username in user_votes:
                    prev = user_votes[username]
                    results[prev] -= 1
                    event_type = "change_vote"
                user_votes[username] = selected
                results[selected] += 1
                log_vote(username, selected, event_type)
                print_analytics()
                conn.sendall(f"Thank you, {username}! Your vote for {selected} has been recorded.\n".encode())
                broadcast_results()
            else:
                conn.sendall(b"Invalid choice.\n")
        except ValueError:
            conn.sendall(b"Invalid input.\n")
    finally:
        conn.close()

def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((TCP_HOST, TCP_PORT))
        s.listen()
        print(f"[SERVER] Listening for votes on {TCP_HOST}:{TCP_PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    print(f"[SERVER] Poll: {POLL_QUESTION}")
    print("Options:")
    for idx, opt in enumerate(POLL_OPTIONS):
        print(f"  {idx+1}. {opt}")
    print_analytics()
    threading.Thread(target=tcp_server, daemon=True).start()
    print(f"[SERVER] Broadcasting live results on ZeroMQ port {ZMQ_PUB_PORT}")
    try:
        while True:
            pass  # Keep main thread alive
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
        pub_socket.close()
        context.term() 