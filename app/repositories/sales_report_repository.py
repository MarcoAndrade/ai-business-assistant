from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Sale


BUSINESS_TZ = ZoneInfo("America/Mexico_City")


class SalesReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_summary(self, target_date: date) -> dict:
        # Límites del día en la zona horaria del negocio.
        start_local = datetime.combine(
            target_date, time.min, tzinfo=BUSINESS_TZ
        )
        end_local = datetime.combine(
            target_date + timedelta(days=1),
            time.min,
            tzinfo=BUSINESS_TZ,
        )

        # Convertir los límites a UTC para comparar timestamps con zona.
        from datetime import timezone

        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)

        statement = select(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total), 0),
        ).where(
            Sale.created_at >= start_utc,
            Sale.created_at < end_utc,
        )

        count, total = self.db.execute(statement).one()

        return {
            "date": target_date.isoformat(),
            "sales_count": count,
            "total": str(total),
        }