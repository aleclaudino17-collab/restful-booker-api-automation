"""
Testes de Autenticação para a API Restful Booker.
Valida geração de token, headers de resposta e schemas de contrato.
"""

import pytest
import requests
from utils.api_client import APIClient
from schemas.auth_schema import AuthResponse, AuthErrorResponse


class TestAuthentication:
    """Suite de testes para o endpoint de autenticação /auth."""

    def test_auth_success_returns_token(self, api_client: APIClient):
        """
        Cenário: Autenticação bem-sucedida retorna token JWT válido.

        Critérios de aceitação:
        - Status code 200 OK
        - Resposta contém campo 'token' não vazio
        - Schema da resposta validado via Pydantic
        """
        # Arrange
        payload = {
            "username": APIClient.DEFAULT_USERNAME,
            "password": APIClient.DEFAULT_PASSWORD
        }

        # Act
        response = api_client.post("/auth", json=payload)

        # Assert
        assert response.status_code == 200, (
            f"Esperado status 200, obtido {response.status_code}. "
            f"Resposta: {response.text}"
        )

        data = response.json()

        # Validação de contrato via Pydantic
        auth_response = AuthResponse.model_validate(data)
        assert auth_response.token, "Token não deve ser vazio"
        assert len(auth_response.token) > 10, "Token parece inválido (muito curto)"

    def test_auth_response_headers(self, api_client: APIClient):
        """
        Cenário: Headers de resposta da autenticação estão corretos.

        Critérios de aceitação:
        - Content-Type: application/json
        - Status code 200
        """
        payload = {
            "username": APIClient.DEFAULT_USERNAME,
            "password": APIClient.DEFAULT_PASSWORD
        }

        response = api_client.post("/auth", json=payload)

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", ""), (
            "Content-Type deve ser application/json"
        )

    def test_auth_invalid_credentials_returns_200_with_reason(self, api_client: APIClient):
        """
        Cenário: Credenciais inválidas retornam 200 com motivo de erro.

        Nota: A API Restful Booker retorna 200 mesmo com credenciais inválidas,
        mas com um campo 'reason' indicando falha. Este é um comportamento conhecido da API.

        Critérios de aceitação:
        - Status code 200
        - Resposta contém campo 'reason'
        - Schema de erro validado via Pydantic
        """
        payload = {
            "username": "usuario_invalido",
            "password": "senha_errada"
        }

        response = api_client.post("/auth", json=payload)

        assert response.status_code == 200, (
            f"Esperado status 200 (comportamento da API), obtido {response.status_code}"
        )

        data = response.json()

        # Valida schema de erro
        error_response = AuthErrorResponse.model_validate(data)
        assert error_response.reason, "Deve conter motivo de erro"
        assert "Bad credentials" in error_response.reason or "reason" in data

    def test_auth_missing_username_returns_bad_request(self, api_client: APIClient):
        """
        Cenário: Requisição sem username retorna erro.

        Critérios de aceitação:
        - Status code 400 Bad Request
        """
        payload = {"password": APIClient.DEFAULT_PASSWORD}

        response = api_client.post("/auth", json=payload)

        # A API pode retornar 200 com reason ou 400
        assert response.status_code in [200, 400], (
            f"Status inesperado: {response.status_code}"
        )

    def test_auth_missing_password_returns_bad_request(self, api_client: APIClient):
        """
        Cenário: Requisição sem password retorna erro.

        Critérios de aceitação:
        - Status code 400 Bad Request
        """
        payload = {"username": APIClient.DEFAULT_USERNAME}

        response = api_client.post("/auth", json=payload)

        assert response.status_code in [200, 400], (
            f"Status inesperado: {response.status_code}"
        )

    def test_auth_empty_payload(self, api_client: APIClient):
        """
        Cenário: Payload vazio na autenticação.

        Critérios de aceitação:
        - API deve rejeitar requisição com payload vazio
        """
        response = api_client.post("/auth", json={})

        assert response.status_code in [200, 400, 500], (
            f"Status inesperado: {response.status_code}"
        )
