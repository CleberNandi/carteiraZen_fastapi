# Stub básico para dynaconf

class Dynaconf:
    ENV: str
    PROJECT_NAME: str
    VERSION: str
    DATABASE_URL: str
    BASE_URL: str
    PASSWORD_SYSTEM: str
    SECRET_KEY: str
    ALGORITHM: str
    def __init__(self, *args: object, **kwargs: object) -> None: ...
