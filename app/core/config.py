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
settings.DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@db:5432/{settings.POSTGRES_DB}"


def mask_db_url(url: str) -> str:
    """Remove senha da URL para exibir no log."""
    if "@" in url and "://" in url:
        prefix, rest = url.split("://", 1)
        if "@" in rest and ":" in rest.split("@")[0]:
            user, rest_after_user = rest.split("@", 1)
            user_no_pass = user.split(":")[0]
            return f"{prefix}://{user_no_pass}:***@{rest_after_user}"
    return url


print(f"🔹 DATABASE_URL database: {mask_db_url(settings.DATABASE_URL)}")
