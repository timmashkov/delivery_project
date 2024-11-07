from redis.asyncio import Redis

from src.application.service.auth import AuthHandler
from src.infrastructure.amqp.broker.kafka import KafkaProducer, KafkaConsumer
from src.infrastructure.base.singleton import Singleton, OnlyContainer
from src.infrastructure.database.gateways.alchemy_gateway import AlchemyGateway
from src.infrastructure.database.gateways.clickhouse_gateway import ClickHouseManager
from src.infrastructure.repositories.user_repository import ReadRepository, WriteRepository
from src.infrastructure.server.config import settings


class Provider(Singleton):

    redis = OnlyContainer(
        Redis,
        **settings.REDIS,
        decode_responses=True,
    )

    alchemy_manager = OnlyContainer(
        AlchemyGateway,
        dialect=settings.POSTGRES.dialect,
        host=settings.POSTGRES.host,
        login=settings.POSTGRES.login,
        password=settings.POSTGRES.password,
        port=settings.POSTGRES.port,
        database=settings.POSTGRES.database,
        echo=settings.POSTGRES.echo,
    )

    clickhouse_manager = OnlyContainer(
        ClickHouseManager,
        host=settings.CLICKHOUSE.host,
        user=settings.CLICKHOUSE.user,
        password=settings.CLICKHOUSE.password,
        port=settings.CLICKHOUSE.port,
        database=settings.CLICKHOUSE.database,
    )

    auth_handler = OnlyContainer(
        AuthHandler,
        secret=settings.AUTH.secret,
        exp=settings.AUTH.expiration,
        api_x_key_header=settings.AUTH.api_x_key_header,
        iterations=settings.AUTH.iterations,
        hash_name=settings.AUTH.hash_name,
        formats=settings.AUTH.formats,
        algorythm=settings.AUTH.algorythm,
        redis_client=redis(),
    )

    producer_client = OnlyContainer(
        KafkaProducer,
        host=settings.KAFKA.host,
        port=settings.KAFKA.port,
        topics=settings.KAFKA.topics,
        logging_config=settings.LOG_LEVEL,
        acks=settings.KAFKA.acks,
        transactional_id=settings.KAFKA.transactional_id,
    )

    consumer_client = OnlyContainer(
        KafkaConsumer,
        host=settings.KAFKA.host,
        port=settings.KAFKA.port,
        topics=[settings.KAFKA.topics.register_topic],
        logging_config=settings.LOG_LEVEL,
    )

    user_read_registry = OnlyContainer(
        ReadRepository,
        session_manager=alchemy_manager(),
    )

    user_write_registry = OnlyContainer(
        WriteRepository,
        session_manager=alchemy_manager(),
    )
