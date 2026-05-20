"""
Schemas Pydantic para validação de contrato da API de Autenticação.
Garante integridade estrutural e tipagem dos dados retornados.
"""

from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    """Modelo de requisição para geração de token de autenticação."""
    username: str = Field(
        ..., 
        min_length=1, 
        description="Nome de usuário para autenticação"
    )
    password: str = Field(
        ..., 
        min_length=1, 
        description="Senha para autenticação"
    )


class AuthResponse(BaseModel):
    """Modelo de resposta da API de autenticação com token JWT."""
    token: str = Field(
        ..., 
        min_length=1, 
        description="Token JWT para autenticação em endpoints protegidos"
    )


class AuthErrorResponse(BaseModel):
    """Modelo de resposta de erro da API de autenticação."""
    reason: str = Field(
        ..., 
        description="Motivo da falha na autenticação"
    )
