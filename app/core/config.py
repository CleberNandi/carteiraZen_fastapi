from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False,
    settings_files=[".env", ".env.ci", ".secrets.toml", "settings.toml"],
    load_dotenv=True,
    environments=True,
    env_switcher="ENV_MODE",
    merge_enabled=True,
)

# Montar DATABASE_URL dinamicamente
DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@db:5432/{settings.POSTGRES_DB}"
