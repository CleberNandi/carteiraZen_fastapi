from dataclasses import dataclass


@dataclass(frozen=True)
class AppError:
    code: str
    message_template: str

    def format(self, **kwargs: object) -> dict[str, str]:
        return {"code": self.code, "message": self.message_template.format(**kwargs)}
