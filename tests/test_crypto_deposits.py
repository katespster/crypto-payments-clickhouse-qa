import allure
import pytest

from utils.allure_helpers import attach_json


class FakeResponse:
    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self._body = body

    def json(self) -> dict:
        return self._body


class FakeApiClient:
    """
    Fake API client for portfolio/demo purposes.
    Later it can be replaced with a real requests-based API client.
    """

    def post(self, endpoint: str, json: dict) -> FakeResponse:
        if endpoint != "/deposits":
            return FakeResponse(404, {"error": "Endpoint not found"})

        required_fields = ["currency", "amount", "user_id"]

        for field in required_fields:
            if field not in json:
                return FakeResponse(
                    422,
                    {
                        "error": "Validation error",
                        "message": f"Missing required field: {field}",
                    },
                )

        if json["amount"] <= 0:
            return FakeResponse(
                400,
                {
                    "error": "Validation error",
                    "message": "Amount must be greater than zero",
                },
            )

        supported_currencies = ["BTC", "ETH", "BSC", "TRON"]

        if json["currency"] not in supported_currencies:
            return FakeResponse(
                400,
                {
                    "error": "Unsupported currency",
                    "currency": json["currency"],
                },
            )

        return FakeResponse(
            201,
            {
                "deposit_id": "dep-test-001",
                "currency": json["currency"],
                "amount": json["amount"],
                "user_id": json["user_id"],
                "status": "created",
            },
        )


@pytest.fixture
def api_client():
    return FakeApiClient()


@allure.epic("Crypto Payments")
@allure.feature("Deposits API")
@allure.story("Create deposit")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Create BTC deposit with valid amount")
def test_create_btc_deposit(api_client):
    payload = {
        "currency": "BTC",
        "amount": 100,
        "user_id": "test-user-001",
    }

    with allure.step("Send deposit creation request"):
        response = api_client.post("/deposits", json=payload)
        attach_json("Request payload", payload)
        attach_json("Response body", response.json())

    with allure.step("Verify HTTP status code"):
        assert response.status_code == 201

    with allure.step("Verify deposit response fields"):
        body = response.json()
        assert body["deposit_id"] is not None
        assert body["currency"] == "BTC"
        assert body["amount"] == 100
        assert body["user_id"] == "test-user-001"
        assert body["status"] in ["created", "pending"]


@allure.epic("Crypto Payments")
@allure.feature("Deposits API")
@allure.story("Create deposit")
@allure.title("Create deposit with supported crypto currency: {currency}")
@pytest.mark.parametrize("currency", ["BTC", "ETH", "BSC", "TRON"])
def test_create_deposit_with_supported_currency(api_client, currency):
    payload = {
        "currency": currency,
        "amount": 50,
        "user_id": "test-user-002",
    }

    with allure.step(f"Send deposit creation request for {currency}"):
        response = api_client.post("/deposits", json=payload)
        attach_json("Request payload", payload)
        attach_json("Response body", response.json())

    with allure.step("Verify deposit is created"):
        assert response.status_code == 201
        assert response.json()["currency"] == currency
        assert response.json()["status"] == "created"


@allure.epic("Crypto Payments")
@allure.feature("Deposits API")
@allure.story("Deposit validation")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Create deposit with invalid amount")
@pytest.mark.parametrize("amount", [0, -1, -100])
def test_create_deposit_with_invalid_amount(api_client, amount):
    payload = {
        "currency": "BTC",
        "amount": amount,
        "user_id": "test-user-003",
    }

    with allure.step("Send deposit request with invalid amount"):
        response = api_client.post("/deposits", json=payload)
        attach_json("Request payload", payload)
        attach_json("Response body", response.json())

    with allure.step("Verify validation error"):
        assert response.status_code == 400
        assert response.json()["error"] == "Validation error"


@allure.epic("Crypto Payments")
@allure.feature("Deposits API")
@allure.story("Deposit validation")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Create deposit with unsupported currency")
def test_create_deposit_with_unsupported_currency(api_client):
    payload = {
        "currency": "DOGE",
        "amount": 100,
        "user_id": "test-user-004",
    }

    with allure.step("Send deposit request with unsupported currency"):
        response = api_client.post("/deposits", json=payload)
        attach_json("Request payload", payload)
        attach_json("Response body", response.json())

    with allure.step("Verify unsupported currency error"):
        assert response.status_code == 400
        assert response.json()["error"] == "Unsupported currency"
        assert response.json()["currency"] == "DOGE"


@allure.epic("Crypto Payments")
@allure.feature("Deposits API")
@allure.story("Deposit validation")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Create deposit without user_id")
def test_create_deposit_without_user_id(api_client):
    payload = {
        "currency": "BTC",
        "amount": 100,
    }

    with allure.step("Send deposit request without user_id"):
        response = api_client.post("/deposits", json=payload)
        attach_json("Request payload", payload)
        attach_json("Response body", response.json())

    with allure.step("Verify missing field validation error"):
        assert response.status_code == 422
        assert response.json()["error"] == "Validation error"
        assert "Missing required field" in response.json()["message"]