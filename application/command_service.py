from domain.aggregate import BankAccount
from infrastructure.event_store import EventStore

class AccountCommandService:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def create_account(self, account_id: str, owner: str) -> BankAccount:
        account = BankAccount(account_id)
        account.create(owner)
        self.event_store.append(account_id, account.changes)
        return account

    def deposit_money(self, account_id: str, amount: float) -> BankAccount:
        # 1. Traer historial del EventStore
        history = self.event_store.get_events_for(account_id)
        # 2. Reconstruir el Aggregate (Rehidratación)
        account = BankAccount.rehydrate(account_id, history)
        # 3. Ejecutar comando de negocio
        account.deposit(amount)
        # 4. Guardar únicamente los nuevos eventos
        self.event_store.append(account_id, account.changes)
        return account

    def withdraw_money(self, account_id: str, amount: float) -> BankAccount:
        history = self.event_store.get_events_for(account_id)
        account = BankAccount.rehydrate(account_id, history)
        account.withdraw(amount)
        self.event_store.append(account_id, account.changes)
        return account