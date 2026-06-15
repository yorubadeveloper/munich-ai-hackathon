import asyncio
import os
import sys
import uuid
from datetime import datetime

# Adjust sys.path so we can import from backend root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from database import AsyncSessionLocal, init_db


async def seed_company(
    session, id: uuid.UUID, name: str, website: str, job_url: str, status: str, fit_score: float
) -> models.Company:
    company = await session.get(models.Company, id)
    if company:
        company.name = name
        company.website = website
        company.job_url = job_url
        company.status = status
        company.fit_score = fit_score
    else:
        company = models.Company(
            id=id,
            name=name,
            website=website,
            job_url=job_url,
            status=status,
            fit_score=fit_score,
            discovered_at=datetime.utcnow(),
        )
        session.add(company)
    await session.commit()
    return company


async def seed_research(
    session,
    company_id: uuid.UUID,
    id: uuid.UUID,
    funding_stage: str,
    headcount_estimate: str,
    tech_stack: list[str],
    hiring_manager_name: str,
    hiring_manager_role: str,
    hiring_manager_linkedin: str,
    hiring_manager_email: str,
    fit_reasoning: str,
) -> models.Research:
    research = await session.get(models.Research, id)
    if research:
        research.company_id = company_id
        research.funding_stage = funding_stage
        research.headcount_estimate = headcount_estimate
        research.tech_stack = tech_stack
        research.hiring_manager_name = hiring_manager_name
        research.hiring_manager_role = hiring_manager_role
        research.hiring_manager_linkedin = hiring_manager_linkedin
        research.hiring_manager_email = hiring_manager_email
        research.fit_reasoning = fit_reasoning
    else:
        research = models.Research(
            id=id,
            company_id=company_id,
            funding_stage=funding_stage,
            headcount_estimate=headcount_estimate,
            tech_stack=tech_stack,
            hiring_manager_name=hiring_manager_name,
            hiring_manager_role=hiring_manager_role,
            hiring_manager_linkedin=hiring_manager_linkedin,
            hiring_manager_email=hiring_manager_email,
            fit_reasoning=fit_reasoning,
            enriched_at=datetime.utcnow(),
        )
        session.add(research)
    await session.commit()
    return research


async def seed_evidence_event(
    session,
    id: uuid.UUID,
    company_id: uuid.UUID,
    resource_name: str,
    artifact_type: str,
    payload: dict,
    status: str = "success",
    error_context: dict = None,
) -> models.EvidenceEvent:
    event = await session.get(models.EvidenceEvent, id)
    if event:
        event.company_id = company_id
        event.resource_name = resource_name
        event.artifact_type = artifact_type
        event.payload = payload
        event.status = status
        event.error_context = error_context
    else:
        event = models.EvidenceEvent(
            id=id,
            company_id=company_id,
            resource_name=resource_name,
            artifact_type=artifact_type,
            payload=payload,
            status=status,
            error_context=error_context,
            timestamp=datetime.utcnow(),
        )
        session.add(event)
    await session.commit()
    return event


async def seed_message(
    session, id: uuid.UUID, company_id: uuid.UUID, channel: str, subject: str, draft_body: str, status: str = "pending"
) -> models.Message:
    message = await session.get(models.Message, id)
    if message:
        message.company_id = company_id
        message.channel = channel
        message.subject = subject
        message.draft_body = draft_body
        message.status = status
    else:
        message = models.Message(
            id=id, company_id=company_id, channel=channel, subject=subject, draft_body=draft_body, status=status
        )
        session.add(message)
    await session.commit()
    return message


