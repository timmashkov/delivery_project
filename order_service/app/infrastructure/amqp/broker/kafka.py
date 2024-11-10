import logging
import uuid
from asyncio import (AbstractEventLoop, Future, TimeoutError, get_event_loop,
                     sleep, wait_for)
from typing import Any, Awaitable, List, NoReturn, Optional, Self, Union

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.infrastructure.base.mixin.broker_mixin import BrokerSerializeMixin


class KafkaProducer(BrokerSerializeMixin):
    def __init__(
        self,
        host: str,
        port: int,
        acks: str,
        transactional_id: Any,
        loop: Optional[AbstractEventLoop] = None,
        topics: Optional[List[str]] = None,
        logging_config: Optional[str] = None,
    ) -> NoReturn:
        self.host = host
        self.port = port
        self.loop = loop if loop else get_event_loop()
        self.topics = topics if topics else []
        self.logging_config = logging_config.upper() if logging_config else logging.INFO
        self._response_queue = {}
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=f"{host}:{port}",
            loop=self.loop,
            acks=acks,
            transactional_id=transactional_id,
        )

    async def __aenter__(self) -> Self:
        await self.__producer.begin_transaction()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            await self.__producer.commit_transaction()
            logging.info("Транзакция успешно зафиксирована")
        else:
            await self.__producer.abort_transaction()
            logging.error(f"Ошибка в транзакции: {exc_val}, транзакция откатана")

    async def _init_logger(self) -> None:
        logging.basicConfig(level=self.logging_config)
        logging.info("Инициализация logger прошла успешно")

    async def connect(self) -> None:
        await self._init_logger()
        await self.__producer.start()
        logging.info("Инициализация kafka прошла успешно")

    async def disconnect(self) -> None:
        await self._init_logger()
        await self.__producer.stop()
        logging.info("Отключение kafka прошла успешно")

    async def simple_send_message(
        self,
        message: Union[str, bytes, list, dict],
        topic: str,
    ) -> None:
        await self._init_logger()
        await self.__producer.send_and_wait(
            topic=topic,
            value=self.serialize_message(message),
        )
        logging.info("Сообщение отправлено")

    async def transactional_send_message(
        self,
        message: Union[str, bytes, list, dict],
        topic: str,
    ) -> None:
        await self._init_logger()
        try:
            async with self:
                await self.simple_send_message(
                    topic=topic,
                    message=self.serialize_message(message),
                )
                logging.info("Сообщение отправлено и транзакция зафиксирована")
        except Exception as e:
            await self.__producer.abort_transaction()
            logging.error(f"Ошибка при отправке сообщения: {e}, транзакция откатана")

    async def rpc_request(
        self, message: Union[str, bytes, dict], topic: str, timeout: float = 10.0
    ) -> Any:
        correlation_id = str(uuid.uuid4())
        rpc_message = self.serialize_message(
            {"message": message, "correlation_id": correlation_id}
        )

        future = Future()
        self._response_queue[correlation_id] = future

        await self.simple_send_message(rpc_message, topic)

        try:
            response = await wait_for(future, timeout)
            return response
        except TimeoutError:
            logging.error("RPC запрос не получил ответ в течение времени ожидания")
            return None
        finally:
            self._response_queue.pop(correlation_id, None)


class KafkaConsumer(BrokerSerializeMixin):
    def __init__(
        self,
        host: str,
        port: int,
        retry: int = 5,
        loop: Optional[AbstractEventLoop] = None,
        topics: Optional[List[str]] = None,
        logging_config: Optional[str] = None,
    ) -> NoReturn:
        self.host = host
        self.port = port
        self.retry = retry
        self.loop = loop if loop else get_event_loop()
        self.topics = topics if topics else []
        self.logging_config = logging_config.upper() if logging_config else logging.INFO
        self.__consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=f"{host}:{port}",
            loop=self.loop,
        )

    async def _init_logger(self) -> None:
        logging.basicConfig(level=self.logging_config)
        logging.info("Инициализация logger прошла успешно")

    async def connect(self) -> None:
        await self._init_logger()
        await self.__consumer.start()
        self.__consumer.subscribe(self.topics)
        logging.info("Инициализация kafka прошла успешно")

    async def disconnect(self) -> None:
        await self._init_logger()
        await self.__consumer.stop()
        logging.info("Отключение kafka прошла успешно")

    async def init_consuming(self, on_message: Union[callable, Awaitable]) -> None:
        await self._init_logger()
        async for msg in self.__consumer:
            for attempt in range(self.retry):
                try:
                    await on_message(msg)
                    await self.__consumer.commit()
                    logging.info("Сообщение получено")
                    break
                except Exception as e:
                    logging.error(
                        f"Ошибка при обработке сообщения: {e}. Попытка {attempt + 1} из {self.retry}"
                    )
                    await sleep(0.1)
            else:
                logging.error(
                    f"Не удалось обработать сообщение после {self.retry} попыток"
                )

    async def rpc_response(
        self,
        on_request: Union[callable, Awaitable],
        producer_client: KafkaProducer = None,
    ) -> None:
        async for msg in self.__consumer:
            try:
                data = self.deserialize_message(msg.value)
                correlation_id = data.get("correlation_id")
                request = data.get("message")

                if not correlation_id:
                    logging.warning("Пропущен запрос без correlation_id")
                    continue

                response = await on_request(request)
                response_data = self.serialize_message(
                    {"response": response, "correlation_id": correlation_id}
                )

                await producer_client.simple_send_message(
                    response_data, topic=msg.topic
                )

            except Exception as e:
                logging.error(f"Ошибка обработки RPC запроса: {e}")
                await sleep(0.1)
