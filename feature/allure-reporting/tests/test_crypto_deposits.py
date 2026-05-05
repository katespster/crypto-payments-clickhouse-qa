import allure
from utils.allure_helpers import attach_json


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

    with allure.step("Verify deposit fields"):
        body = response.json()
        assert body["currency"] == "BTC"
        assert body["amount"] == 100
        assert body["status"] in ["created", "pending"]