async def main():
    # Make sure tables are created
    print("Initializing database tables...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Aetheria AI (Golden Path)
        aetheria_id = uuid.uuid5(uuid.NAMESPACE_URL, "https://aetheria-ai.com")
        print(f"Seeding Aetheria AI (ID: {aetheria_id})...")

        await seed_company(
            session=session,
            id=aetheria_id,
            name="Aetheria AI",
            website="https://aetheria-ai.com",
            job_url="https://aetheria-ai.com/jobs/senior-python-engineer",
            status="approved",
            fit_score=0.92,
        )

        research_id_aetheria = uuid.uuid5(aetheria_id, "research")
        await seed_research(
            session=session,
            company_id=aetheria_id,
            id=research_id_aetheria,
            funding_stage="Series A",
            headcount_estimate="10-50",
            tech_stack=["Python", "FastAPI", "PostgreSQL", "Next.js", "React", "Gemini"],
            hiring_manager_name="Elena Vance",
            hiring_manager_role="VP of Engineering",
            hiring_manager_linkedin="https://linkedin.com/in/elena-vance-mock",
            hiring_manager_email="elena.vance@aetheria-ai.com",
            fit_reasoning="Aetheria AI is building next-generation multi-agent autonomous developer workflows, completely aligned with the candidate's expertise in FastAPI, PostgreSQL, and LLM integrations. They are expanding their backend team and looking for a Senior Agentic Engineer.",
        )

        # EvidenceEvents for Aetheria AI
        evidence_events_aetheria = [
            (
                "Tavily",
                "source",
                {
                    "urls": ["https://aetheria-ai.com", "https://aetheria-ai.com/about"],
                    "snippet": "Aetheria AI is building next-generation agentic developer platforms. Based in Munich, Series A funding.",
                },
            ),
            (
                "Pioneer",
                "entity_extraction",
                {
                    "entities": {
                        "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Next.js", "React", "Gemini"],
                        "headcount": "10-50",
                    },
                    "labels": ["Tech Stack", "Growth", "Culture"],
                },
            ),
            (
                "Gemini",
                "reasoning",
                {
                    "reasoning": "Strong match because of direct alignment between FastAPI backend agent experience and Aetheria's agentic framework. Highly relevant Series A growth stage.",
                    "score": 0.92,
                    "labels": ["Leadership", "Funding"],
                },
            ),
            (
                "Telegram",
                "approval_state",
                {
                    "approved": True,
                    "comment": "Aetheria AI matches your FastAPI agent profile perfectly! Approved by user.",
                },
            ),
            (
                "fal",
                "visual_artifact",
                {
                    "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=60",
                    "prompt": "Futuristic AI agents collaborating to build software, modern tech aesthetic, synthwave style",
                },
            ),
        ]

        for i, (resource, artifact, payload) in enumerate(evidence_events_aetheria):
            event_id = uuid.uuid5(aetheria_id, f"evidence_{resource}_{artifact}_{i}")
            await seed_evidence_event(
                session=session,
                id=event_id,
                company_id=aetheria_id,
                resource_name=resource,
                artifact_type=artifact,
                payload=payload,
            )

        message_id_aetheria = uuid.uuid5(aetheria_id, "message")
        await seed_message(
            session=session,
            id=message_id_aetheria,
            company_id=aetheria_id,
            channel="linkedin",
            subject=None,
            draft_body="Hi Elena, I saw Aetheria AI is scaling its backend team with FastAPI and Agentic workflows. I'm building GSD-based multi-agent systems and would love to chat about how my experience aligns with your VP of Engineering goals!",
            status="approved",
        )

        # 2. Nebula Robotics (Partial Failure/Error state)
        nebula_id = uuid.uuid5(uuid.NAMESPACE_URL, "https://nebularobotics.com")
        print(f"Seeding Nebula Robotics (ID: {nebula_id})...")

        await seed_company(
            session=session,
            id=nebula_id,
            name="Nebula Robotics",
            website="https://nebularobotics.com",
            job_url="https://nebularobotics.com/careers/robotics-software-engineer",
            status="researched",
            fit_score=0.65,
        )

        research_id_nebula = uuid.uuid5(nebula_id, "research")
        await seed_research(
            session=session,
            company_id=nebula_id,
            id=research_id_nebula,
            funding_stage="Seed",
            headcount_estimate="1-10",
            tech_stack=["Python", "C++", "ROS2", "PyTorch"],
            hiring_manager_name="Marcus Vance",
            hiring_manager_role="Co-Founder & CTO",
            hiring_manager_linkedin="https://linkedin.com/in/marcus-vance-mock",
            hiring_manager_email="marcus@nebularobotics.com",
            fit_reasoning="Nebula Robotics is focusing on autonomous physical robot coordination. While they use Python, their core stack is heavily ROS2 and C++ which is a partial fit but not a direct match for the candidate's core web agent skill set.",
        )

        # fal visual_artifact event with status='error' and error_context
        fal_event_id_nebula = uuid.uuid5(nebula_id, "evidence_fal_visual_artifact_error")
        await seed_evidence_event(
            session=session,
            id=fal_event_id_nebula,
            company_id=nebula_id,
            resource_name="fal",
            artifact_type="visual_artifact",
            payload={},
            status="error",
            error_context={"code": "timeout", "message": "fal API timed out after 30s"},
        )

        print("\nSeeding completed successfully!")
        print("Summary of Seeded Data:")
        print("- Company Aetheria AI (approved, fit_score: 0.92)")
        print(
            f"  └─ Research: Series A, VP of Engineering, tech_stack: {['Python', 'FastAPI', 'PostgreSQL', 'Next.js', 'React', 'Gemini']}"
        )
        print("  └─ EvidenceEvents: Tavily, Pioneer, Gemini, Telegram (approved), fal (success)")
        print("  └─ Message: LinkedIn message (approved)")
        print("- Company Nebula Robotics (researched, fit_score: 0.65)")
        print(f"  └─ Research: Seed, Co-Founder & CTO, tech_stack: {['Python', 'C++', 'ROS2', 'PyTorch']}")
        print("  └─ EvidenceEvent: fal (error: timeout)")


if __name__ == "__main__":
    asyncio.run(main())
