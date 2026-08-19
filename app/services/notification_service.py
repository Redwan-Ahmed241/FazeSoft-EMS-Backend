"""
app/services/notification_service.py — Business logic for notification operations.
"""
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationUpdate


class NotificationService:
    @staticmethod
    async def list_notifications(db: AsyncSession, current_user: User) -> List[Notification]:
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == current_user.id)
            .order_by(desc(Notification.created_at))
        )
        return list(result.scalars().all())

    @staticmethod
    async def mark_as_read(
        db: AsyncSession, notification_id: int, payload: NotificationUpdate, current_user: User
    ) -> Notification:
        result = await db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with id={notification_id} not found.",
            )

        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only update your own notifications.",
            )

        notification.is_read = payload.is_read
        await db.commit()
        await db.refresh(notification)
        return notification

    @staticmethod
    async def create_notification(
        db: AsyncSession, payload: NotificationCreate, current_user: User
    ) -> Notification:
        notification = Notification(
            user_id=payload.user_id,
            title=payload.title,
            message=payload.message,
            type=payload.type,
            is_read=False,
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification
