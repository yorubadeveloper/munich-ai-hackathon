import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class UserProfile(Base):
    __tablename__ = "user_profile"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    stack: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    dealbreakers: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    github_url: Mapped[str] = mapped_column(String, nullable=True)
    portfolio_url: Mapped[str] = mapped_column(String, nullable=True)
    projects: Mapped[str] = mapped_column(Text, nullable=True)
    # ── Targeting: what kind of companies/roles to surface ──
    target_industries: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    target_funding_stages: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    company_size: Mapped[str] = mapped_column(String, nullable=True)
    remote_pref: Mapped[str] = mapped_column(String, nullable=True)
    seniority: Mapped[str] = mapped_column(String, nullable=True)


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    website: Mapped[str] = mapped_column(String, nullable=True)
    job_url: Mapped[str] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=True)
    raw_job_text: Mapped[str] = mapped_column(Text, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    status: Mapped[str] = mapped_column(String, default="discovered")
    fit_score: Mapped[float] = mapped_column(Float, nullable=True)
    research: Mapped["Research"] = relationship(
        "Research", back_populates="company", uselist=False
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="company"
    )
    evidence_events: Mapped[list["EvidenceEvent"]] = relationship(
        "EvidenceEvent", back_populates="company"
    )


class Research(Base):
    __tablename__ = "research"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    funding_stage: Mapped[str] = mapped_column(String, nullable=True)
    headcount_estimate: Mapped[str] = mapped_column(String, nullable=True)
    tech_stack: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    hiring_manager_name: Mapped[str] = mapped_column(String, nullable=True)
    hiring_manager_linkedin: Mapped[str] = mapped_column(String, nullable=True)
    hiring_manager_email: Mapped[str] = mapped_column(String, nullable=True)
    hiring_manager_role: Mapped[str] = mapped_column(String, nullable=True)
    hiring_manager_provider_id: Mapped[str] = mapped_column(String, nullable=True)
    recent_news: Mapped[str] = mapped_column(Text, nullable=True)
    fit_reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    enriched_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    company: Mapped["Company"] = relationship(
        "Company", back_populates="research"
    )


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    channel: Mapped[str] = mapped_column(String, nullable=False)  # "linkedin" | "email"
    subject: Mapped[str] = mapped_column(String, nullable=True)
    draft_body: Mapped[str] = mapped_column(Text, nullable=False)
    final_body: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    conversation_id: Mapped[str] = mapped_column(String, nullable=True)
    approved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    replied_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    followup_draft: Mapped[str] = mapped_column(Text, nullable=True)
    followup_status: Mapped[str] = mapped_column(String, default="pending")
    company: Mapped["Company"] = relationship(
        "Company", back_populates="messages"
    )


class EvidenceEvent(Base):
    __tablename__ = "evidence_events"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    resource_name: Mapped[str] = mapped_column(String, nullable=False)
    artifact_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String, default="success", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    error_context: Mapped[dict] = mapped_column(JSONB, nullable=True)

    company: Mapped["Company"] = relationship(
        "Company", back_populates="evidence_events"
    )


class AgentLog(Base):
    __tablename__ = "agent_log"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )
    agent: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
