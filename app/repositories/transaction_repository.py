from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.DAO.transaction_dao import TransactionDAO
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.transaction_type import TransactionType
from app.database.database import AsyncSessionLocal
from datetime import datetime
from typing import Optional, List

class TransactionRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_transaction(self, amount: float, type: TransactionType, description: str | None, user_id: int | None) -> TransactionDAO:
        async with await self._get_session() as session:
            # Create transaction record
            transaction = TransactionDAO(
                amount=amount,
                type=type,
                description=description,
                created_by=user_id
            )
            session.add(transaction)

            # Update system balance
            # Assuming there is only one system info row, or we create one if not exists
            result = await session.execute(select(SystemInfoDAO).limit(1))
            system_info = result.scalars().first()
            
            if not system_info:
                system_info = SystemInfoDAO(balance=0.0)
                session.add(system_info)
            
            if type == TransactionType.CREDIT:
                system_info.balance += amount
            elif type == TransactionType.DEBIT:
                system_info.balance -= amount
            
            await session.commit()
            await session.refresh(transaction)
            return transaction

    async def get_transactions(self, start_date: datetime | None, end_date: datetime | None) -> List[TransactionDAO]:
        async with await self._get_session() as session:
            query = select(TransactionDAO)
            
            conditions = []
            if start_date:
                conditions.append(TransactionDAO.timestamp >= start_date)
            if end_date:
                conditions.append(TransactionDAO.timestamp <= end_date)
            
            if conditions:
                query = query.filter(and_(*conditions))
            
            query = query.order_by(TransactionDAO.timestamp.desc())
            
            result = await session.execute(query)
            return result.scalars().all()

    async def get_balance(self) -> float:
        async with await self._get_session() as session:
            system_info = result.scalars().first()
            return system_info.balance if system_info else 0.0

    async def set_balance(self, amount: float, user_id: int | None) -> TransactionDAO:
        async with await self._get_session() as session:
            # Get current balance (transactional, locking might be needed in real world but ok for now)
            result = await session.execute(select(SystemInfoDAO).limit(1))
            system_info = result.scalars().first()
            
            if not system_info:
                system_info = SystemInfoDAO(balance=0.0)
                session.add(system_info)
                current_balance = 0.0
            else:
                current_balance = system_info.balance
                
            difference = amount - current_balance
            
            if difference == 0:
                # No change needed, but maybe we want to log it? 
                # For now let's create a 0 amount transaction or just return a dummy
                # Postman doesn't specify behavior for 0 change. 
                # Let's create a transaction for record.
                # Assuming 0 diff is "CREDIT" 0.0
                correction_type = TransactionType.CREDIT
                correction_amount = 0.0
            elif difference > 0:
                correction_type = TransactionType.CREDIT
                correction_amount = difference
            else:
                correction_type = TransactionType.DEBIT
                correction_amount = abs(difference)
                
            # Create transaction record
            transaction = TransactionDAO(
                amount=correction_amount,
                type=correction_type,
                description="Balance correction (Set Balance)",
                created_by=user_id,
                timestamp=datetime.now()
            )
            session.add(transaction)
            
            # Update balance
            # We can trust our calc: current + diff = amount, OR just force set it.
            # Force setting is safer to match exact request.
            system_info.balance = amount
            
            await session.commit()
            await session.refresh(transaction)
            return transaction

    async def reset_balance(self, user_id: int | None) -> TransactionDAO:
        return await self.set_balance(0.0, user_id)
