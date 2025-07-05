from dynaconf import Dynaconf

config = Dynaconf(
    envvar_prefix="APP",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    env_switcher="ENV_MODE",
)
