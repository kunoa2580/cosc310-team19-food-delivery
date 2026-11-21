"""Expiring in-memory sessions; restarting the single server signs users out."""
from dataclasses import dataclass
import secrets
from threading import RLock
from time import time
from app.services.account_service import ACCOUNT_DEACTIVATED_MESSAGE, Forbidden, Unauthenticated

SESSION_SECONDS = 3600


@dataclass
class Session:
    account_id: int
    expires_at: float
    revoked_by_deactivation: bool = False


class SessionStore:
    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}
        self.lock = RLock()

    def create(self, account_id: int) -> tuple[str, Session]:
        with self.lock:
            now = time()
            self.sessions = {k: v for k, v in self.sessions.items() if v.expires_at > now}
            token = secrets.token_urlsafe(32)
            session = Session(account_id, now + SESSION_SECONDS)
            self.sessions[token] = session
            return token, session

    def get(self, token: str | None) -> Session:
        with self.lock:
            session = self.sessions.get(token or "")
            if session is None or session.expires_at <= time():
                self.sessions.pop(token or "", None)
                raise Unauthenticated("Sign in required")
            if session.revoked_by_deactivation:
                raise Forbidden(ACCOUNT_DEACTIVATED_MESSAGE)
            return session

    def revoke_for_deactivation(self, account_id: int) -> None:
        # Retain the reason until expiry so revoked tokens receive the right error.
        with self.lock:
            for session in self.sessions.values():
                if session.account_id == account_id:
                    session.revoked_by_deactivation = True

    def remove(self, token: str | None) -> None:
        with self.lock:
            self.sessions.pop(token or "", None)


sessions = SessionStore()

