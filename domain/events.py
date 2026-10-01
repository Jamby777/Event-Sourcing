from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class Event:
    pass

@dataclass(frozen=True)
class AccountCreated(Event):
    account_id: str
    owner: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass(frozen=True)
class MoneyDeposited(Event):
    account_id: str
    amount: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass(frozen=True)
class MoneyWithdrawn(Event):
    account_id: str
    amount: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())