from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="ZNY",
    settings_files=[".env", ".env.ci", ".secrets.toml", "settings.toml"],
    load_dotenv=True,
    environments=True,
    env_switcher="ENV_MODE",
)

DATABASE_URL = settings.DATABASE_URL
