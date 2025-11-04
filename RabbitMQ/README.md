# RabbitMQ Streams Module

A RabbitMQ Streams wrapper for real-time messaging with automatic recovery and protobuf support.

**Version:** 1.0.0  
**Authors:** Ahmed Adel & Zeyad Hemeda

---

## Features

- Singleton pattern for shared connections
- Auto-retry on connection failures (10 attempts)
- Automatic stream recreation on send failures
- Async message consumption with generator pattern
- Protobuf serialization support
- Docker-aware configuration

---

## Setup

```bash
pip install rstream python-dotenv protobuf
```

**.env file:**
```env
RABBITMQ_HOST=localhost      # Or 'rabbitmq' in Docker
RABBITMQ_PORT=5552          # Streams port (not 5672)
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
DOCKER_ENV=false            # Set 'true' in containers
```

**Enable RabbitMQ Streams plugin:**
```bash
rabbitmq-plugins enable rabbitmq_stream
```

---

## Usage

### Initialize

```python
from RabbitMQ.RabbitMQStreams import RabbitMQStreams
import logging

logger = logging.getLogger("__main__")
rabbitmq = RabbitMQStreams(logger)

# Create streams at startup
await rabbitmq._init_streams(["chat_room_1", "notifications"])
```

### Send Messages

```python
from grpc_files import chat_pb2

message = chat_pb2.ChatMessage(
    user_id="user123",
    content="Hello!",
    timestamp=int(time.time())
)

await rabbitmq.send_to_stream("chat_room_1", message)
```

### Consume Messages

```python
async for message in rabbitmq.consume_messages("chat_room_1"):
    print(f"{message.user_id}: {message.content}")
```

### WebSocket Example (FastAPI)

```python
@app.websocket("/ws/{room}")
async def chat(websocket: WebSocket, room: str):
    await websocket.accept()
    await rabbitmq.create_stream(room)
    
    async def consume():
        async for msg in rabbitmq.consume_messages(room):
            await websocket.send_json({
                "user_id": msg.user_id,
                "content": msg.content
            })
    
    async def produce():
        while True:
            data = await websocket.receive_json()
            message = chat_pb2.ChatMessage(**data)
            await rabbitmq.send_to_stream(room, message)
    
    await asyncio.gather(consume(), produce(), return_exceptions=True)
```

---

## Key Design Choices

**Singleton Pattern** - Shared producer/consumer across app, centralized stream status tracking

**RabbitMQ Streams vs Queues** - Persistent messages, multiple consumers, offset control, replay capability

**Retry Logic** - 10 attempts with 5s delay handles transient network issues

**asyncio.Queue** - Non-blocking message buffering between parsing and consumption

**Auto-Recovery** - Catches `StreamDoesNotExist`, recreates stream (5 attempts), prevents message loss

---

## Protobuf Setup

**Define messages** (`grpc_files/chat.proto`):
```protobuf
syntax = "proto3";

message ChatMessage {
    string user_id = 1;
    string content = 2;
    int64 timestamp = 3;
}
```

**Generate Python:**
```bash
python -m grpc_tools.protoc -I. --python_out=. grpc_files/chat.proto
```

---

## Docker Deployment

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5552:5552"   # Streams
      - "15672:15672" # Management UI
    command: >
      bash -c "rabbitmq-plugins enable rabbitmq_stream &&
               rabbitmq-server"

  app:
    environment:
      RABBITMQ_HOST: rabbitmq
      DOCKER_ENV: true
    depends_on:
      - rabbitmq
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check RabbitMQ running, streams plugin enabled, port 5552 (not 5672) |
| Stream doesn't exist | Auto-recovery built-in, check `streams_status` dict |
| Messages not consuming | Verify offset spec, check RabbitMQ UI for messages |

---

## Best Practices

1. Initialize streams at startup with `_init_streams()`
2. Check `streams_status` before critical operations
3. Use try/finally for consumer cleanup
4. Set `DOCKER_ENV` correctly for host resolution
5. Enable streams plugin (not default)

---

## Authors

- **Ahmed Adel** - [@ahmeda335](https://github.com/ahmeda335)
- **Zeyad Hemeda** - [@T1t4n25](https://github.com/T1t4n25)
