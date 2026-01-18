from datetime import date
import time
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.tables import LoveDailyRef, MessageOwnerIndex
from .database import DBManager


class LoveRepo:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    async def get_or_create_daily_ref(
        self, session: AsyncSession, group_id: str, user_id: str
    ) -> LoveDailyRef:
        today = date.today()
        stmt = select(LoveDailyRef).where(
            LoveDailyRef.date == today,
            LoveDailyRef.group_id == group_id,
            LoveDailyRef.user_id == user_id,
        )
        result = await session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            record = LoveDailyRef(
                date=today, group_id=group_id, user_id=user_id, updated_at=time.time()
            )
            session.add(record)
            # Flush to get ID if needed immediately, though session commit will handle it
            await session.flush()

        return record

    async def update_msg_stats(
        self, group_id: str, user_id: str, text_len: int, image_count: int = 0
    ):
        async with self.db.get_session() as session:
            record = await self.get_or_create_daily_ref(session, group_id, user_id)
            record.msg_sent += 1
            record.text_len_total += text_len
            record.image_sent += image_count
            record.updated_at = time.time()
            session.add(record)

    async def save_message_index(self, message_id: str, group_id: str, user_id: str):
        async with self.db.get_session() as session:
            idx = MessageOwnerIndex(
                message_id=message_id,
                group_id=group_id,
                user_id=user_id,
                timestamp=time.time(),
            )
            session.add(idx)

    async def get_message_owner(self, message_id: str) -> Optional[MessageOwnerIndex]:
        async with self.db.get_session() as session:
            stmt = select(MessageOwnerIndex).where(
                MessageOwnerIndex.message_id == message_id
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def update_interaction_sent(
        self,
        group_id: str,
        user_id: str,
        poke: int = 0,
        reply: int = 0,
        reaction: int = 0,
        recall: int = 0,
    ):
        async with self.db.get_session() as session:
            record = await self.get_or_create_daily_ref(session, group_id, user_id)
            record.poke_sent += poke
            record.reply_sent += reply
            record.reaction_sent += reaction
            record.recall_count += recall
            record.updated_at = time.time()
            session.add(record)

    async def update_interaction_received(
        self,
        group_id: str,
        user_id: str,
        poke: int = 0,
        reply: int = 0,
        reaction: int = 0,
    ):
        async with self.db.get_session() as session:
            record = await self.get_or_create_daily_ref(session, group_id, user_id)
            record.poke_received += poke
            record.reply_received += reply
            record.reaction_received += reaction
            record.updated_at = time.time()
            session.add(record)

    async def get_today_data(
        self, group_id: str, user_id: str
    ) -> Optional[LoveDailyRef]:
        async with self.db.get_session() as session:
            today = date.today()
            stmt = select(LoveDailyRef).where(
                LoveDailyRef.date == today,
                LoveDailyRef.group_id == group_id,
                LoveDailyRef.user_id == user_id,
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
