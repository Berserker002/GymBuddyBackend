"""Helper utilities for working with persisted users."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


def resolve_user_id(token: str) -> uuid.UUID:
    """Create a stable, deterministic UUID for a bearer token.

    This keeps the demo environment functioning until JWT verification is
    replaced with real Supabase or custom auth integration.
    """

    return uuid.uuid5(uuid.NAMESPACE_DNS, token)


async def ensure_user(db: AsyncSession, token: str) -> User:
    """Fetch or create a User record for the provided token."""

    user_id = resolve_user_id(token)
    user = await db.get(User, user_id)
    if user:
        return user

    user = User(id=user_id, email=f"{token[:8]}@example.com")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
