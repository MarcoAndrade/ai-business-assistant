from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Intent = Literal[
    "product_query",
    "inventory_query",
    "sales_report",
    "quote_sale",
    "register_sale",
    "clarification",
    "unsupported",
]


class RequestedItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_name: str | None = Field(
        default=None,
        min_length=1,
        description="Nombre del producto mencionado por el usuario",
    )

    product_id: int | None = Field(
        default=None,
        gt=0,
        description="ID del producto, únicamente si el usuario lo especificó",
    )

    quantity: int | None = Field(
        default=None,
        gt=0,
        le=10000,
        description="Cantidad explícitamente solicitada",
    )


class BusinessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent = Field(
        description="Intención principal del usuario",
    )

    items: list[RequestedItem] = Field(
        default_factory=list,
        max_length=100,
        description="Productos y cantidades mencionados",
    )

    target_date: str | None = Field(
        default=None,
        description="Fecha de consulta en formato YYYY-MM-DD",
    )

    customer_id: int | None = Field(
        default=None,
        gt=0,
        description="ID del cliente, solo si fue indicado explícitamente",
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description="Datos necesarios que aún deben solicitarse",
    )

    requires_confirmation: bool = Field(
        default=False,
        description="Indica si el flujo requiere confirmación del usuario",
    )

    inventory_threshold: int | None = Field(
        default=None,
        ge=0,
        le=10000,
        description=(
            "Umbral máximo de existencias solicitado explícitamente "
            "para consultar inventario bajo"
        ),
    )

    @model_validator(mode="after")
    def validate_request(self):
        if self.intent in {"quote_sale", "register_sale"} and not self.items:
            if not self.missing_information:
                self.missing_information.append(
                    "Identificar al menos un producto y su cantidad"
                )

        if self.intent == "sales_report" and self.target_date is None:
            if not self.missing_information:
                self.missing_information.append(
                    "Fecha del reporte"
                )

        if self.intent in {"quote_sale", "register_sale"}:
            if not self.items:
                self.missing_information.append(
                    "Al menos un producto"
                )

            for index, item in enumerate(self.items, start=1):
                if item.product_id is None and not item.product_name:
                    self.missing_information.append(
                        f"Identificar el producto de la partida {index}"
                    )

                if item.quantity is None:
                    self.missing_information.append(
                        f"Cantidad de la partida {index}"
                    )

        return self

def validate_target_date(value: str | None) -> date | None:
    if value is None:
        return None

    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            "target_date debe tener el formato YYYY-MM-DD"
        ) from exc

    if parsed.isoformat() != value:
        raise ValueError(
            "target_date debe tener el formato YYYY-MM-DD"
        )

    return parsed