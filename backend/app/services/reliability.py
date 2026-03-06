from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CircuitBreaker:
    failure_threshold: int
    reset_seconds: int
    failures: int = 0
    opened_at: datetime | None = None

    def allow_request(self) -> bool:
        if self.opened_at is None:
            return True
        if datetime.utcnow() - self.opened_at > timedelta(seconds=self.reset_seconds):
            self.failures = 0
            self.opened_at = None
            return True
        return False

    def on_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def on_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = datetime.utcnow()
