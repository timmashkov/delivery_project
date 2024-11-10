# from app.infrastructure.amqp.broker.kafka import KafkaConsumer, KafkaProducer
from app.infrastructure.base.singleton import OnlyContainer, Singleton
from app.infrastructure.database.gateways.alchemy_gateway import AlchemyGateway
from app.infrastructure.database.gateways.clickhouse_gateway import \
    ClickHouseManager
from app.infrastructure.server.config import settings
from redis.asyncio import Redis


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

    # producer_client = OnlyContainer(
    #     KafkaProducer,
    #     host=settings.KAFKA.host,
    #     port=settings.KAFKA.port,
    #     topics=settings.KAFKA.topics,
    #     logging_config=settings.LOG_LEVEL,
    #     acks=settings.KAFKA.acks,
    #     transactional_id=settings.KAFKA.transactional_id,
    # )
    #
    # consumer_client = OnlyContainer(
    #     KafkaConsumer,
    #     host=settings.KAFKA.host,
    #     port=settings.KAFKA.port,
    #     topics=[settings.KAFKA.topics.register_topic],
    #     logging_config=settings.LOG_LEVEL,
    # )
