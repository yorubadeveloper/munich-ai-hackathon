from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import UserProfile

router = APIRouter()


class ProfileIn(BaseModel):
    name: str
    role: str
    stack: list[str]
    location: str
    dealbreakers: list[str] = []
    bio: str = ""
    linkedin_url: str = ""
    email: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    projects: str = ""
    target_industries: list[str] = []
    target_funding_stages: list[str] = []
    company_size: str = ""
    remote_pref: str = ""
    seniority: str = ""


@router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        return None
    return {
        "name": profile.name,
        "role": profile.role,
        "stack": profile.stack,
        "location": profile.location,
        "dealbreakers": profile.dealbreakers,
        "bio": profile.bio,
        "linkedin_url": profile.linkedin_url,
        "email": profile.email,
        "github_url": profile.github_url,
        "portfolio_url": profile.portfolio_url,
        "projects": profile.projects,
        "target_industries": profile.target_industries,
        "target_funding_stages": profile.target_funding_stages,
        "company_size": profile.company_size,
        "remote_pref": profile.remote_pref,
        "seniority": profile.seniority,
    }


@router.post("/profile")
async def save_profile(data: ProfileIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).limit(1))
    existing = result.scalar_one_or_none()
    if existing:
        existing.name = data.name
        existing.role = data.role
        existing.stack = data.stack
        existing.location = data.location
        existing.dealbreakers = data.dealbreakers
        existing.bio = data.bio
        existing.linkedin_url = data.linkedin_url
        existing.email = data.email
        existing.github_url = data.github_url
        existing.portfolio_url = data.portfolio_url
        existing.projects = data.projects
        existing.target_industries = data.target_industries
        existing.target_funding_stages = data.target_funding_stages
        existing.company_size = data.company_size
        existing.remote_pref = data.remote_pref
        existing.seniority = data.seniority
    else:
        profile = UserProfile(**data.model_dump())
        db.add(profile)
    await db.commit()
    return {"status": "saved"}
