"""
HTTP API Client para Restful Booker API.
Encapsula requisições HTTP, gerenciamento de headers e persistência de token JWT.
"""

import requests
from typing import Any, Dict, Optional
from urllib.parse import urljoin


class APIClient:
    """Cliente HTTP profissional para APIs RESTful."""

    BASE_URL = "https://restful-booker.herokuapp.com"

    # Credenciais padrão da API (documentação oficial)
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "password123"

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._token: Optional[str] = None

        # Headers padrão para todas as requisições
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "RestfulBooker-QA-Automation/1.0"
        })

    @property
    def token(self) -> Optional[str]:
        """Retorna o token de autenticação atual."""
        return self._token

    @token.setter
    def token(self, value: str) -> None:
        """Define o token de autenticação e atualiza o header Cookie."""
        self._token = value
        self.session.headers["Cookie"] = f"token={value}"

    def authenticate(self, username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> str:
        """
        Realiza autenticação na API e armazena o token JWT.

        Args:
            username: Nome de usuário para autenticação.
            password: Senha para autenticação.

        Returns:
            Token JWT gerado pela API.

        Raises:
            requests.HTTPError: Se a autenticação falhar.
        """
        payload = {
            "username": username,
            "password": password
        }
        response = self.session.post(
            urljoin(self.base_url, "/auth"),
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        self.token = data["token"]
        return self._token

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Executa requisição GET."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        return self.session.get(url, params=params, **kwargs)

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Executa requisição POST."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        return self.session.post(url, json=json, **kwargs)

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Executa requisição PUT."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        return self.session.put(url, json=json, **kwargs)

    def patch(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Executa requisição PATCH."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        return self.session.patch(url, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Executa requisição DELETE."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        return self.session.delete(url, **kwargs)

    def ping(self) -> requests.Response:
        """Verifica se a API está online (health check)."""
        return self.get("/ping")
