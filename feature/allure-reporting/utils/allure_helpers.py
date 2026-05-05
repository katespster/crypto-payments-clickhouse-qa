import json
import allure


def attach_json(name: str, data: dict) -> None:
    allure.attach(
        json.dumps(data, indent=2, ensure_ascii=False),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_text(name: str, text: str) -> None:
    allure.attach(
        text,
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )