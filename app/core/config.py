from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="APP",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["dev", "hml", "prod"],
    env_switcher="ENV_MODE",
)

settings.setdefault("ENV", "dev")  # type: ignore
settings.setdefault("PROJECT_NAME", "CarteiraZen")  # type: ignore
settings.setdefault("VERSION", "0.1.0")  # type: ignore
settings.setdefault("BASE_URL", "app")  # type: ignore
