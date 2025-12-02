from fastapi import Depends, Header, HTTPException, status


async def verify_jwt(authorization: str = Header(...)) -> str:
    """Simple JWT placeholder for future Supabase/custom validation.

    For now, ensure a Bearer token is present. Replace with real JWT checks once
    the frontend integration is ready.
    """

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
        )
    return token
