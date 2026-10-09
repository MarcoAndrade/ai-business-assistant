from datetime import date as Date
from langchain.tools import tool
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.ai.tool_schemas import (
    GetProductInput,
    GetLowStockInput,
    GetDailySalesInput,
    RegisterSaleInput
    )
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.exceptions import (
    ProductNotFoundError,
    CustomerNotFoundError,
    InsufficientStockError,
    InactiveProductError,
)
from app.services.product_service import ProductService
from app.services.sale_service import SaleService
from app.repositories.sales_report_repository import SalesReportRepository


@tool(args_schema=GetProductInput)
def get_product(product_id: int) -> dict:
    """Consulta los datos reales de un producto por su ID."""

    with SessionLocal() as db:
        service = ProductService(db)
        product = service.get(product_id)

        if product is None:
            return {
                "found": False,
                "message": "No se encontró el producto."
            }

        return {
            "found": True,
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "stock": product.stock,
            "active": product.active,
        }


@tool(args_schema=GetLowStockInput)
def get_low_stock_products(threshold: int = 5) -> dict:
    """Lista productos activos cuyo stock es menor o igual al umbral."""

    with SessionLocal() as db:
        service = ProductService(db)

        # Ajusta el nombre del método a tu ProductService.
        products = service.list(skip=0, limit=500)

        low_stock = [
            {
                "id": p.id,
                "name": p.name,
                "stock": p.stock,
                "price": str(p.price),
            }
            for p in products
            if p.active and p.stock <= threshold
        ]

        return {
            "threshold": threshold,
            "count": len(low_stock),
            "products": low_stock,
        }

@tool(args_schema=GetDailySalesInput)
def get_daily_sales(date: str) -> dict:
    """Consulta el número de ventas y el total vendido en una fecha."""

    try:
        target_date = Date.fromisoformat(date)
    except ValueError:
        return {
            "success": False,
            "message": "Fecha inválida. Utiliza YYYY-MM-DD."
        }

    with SessionLocal() as db:
        return SalesReportRepository(db).get_daily_summary(target_date)

@tool(args_schema=RegisterSaleInput)
def register_sale(
    customer_id: int | None,
    items: list[dict],
) -> dict:
    """
    Registra una venta con productos y cantidades explícitos.
    Los precios y el total se calculan en el servicio de negocio.
    """

    sale_data = SaleCreate(
        customer_id=customer_id,
        items=[
            SaleItemCreate(
                product_id=item["product_id"],
                quantity=item["quantity"],
            )
            for item in items
        ],
    )

    with SessionLocal() as db:
        try:
            sale = SaleService(db).create(sale_data)

            return {
                "success": True,
                "sale_id": sale.id,
                "total": str(sale.total),
                "message": "Venta registrada correctamente.",
            }

        except ProductNotFoundError:
            return {
                "success": False,
                "error": "product_not_found",
                "message": "Uno de los productos no existe.",
            }

        except CustomerNotFoundError:
            return {
                "success": False,
                "error": "customer_not_found",
                "message": "El cliente indicado no existe.",
            }

        except InsufficientStockError:
            return {
                "success": False,
                "error": "insufficient_stock",
                "message": "No hay inventario suficiente.",
            }

        except InactiveProductError:
            return {
                "success": False,
                "error": "inactive_product",
                "message": "Uno de los productos está inactivo.",
            }

        except Exception:
            # No exponer al modelo trazas, credenciales ni errores internos.
            # En el siguiente ajuste sustituiremos esto por excepciones
            # de negocio específicas.
            return {
                "success": False,
                "message": (
                    "No fue posible registrar la venta. "
                    "Verifica los datos o solicita asistencia."
                ),
            }

AI_TOOLS = [
    get_product,
    get_low_stock_products,
    get_daily_sales,
    register_sale,
]