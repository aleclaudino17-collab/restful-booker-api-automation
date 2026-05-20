"""
Schemas Pydantic para validação de contrato da API de Reservas (Bookings).
Validação rigorosa de tipos, formatos e estrutura dos dados da API Restful Booker.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import date


class BookingDates(BaseModel):
    """Modelo para as datas de check-in e check-out da reserva."""
    checkin: str = Field(
        ..., 
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de check-in no formato YYYY-MM-DD"
    )
    checkout: str = Field(
        ..., 
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de check-out no formato YYYY-MM-DD"
    )

    @field_validator("checkout")
    @classmethod
    def checkout_after_checkin(cls, v: str, info) -> str:
        """Valida que checkout é posterior ao checkin."""
        checkin = info.data.get("checkin")
        if checkin and v <= checkin:
            raise ValueError("Checkout date must be after checkin date")
        return v


class Booking(BaseModel):
    """Modelo principal de uma reserva (Booking)."""
    firstname: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Primeiro nome do hóspede"
    )
    lastname: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Sobrenome do hóspede"
    )
    totalprice: int = Field(
        ..., 
        ge=0, 
        description="Preço total da reserva em valor inteiro"
    )
    depositpaid: bool = Field(
        ..., 
        description="Indica se o depósito foi pago"
    )
    bookingdates: BookingDates = Field(
        ..., 
        description="Datas de check-in e check-out"
    )
    additionalneeds: Optional[str] = Field(
        default=None, 
        description="Necessidades adicionais do hóspede"
    )


class BookingResponse(BaseModel):
    """Modelo de resposta ao criar uma nova reserva (POST /booking)."""
    bookingid: int = Field(
        ..., 
        gt=0, 
        description="ID único da reserva criada"
    )
    booking: Booking = Field(
        ..., 
        description="Dados da reserva criada"
    )


class BookingIdListItem(BaseModel):
    """Modelo para item da lista de IDs de reservas."""
    bookingid: int = Field(
        ..., 
        gt=0, 
        description="ID da reserva"
    )


class UpdateBookingResponse(BaseModel):
    """Modelo de resposta para atualização de reserva (PUT /booking/:id)."""
    firstname: str = Field(..., min_length=1)
    lastname: str = Field(..., min_length=1)
    totalprice: int = Field(..., ge=0)
    depositpaid: bool = Field(...)
    bookingdates: BookingDates = Field(...)
    additionalneeds: Optional[str] = Field(default=None)
