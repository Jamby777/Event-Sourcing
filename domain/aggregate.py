from typing import List
from domain.events import Event, AccountCreated, MoneyDeposited, MoneyWithdrawn
from domain.exceptions import InsufficientFundsError, InvalidAmountError

class BankAccount:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.owner: str = ""
        self.balance: float = 0.0
        self.changes: List[Event] = []  # Eventos no guardados aún en la base de datos

    def apply(self, event: Event) -> None:
        """Muestra cómo cambia el estado interno al reaccionar a un evento."""
        if isinstance(event, AccountCreated):
            self.owner = event.owner
            self.balance = 0.0
        elif isinstance(event, MoneyDeposited):
            self.balance += event.amount
        elif isinstance(event, MoneyWithdrawn):
            self.balance -= event.amount

    def create(self, owner: str) -> None:
        event = AccountCreated(account_id=self.account_id, owner=owner)
        self.apply(event)
        self.changes.append(event)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError("El depósito debe ser mayor a cero.")
        event = MoneyDeposited(account_id=self.account_id, amount=amount)
        self.apply(event)
        self.changes.append(event)

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError("El retiro debe ser mayor a cero.")
        if amount > self.balance:
            raise InsufficientFundsError(f"Fondos insuficientes. Saldo actual: ${self.balance}")
        
        event = MoneyWithdrawn(account_id=self.account_id, amount=amount)
        self.apply(event)
        self.changes.append(event)

    @classmethod
    def rehydrate(cls, account_id: str, history: List[Event]) -> "BankAccount":
        """Reconstruye el estado del objeto leyendo todo su historial de eventos."""
        account = cls(account_id)
        for event in history:
            account.apply(event)
        return account