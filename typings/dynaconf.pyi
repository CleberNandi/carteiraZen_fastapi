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
    SMTP_USER: str
    SMTP_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    SMTP_SERVER: str
    SMTP_PORT: str
    def __init__(self, *args: object, **kwargs: object) -> None: ...
