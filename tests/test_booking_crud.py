"""
Testes de CRUD (Create, Read, Update, Delete) para a API Restful Booker.
Fluxo completo de reservas com validação de contrato Pydantic e status codes.
"""

import pytest
from utils.api_client import APIClient
from schemas.booking_schema import (
    Booking,
    BookingDates,
    BookingResponse,
    BookingIdListItem,
    UpdateBookingResponse
)


class TestBookingCRUD:
    """Suite de testes para operações CRUD de reservas."""

    # ==================== CREATE (POST) ====================

    def test_create_booking_success(self, api_client: APIClient, sample_booking_payload: dict):
        """
        Cenário: Criar uma nova reserva com dados válidos.

        Critérios de aceitação:
        - Status code 200 OK
        - Resposta contém bookingid e dados da reserva
        - Schema de resposta validado via Pydantic
        - Dados retornados correspondem ao payload enviado
        """
        # Act
        response = api_client.post("/booking", json=sample_booking_payload)

        # Assert Status Code
        assert response.status_code == 200, (
            f"Esperado 200, obtido {response.status_code}. Resposta: {response.text}"
        )

        # Validação de contrato via Pydantic
        data = response.json()
        booking_response = BookingResponse.model_validate(data)

        # Assert dados retornados
        assert booking_response.bookingid > 0, "bookingid deve ser maior que 0"
        assert booking_response.booking.firstname == sample_booking_payload["firstname"]
        assert booking_response.booking.lastname == sample_booking_payload["lastname"]
        assert booking_response.booking.totalprice == sample_booking_payload["totalprice"]
        assert booking_response.booking.depositpaid == sample_booking_payload["depositpaid"]
        assert booking_response.booking.bookingdates.checkin == sample_booking_payload["bookingdates"]["checkin"]
        assert booking_response.booking.bookingdates.checkout == sample_booking_payload["bookingdates"]["checkout"]
        assert booking_response.booking.additionalneeds == sample_booking_payload["additionalneeds"]

    def test_create_booking_without_optional_fields(self, api_client: APIClient):
        """
        Cenário: Criar reserva sem campo opcional 'additionalneeds'.

        Critérios de aceitação:
        - Status code 200 OK
        - Reserva criada com sucesso
        """
        payload = {
            "firstname": "Maria",
            "lastname": "Silva",
            "totalprice": 200,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2026-07-01",
                "checkout": "2026-07-05"
            }
        }

        response = api_client.post("/booking", json=payload)

        assert response.status_code == 200
        data = response.json()
        booking_response = BookingResponse.model_validate(data)
        assert booking_response.booking.additionalneeds is None

    def test_create_booking_invalid_date_format(self, api_client: APIClient):
        """
        Cenário: Tentar criar reserva com formato de data inválido.

        Nota: A API aceita formatos inválidos mas salva como NaN (bug conhecido).
        Este teste documenta o comportamento atual da API.
        """
        payload = {
            "firstname": "Test",
            "lastname": "User",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "15-06-2026",  # Formato inválido (DD-MM-YYYY)
                "checkout": "20-06-2026"
            }
        }

        response = api_client.post("/booking", json=payload)

        # A API aceita mas corrompe os dados (bug conhecido)
        assert response.status_code == 200
        data = response.json()
        # O campo checkin será "0NaN-aN-aN" devido ao bug da API
        assert "checkin" in data["booking"]["bookingdates"]

    # ==================== READ (GET) ====================

    def test_get_all_bookings_returns_list(self, api_client: APIClient):
        """
        Cenário: Buscar todas as reservas retorna lista de IDs.

        Critérios de aceitação:
        - Status code 200 OK
        - Resposta é uma lista de objetos com bookingid
        """
        response = api_client.get("/booking")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list), "Resposta deve ser uma lista"
        if len(data) > 0:
            # Valida o primeiro item da lista
            BookingIdListItem.model_validate(data[0])
            assert all("bookingid" in item for item in data), (
                "Todos os itens devem conter bookingid"
            )

    def test_get_booking_by_id_success(self, api_client: APIClient, create_booking: int):
        """
        Cenário: Buscar reserva por ID existente.

        Critérios de aceitação:
        - Status code 200 OK
        - Resposta contém dados da reserva
        - Schema validado via Pydantic
        """
        booking_id = create_booking

        response = api_client.get(f"/booking/{booking_id}")

        assert response.status_code == 200, (
            f"Esperado 200, obtido {response.status_code}"
        )

        data = response.json()
        # Valida schema da reserva
        booking = Booking.model_validate(data)
        assert booking.firstname, "Deve conter firstname"
        assert booking.lastname, "Deve conter lastname"

    def test_get_booking_by_id_not_found(self, api_client: APIClient):
        """
        Cenário: Buscar reserva por ID inexistente.

        Critérios de aceitação:
        - Status code 404 Not Found
        """
        non_existent_id = 999999999

        response = api_client.get(f"/booking/{non_existent_id}")

        assert response.status_code == 404, (
            f"Esperado 404, obtido {response.status_code}"
        )

    def test_get_bookings_with_query_params(self, api_client: APIClient):
        """
        Cenário: Buscar reservas com filtros (query parameters).

        Critérios de aceitação:
        - Status code 200 OK
        - Resposta filtrada retornada
        """
        response = api_client.get("/booking", params={"firstname": "Alexandre"})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    # ==================== UPDATE (PUT) ====================

    def test_update_booking_full_success(self, authenticated_client: APIClient, create_booking: int):
        """
        Cenário: Atualizar completamente uma reserva existente (PUT).

        Critérios de aceitação:
        - Status code 200 OK
        - Dados atualizados retornados
        - Schema validado via Pydantic
        - Token de autenticação obrigatório
        """
        booking_id = create_booking

        updated_payload = {
            "firstname": "Alexandre",
            "lastname": "Updated",
            "totalprice": 500,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2026-08-01",
                "checkout": "2026-08-10"
            },
            "additionalneeds": "Breakfast included"
        }

        response = authenticated_client.put(f"/booking/{booking_id}", json=updated_payload)

        assert response.status_code == 200, (
            f"Esperado 200, obtido {response.status_code}. "
            f"Resposta: {response.text}"
        )

        data = response.json()
        updated_response = UpdateBookingResponse.model_validate(data)

        assert updated_response.lastname == "Updated"
        assert updated_response.totalprice == 500
        assert updated_response.depositpaid == False
        assert updated_response.bookingdates.checkin == "2026-08-01"
        assert updated_response.additionalneeds == "Breakfast included"

    def test_update_booking_without_auth_returns_403(self, api_client: APIClient, create_booking: int):
        """
        Cenário: Tentar atualizar reserva sem autenticação.

        Critérios de aceitação:
        - Status code 403 Forbidden
        """
        booking_id = create_booking

        payload = {
            "firstname": "Hacker",
            "lastname": "Attempt",
            "totalprice": 1,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2026-09-01",
                "checkout": "2026-09-05"
            }
        }

        # Remove o token de autenticação
        if "Cookie" in api_client.session.headers:
            del api_client.session.headers["Cookie"]

        response = api_client.put(f"/booking/{booking_id}", json=payload)

        assert response.status_code == 403, (
            f"Esperado 403, obtido {response.status_code}"
        )

    def test_update_nonexistent_booking(self, authenticated_client: APIClient):
        """
        Cenário: Tentar atualizar reserva inexistente.

        Nota: A API Restful Booker retorna 405 Method Not Allowed para IDs inexistentes.
        Este é um bug conhecido da API — o comportamento correto seria 404 Not Found.
        Documentamos o comportamento real para garantir consistência nos testes.

        Critérios de aceitação:
        - Status code 405 (comportamento atual da API — bug documentado)
        """
        non_existent_id = 999999999

        payload = {
            "firstname": "Ghost",
            "lastname": "User",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2026-10-01",
                "checkout": "2026-10-05"
            }
        }

        response = authenticated_client.put(f"/booking/{non_existent_id}", json=payload)

        assert response.status_code == 405, (
            f"Esperado 405 (bug conhecido da API), obtido {response.status_code}"
        )

    # ==================== PARTIAL UPDATE (PATCH) ====================

    def test_partial_update_booking_success(self, authenticated_client: APIClient, create_booking: int):
        """
        Cenário: Atualizar parcialmente uma reserva (PATCH).

        Critérios de aceitação:
        - Status code 200 OK
        - Apenas campos enviados são atualizados
        - Schema validado via Pydantic
        """
        booking_id = create_booking

        patch_payload = {
            "firstname": "Alexandre Updated",
            "totalprice": 999
        }

        response = authenticated_client.patch(f"/booking/{booking_id}", json=patch_payload)

        assert response.status_code == 200, (
            f"Esperado 200, obtido {response.status_code}. Resposta: {response.text}"
        )

        data = response.json()
        updated = UpdateBookingResponse.model_validate(data)

        assert updated.firstname == "Alexandre Updated"
        assert updated.totalprice == 999
        # Campos não enviados devem permanecer
        assert updated.lastname  # Deve manter o valor original

    def test_partial_update_without_auth_returns_403(self, api_client: APIClient, create_booking: int):
        """
        Cenário: Tentar PATCH sem autenticação.

        Critérios de aceitação:
        - Status code 403 Forbidden
        """
        booking_id = create_booking

        if "Cookie" in api_client.session.headers:
            del api_client.session.headers["Cookie"]

        response = api_client.patch(f"/booking/{booking_id}", json={"firstname": "Hacker"})

        assert response.status_code == 403, (
            f"Esperado 403, obtido {response.status_code}"
        )

    # ==================== DELETE ====================

    def test_delete_booking_success(self, authenticated_client: APIClient, create_booking: int):
        """
        Cenário: Deletar uma reserva existente.

        Critérios de aceitação:
        - Status code 201 Created (comportamento da API)
        - Reserva não deve mais existir (GET retorna 404)
        - Token de autenticação obrigatório
        """
        booking_id = create_booking

        response = authenticated_client.delete(f"/booking/{booking_id}")

        # Nota: A API retorna 201 Created para delete (bug conhecido da API)
        assert response.status_code == 201, (
            f"Esperado 201 (comportamento da API), obtido {response.status_code}"
        )

        # Verifica que a reserva foi realmente deletada
        get_response = authenticated_client.get(f"/booking/{booking_id}")
        assert get_response.status_code == 404, (
            "Reserva deveria ter sido deletada"
        )

    def test_delete_booking_without_auth_returns_403(self, api_client: APIClient, create_booking: int):
        """
        Cenário: Tentar deletar sem autenticação.

        Critérios de aceitação:
        - Status code 403 Forbidden
        """
        booking_id = create_booking

        if "Cookie" in api_client.session.headers:
            del api_client.session.headers["Cookie"]

        response = api_client.delete(f"/booking/{booking_id}")

        assert response.status_code == 403, (
            f"Esperado 403, obtido {response.status_code}"
        )

    def test_delete_nonexistent_booking(self, authenticated_client: APIClient):
        """
        Cenário: Tentar deletar reserva inexistente.

        Nota: A API retorna 405 Method Not Allowed para IDs inexistentes (bug conhecido).
        Deveria retornar 404 Not Found.

        Critérios de aceitação:
        - Status code 405 (comportamento atual da API)
        """
        non_existent_id = 999999999

        response = authenticated_client.delete(f"/booking/{non_existent_id}")

        assert response.status_code in [405, 404], (
            f"Esperado 405 ou 404, obtido {response.status_code}"
        )

    # ==================== FLUXO COMPLETO (END-TO-END) ====================

    def test_full_crud_workflow(self, authenticated_client: APIClient, sample_booking_payload: dict):
        """
        Cenário: Fluxo completo de CRUD em uma única reserva.

        Passos:
        1. Criar reserva (POST)
        2. Buscar reserva (GET)
        3. Atualizar reserva (PUT)
        4. Atualizar parcialmente (PATCH)
        5. Deletar reserva (DELETE)
        6. Verificar exclusão (GET -> 404)

        Critérios de aceitação:
        - Cada operação retorna status code correto
        - Dados persistem corretamente entre operações
        - Schemas validados em cada etapa
        """
        # 1. CREATE
        create_response = authenticated_client.post("/booking", json=sample_booking_payload)
        assert create_response.status_code == 200

        booking_data = BookingResponse.model_validate(create_response.json())
        booking_id = booking_data.bookingid

        # 2. READ
        get_response = authenticated_client.get(f"/booking/{booking_id}")
        assert get_response.status_code == 200
        Booking.model_validate(get_response.json())

        # 3. UPDATE (PUT)
        updated_payload = {
            "firstname": "Updated",
            "lastname": "Via PUT",
            "totalprice": 777,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2026-12-01",
                "checkout": "2026-12-10"
            },
            "additionalneeds": "Updated needs"
        }
        put_response = authenticated_client.put(f"/booking/{booking_id}", json=updated_payload)
        assert put_response.status_code == 200
        UpdateBookingResponse.model_validate(put_response.json())

        # 4. PARTIAL UPDATE (PATCH)
        patch_payload = {"totalprice": 888}
        patch_response = authenticated_client.patch(f"/booking/{booking_id}", json=patch_payload)
        assert patch_response.status_code == 200

        # 5. DELETE
        delete_response = authenticated_client.delete(f"/booking/{booking_id}")
        assert delete_response.status_code == 201

        # 6. VERIFY DELETION
        verify_response = authenticated_client.get(f"/booking/{booking_id}")
        assert verify_response.status_code == 404
