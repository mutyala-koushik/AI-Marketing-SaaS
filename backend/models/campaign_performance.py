from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
)

from database.database import Base


class CampaignPerformance(Base):
    __tablename__ = "campaign_performance"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    campaign_id = Column(
        Integer,
        ForeignKey("campaign_history.id"),
        nullable=False,
        index=True,
    )

    impressions = Column(
        Integer,
        nullable=False,
        default=0,
    )

    clicks = Column(
        Integer,
        nullable=False,
        default=0,
    )

    conversions = Column(
        Integer,
        nullable=False,
        default=0,
    )

    ad_spend = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    revenue = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )