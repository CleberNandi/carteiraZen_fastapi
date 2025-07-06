from dynaconf import Dynaconf

config = Dynaconf(
    envvar_prefix="APP",
    settings_files=["settings.toml", ".secrets.toml", ".env"],
    environments=True,
    env_switcher="ENV_MODE",
)

print(f"Ambiente ativo: {config.ENV}")
print(f"DATABASE_URL: {config.DATABASE_URL}")
