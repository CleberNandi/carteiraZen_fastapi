from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="ZNY",
    settings_files=[".env", ".secrets.toml", "settings.toml"],
    load_dotenv=True,
    environments=True,
    env_switcher="ENV_MODE",
)

print(f"Ambiente ativo: {settings.ENV}")
print(f"DATABASE_URL: {settings.DATABASE_URL}")