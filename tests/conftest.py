"""
Fixtures compartilhadas para os testes de API.
Fornece instâncias de APIClient e dados de teste reutilizáveis.
"""

import pytest
from utils.api_client import APIClient
from schemas.booking_schema import Booking, BookingDates


@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """Fixture que fornece uma instância do APIClient para toda a sessão de testes."""
    client = APIClient()
    # Verifica se a API está online antes de iniciar os testes
    ping_response = client.ping()
    assert ping_response.status_code == 201, "API Restful Booker está offline"
    return client


@pytest.fixture(scope="function")
def authenticated_client(api_client: APIClient) -> APIClient:
    """Fixture que retorna um cliente autenticado para cada teste."""
    api_client.authenticate()
    assert api_client.token is not None, "Falha na autenticação"
    return api_client


@pytest.fixture(scope="function")
def sample_booking_payload() -> dict:
    """Fixture que fornece um payload de reserva válido para testes."""
    return {
        "firstname": "Alexandre",
        "lastname": "Claudino",
        "totalprice": 350,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-06-15",
            "checkout": "2026-06-20"
        },
        "additionalneeds": "Late checkout, High floor"
    }


@pytest.fixture(scope="function")
def create_booking(api_client: APIClient, sample_booking_payload: dict) -> int:
    """Fixture que cria uma reserva e retorna o bookingid para testes dependentes."""
    response = api_client.post("/booking", json=sample_booking_payload)
    assert response.status_code == 200, f"Falha ao criar reserva: {response.text}"

    data = response.json()
    booking_id = data["bookingid"]

    yield booking_id

    # Cleanup: tenta deletar a reserva após o teste
    try:
        api_client.authenticate()
        api_client.delete(f"/booking/{booking_id}")
    except Exception:
        pass  # Ignora erros de cleanup
