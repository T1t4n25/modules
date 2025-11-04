"""
Module responsible for interacting with RabbitMQ
Made by Ahmed Adel & Zeyad Hemeda
Version: 1.0.0
"""

from rstream import Producer, Consumer, MessageContext, ConsumerOffsetSpecification, OffsetType, exceptions
from logging import Logger, getLogger
import asyncio
import os
from dotenv import load_dotenv
import asyncio
from asyncio import Queue

# Local Imports
from grpc_files import chat_pb2 # you'll later change this to your own protobuf file

# init .env when using it outside of a container
load_dotenv()

# Singleton design pattern
class RabbitMQStreams:
    _instance = None   # holds the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # create the instance the first time
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, logger: Logger):
        
        self.logger = getLogger("__main__.RabbitMQ")
        self.logger.setLevel(logger.level)
        self.logger.debug("inside rabbitmqStream init")
        # Use Docker service name when running in container, localhost otherwise
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq' if os.getenv('DOCKER_ENV') else 'localhost')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5552'))
        self.rabbitmq_username = os.getenv("RABBITMQ_USERNAME", "guest")
        self.rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
        self.producer = Producer(self.rabbitmq_host, port=self.rabbitmq_port, username=self.rabbitmq_username, password=self.rabbitmq_password)
        
        self.streams_status = {} 
    
    async def create_stream(self, room: str, retry = 10, count = 0) -> exceptions.StreamAlreadyExists | ConnectionRefusedError:
        """
        
        """
        if count >= retry:
            raise ConnectionRefusedError
        
        if room.strip() not in [None, '']:
            try:
                await self.producer.create_stream(room)
            except ConnectionRefusedError as e:
                # sleep for 5 seconds and retry
                self.logger.error(f"❌ Connection refused when creating stream '{room}': {str(e)}. Retrying in 5 seconds...")
                await asyncio.sleep(5)
                self.create_stream(room, retry, count + 1)

            
    async def _init_streams(self, channels: list):
        """Initialize streams from config file, and return the channels in a list"""
        failed = []
        if channels:
            for room in channels:
                try:
                    await self.create_stream(room)
                    self.logger.info(f"✅ Stream '{room}' created")
                    self.streams_status[room] = True
                except exceptions.StreamAlreadyExists as e:
                    self.logger.warning(f"⚠️ Stream '{room}' already exists")
                    self.streams_status[room] = True
                    
                except ConnectionRefusedError as e:
                    self.logger.error(f"❌ Failed to create '{room}' after 10 attempts, check if rabbitMQ is online and streams plugin enabled")
                    self.streams_status[room] = False
                    failed.append(room)
                except Exception as e:
                    self.logger.exception(f"❌ Error creating stream '{room}': {str(e)}")
                    self.streams_status[room] = False
                    failed.append(room)
                    
        self.logger.info(f"✅ Initialized streams: {channels}")
        self.logger.warning(f"⚠️ Failed to create streams: {failed}") if failed else None
        return channels
            
        
    async def send_to_stream(self, room: str, message: str):
        try:
            self.logger.debug(f"Sending message to stream: {room}")
            
            message = message.SerializeToString()
            await self.producer.send(
                stream=room,
                message=message,
                on_publish_confirm=None, # TODO: add a mechanism to check for message sent or not
            )
        except exceptions.StreamDoesNotExist as e:
            self.streams_status[room]
            self.logger.error(f"❌ Stream '{room}' does not exist. Re-initializing stream...")
            try:
                await self.create_stream(room, 5)
                self.logger.info(f"✅ Stream '{room}' created")
                self.streams_status[room] = True            
            except ConnectionRefusedError as e:
                self.logger.error(f"❌ Failed to create '{room}' after 5 attempts, check if rabbitMQ is online and streams plugin enabled")
            except Exception as e:
                self.logger.exception(f"❌ Error creating stream '{room}': {str(e)}")
        
        except Exception as e:
            self.logger.exception(f"❌ Error sending to stream: {str(e)}")
            raise

    async def consume_messages(self, room: str):
        consumer = None
        try:
            consumer = Consumer(self.rabbitmq_host, port=self.rabbitmq_port, username=self.rabbitmq_username, password=self.rabbitmq_password)
            messages = Queue()  # Use an asyncio.Queue for efficient message passing

            async def on_message(msg, message_context: MessageContext):
                try:
                    message = chat_pb2.ChatMessage()
                    message.ParseFromString(msg)
                    await messages.put(message)
                except Exception as e:
                    self.logger.exception(f"❌ Error parsing message: {str(e)}")

            await consumer.start()
            await consumer.subscribe(
                stream=room,
                callback=on_message,
                offset_specification=ConsumerOffsetSpecification(OffsetType.FIRST),
            )

            try:
                while True:
                    msg = await messages.get()
                    yield msg
            except asyncio.CancelledError as e:
                self.logger.error(f"Cancelled Error, user closed the connection : {str(e)}")
            except Exception as e:
                self.logger.exception(f"❌ Error in message consumption loop: {str(e)}")
                
        
        except Exception as e:
            self.logger.exception(f"❌ Error in consume_messages: {str(e)}")
            raise
        finally:
            self.logger.debug("inside consume_message finally")
            if consumer:
                try:
                    self.logger.debug("trying to close the consumer")
                    await consumer.close()
                except Exception as e:
                    self.logger.exception(f"❌ Error closing consumer: {str(e)}")
