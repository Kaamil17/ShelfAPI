from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    # I could add a createdAt or updatedAt fields, but for this taks i am keeping it lightweight
    pass

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    productid: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    ''' 
    Since we are querying for a range a composite i added a composite index here.
    '''
    __table_args__ = (

        Index("ix_inventory_productid_timestamp", "productid", "timestamp"),
    )
