import logging
from asyncio import AbstractEventLoop, get_event_loop, sleep
from typing import Any, Awaitable, List, Optional, Union

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.infrastructure.base.mixin.broker_mixin import BrokerSerializeMixin


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
    ):
        self.host = host
        self.port = port
        self.loop = loop if loop else get_event_loop()
        self.topics = topics if topics else []
        self.logging_config = logging_config.upper() if logging_config else logging.INFO
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=f"{host}:{port}",
            loop=self.loop,
            acks=acks,
            transactional_id=transactional_id,
        )

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
            await self.__producer.begin_transaction()
            await self.__producer.send_and_wait(
                topic=topic,
                value=self.serialize_message(message),
            )
            await self.__producer.commit_transaction()
            logging.info("Сообщение отправлено и транзакция зафиксирована")

        except Exception as e:
            await self.__producer.abort_transaction()
            logging.error(f"Ошибка при отправке сообщения: {e}, транзакция откатана")


class KafkaConsumer(BrokerSerializeMixin):
    def __init__(
        self,
        host: str,
        port: int,
        retry: int = 5,
        loop: Optional[AbstractEventLoop] = None,
        topics: Optional[List[str]] = None,
        logging_config: Optional[str] = None,
    ):
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

    async def init_consuming(self, on_message: callable | Awaitable) -> None:
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
