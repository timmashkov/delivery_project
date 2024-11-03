from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False,
    environments=True,
    settings_files=["settings.yml"],
)

db_url: str = (
    f"postgresql+{settings.POSTGRES.dialect}://{settings.POSTGRES.login}:{settings.POSTGRES.password}@"
    f"{settings.POSTGRES.host}:{settings.POSTGRES.port}/{settings.POSTGRES.database}"
)
