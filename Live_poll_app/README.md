# Poll System (with TCP and ZeroMQ)

A simple topic-based poll system for computer networks course.

## Features
- Server holds a fixed poll.
- Clients can vote via TCP.
- Server broadcasts live results to all clients using ZeroMQ (PUB/SUB).
- No GUI, console-based interaction.

## Requirements
- Python 3.x
- pyzmq

Install dependencies:
```
pip install -r requirements.txt
```

## How to Run
1. Start the server:
   ```
   python server.py
   ```
2. Start one or more clients (in separate terminals):
   ```
   python client.py
   ```

## Project Structure
- `server.py`: The poll server (TCP + ZeroMQ PUB)
- `client.py`: The poll client (TCP + ZeroMQ SUB) 