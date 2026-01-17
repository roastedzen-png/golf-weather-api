"""
Usage Tracking Service

Tracks API usage for billing and analytics.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any

from app.models.database import APIUsage, RequestLog


class UsageService:
    """Service for tracking and querying API usage."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def track_request(
        self,
        client_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        latency_ms: float,
        request_id: str,
    ):
        """Track a single API request.

        Updates daily aggregates and logs individual request.
        """
        if self.db is None:
            return

        today = date.today()
        is_error = status_code >= 400

        try:
            # Upsert daily usage stats
            stmt = insert(APIUsage).values(
                client_id=client_id,
                endpoint=endpoint,
                date=today,
                request_count=1,
                error_count=1 if is_error else 0,
                total_latency_ms=latency_ms,
            ).on_conflict_do_update(
                index_elements=["client_id", "endpoint", "date"],
                set_={
                    "request_count": APIUsage.request_count + 1,
                    "error_count": APIUsage.error_count + (1 if is_error else 0),
                    "total_latency_ms": APIUsage.total_latency_ms + latency_ms,
                    "updated_at": datetime.utcnow(),
                },
            )
            await self.db.execute(stmt)

            # Log individual request
            log = RequestLog(
                request_id=request_id,
                client_id=client_id,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                latency_ms=latency_ms,
            )
            self.db.add(log)

            await self.db.commit()
        except Exception:
            # Don't fail the request if tracking fails
            await self.db.rollback()

    async def get_client_usage(
        self,
        client_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[APIUsage]:
        """Get usage stats for a client."""
        if self.db is None:
            return []

        query = select(APIUsage).where(APIUsage.client_id == client_id)

        if start_date:
            query = query.where(APIUsage.date >= start_date)
        if end_date:
            query = query.where(APIUsage.date <= end_date)

        query = query.order_by(APIUsage.date.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_usage_summary(self, client_id: str) -> Dict[str, Any]:
        """Get summary stats for a client."""
        if self.db is None:
            return {
                "total_requests": 0,
                "total_errors": 0,
                "avg_latency": 0,
                "first_request": None,
                "last_request": None,
            }

        query = select(
            func.sum(APIUsage.request_count).label("total_requests"),
            func.sum(APIUsage.error_count).label("total_errors"),
            func.sum(APIUsage.total_latency_ms).label("total_latency"),
            func.min(APIUsage.date).label("first_request"),
            func.max(APIUsage.date).label("last_request"),
        ).where(APIUsage.client_id == client_id)

        result = await self.db.execute(query)
        row = result.first()

        total_requests = row.total_requests or 0
        total_latency = row.total_latency or 0

        return {
            "total_requests": total_requests,
            "total_errors": row.total_errors or 0,
            "avg_latency": round(total_latency / total_requests, 2) if total_requests > 0 else 0,
            "first_request": row.first_request,
            "last_request": row.last_request,
        }

    async def get_all_clients_usage(
        self,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get usage stats for all clients."""
        if self.db is None:
            return []

        start_date = date.today() - timedelta(days=days)

        query = select(
            APIUsage.client_id,
            func.sum(APIUsage.request_count).label("total_requests"),
            func.sum(APIUsage.error_count).label("total_errors"),
            func.sum(APIUsage.total_latency_ms).label("total_latency"),
        ).where(
            APIUsage.date >= start_date
        ).group_by(
            APIUsage.client_id
        ).order_by(
            func.sum(APIUsage.request_count).desc()
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "client_id": row.client_id,
                "total_requests": row.total_requests,
                "total_errors": row.total_errors,
                "avg_latency_ms": round(row.total_latency / row.total_requests, 2) if row.total_requests > 0 else 0,
            }
            for row in rows
        ]
