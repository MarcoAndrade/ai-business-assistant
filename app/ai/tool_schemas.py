from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated


class GetProductInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: Annotated[
        int,
        Field(gt=0, description="ID real del producto")
    ]


class GetLowStockInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    threshold: Annotated[
        int,
        Field(ge=0, le=10000,
              description="Stock máximo para considerar bajo inventario")
    ] = 5


class GetDailySalesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: Annotated[
        str,
        Field(
            description="Fecha de consulta en formato YYYY-MM-DD"
        )
    ]


class SaleItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: Annotated[int, Field(gt=0)]
    quantity: Annotated[int, Field(gt=0, le=10000)]


class RegisterSaleInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: int | None = Field(
        default=None,
        gt=0,
        description="ID del cliente; null si no se especifica"
    )

    items: Annotated[
        list[SaleItemInput],
        Field(min_length=1, max_length=100)
    ]