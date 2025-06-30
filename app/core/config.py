from dynaconf import Dynaconf

config = Dynaconf(
    envvar_prefix="APP",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["dev", "hml", "prod"],
    env_switcher="ENV_MODE",
)

config.setdefault("ENV", "dev")  # type: ignore
config.setdefault("PROJECT_NAME", "CarteiraZen")  # type: ignore
config.setdefault("VERSION", "0.1.0")  # type: ignore
config.setdefault("BASE_URL", "app")  # type: ignore
