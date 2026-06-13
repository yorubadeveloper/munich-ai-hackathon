from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from models import UserProfile
from database import get_db

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
    else:
        profile = UserProfile(**data.model_dump())
        db.add(profile)
    await db.commit()
    return {"status": "saved"}
