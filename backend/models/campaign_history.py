from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from database.database import Base


class CampaignHistory(Base):
    __tablename__ = "campaign_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    product = Column(
        String(255),
        nullable=False,
    )

    persona = Column(
        String(255),
        nullable=False,
    )

    platform = Column(
        String(100),
        nullable=False,
    )

    marketing_goal = Column(
        String(100),
        nullable=False,
    )

    variant_id = Column(
        Integer,
        nullable=False,
    )

    style = Column(
        String(100),
        nullable=False,
    )

    headline = Column(
        String(500),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    call_to_action = Column(
        String(255),
        nullable=False,
    )

    offer = Column(
        String(500),
        nullable=False,
    )

    score = Column(
        Float,
        nullable=True,
    )

    status = Column(
        String(100),
        nullable=False,
        default="Ready to Launch",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )