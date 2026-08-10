"""Per-list session cookie: identity is a cookie whose *name* is scoped to
the list id, so sessions on different lists are independent by construction
(see design.md - Identity).
"""

from fastapi import Request, Response

from app.state import new_session_id, store

COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


def cookie_name(list_id: str) -> str:
    return f"colist_session_{list_id}"


def get_or_create_session(list_id: str, request: Request, response: Response) -> str:
    name = cookie_name(list_id)
    session_id = request.cookies.get(name)
    if not session_id:
        session_id = new_session_id()
        response.set_cookie(
            key=name,
            value=session_id,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
            secure=request.url.scheme == "https",
        )
    store.get(list_id).color_for(session_id)
    return session_id
