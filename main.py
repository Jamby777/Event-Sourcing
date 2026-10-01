import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

# Registrar la raíz para importaciones
sys.path.append(str(Path(__file__).parent))

from infrastructure.event_store import EventStore
from application.command_service import AccountCommandService
from domain.exceptions import InsufficientFundsError, InvalidAmountError

class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Event Sourcing Bank")
        self.root.geometry("450x500")

        self.event_store = EventStore()
        self.service = AccountCommandService(self.event_store)
        self.account_id = "CTA-1001"

        self._build_ui()
        self._refresh_ui()

    def _build_ui(self):
        # Frame de Saldo
        frame_saldo = tk.Frame(self.root, pady=10)
        frame_saldo.pack()
        
        tk.Label(frame_saldo, text="Cuenta: CTA-1001", font=("Arial", 12, "bold")).pack()
        self.lbl_owner = tk.Label(frame_saldo, text="Titular: Sin crear", font=("Arial", 10))
        self.lbl_owner.pack()
        self.lbl_balance = tk.Label(frame_saldo, text="Saldo: $0.0", font=("Arial", 16, "bold"), fg="green")
        self.lbl_balance.pack()

        # Frame Formulario
        frame_form = tk.LabelFrame(self.root, text=" Operaciones ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_form, text="Titular (creación):").grid(row=0, column=0, sticky="w")
        self.ent_owner = tk.Entry(frame_form)
        self.ent_owner.insert(0, "Hector")
        self.ent_owner.grid(row=0, column=1, pady=2)

        btn_create = tk.Button(frame_form, text="Crear Cuenta", command=self.create_account)
        btn_create.grid(row=0, column=2, padx=5, pady=2)

        tk.Label(frame_form, text="Monto ($):").grid(row=1, column=0, sticky="w")
        self.ent_amount = tk.Entry(frame_form)
        self.ent_amount.grid(row=1, column=1, pady=2)

        btn_deposit = tk.Button(frame_form, text="Depositar", bg="#d4edda", command=self.deposit)
        btn_deposit.grid(row=1, column=2, padx=5, pady=2)

        btn_withdraw = tk.Button(frame_form, text="Retirar", bg="#f8d7da", command=self.withdraw)
        btn_withdraw.grid(row=2, column=2, padx=5, pady=2)

        # Frame Historial de Eventos
        frame_history = tk.LabelFrame(self.root, text=" Historial del Event Store (SQLite) ", padx=5, pady=5)
        frame_history.pack(fill="both", expand=True, padx=15, pady=10)

        self.txt_events = tk.Text(frame_history, height=10, state="disabled", font=("Consolas", 9))
        self.txt_events.pack(fill="both", expand=True)

    def _refresh_ui(self):
        history = self.event_store.get_events_for(self.account_id)
        
        # Si la cuenta no existe aún, salir
        if not history:
            return

        # Reconstruir estado actual a partir de eventos
        from domain.aggregate import BankAccount
        account = BankAccount.rehydrate(self.account_id, history)

        self.lbl_owner.config(text=f"Titular: {account.owner}")
        self.lbl_balance.config(text=f"Saldo: ${account.balance:.2f}")

        # Renderizar lista de eventos
        self.txt_events.config(state="normal")
        self.txt_events.delete("1.0", tk.END)
        for idx, ev in enumerate(history, 1):
            name = ev.__class__.__name__
            details = f"{ev.owner}" if hasattr(ev, 'owner') else f"${ev.amount}"
            self.txt_events.insert(tk.END, f"{idx}. {name} -> {details}\n")
        self.txt_events.config(state="disabled")

    def create_account(self):
        owner = self.ent_owner.get().strip()
        if not owner:
            messagebox.showwarning("Atención", "Escribe un nombre de titular")
            return
        self.service.create_account(self.account_id, owner)
        self._refresh_ui()

    def deposit(self):
        try:
            amount = float(self.ent_amount.get())
            self.service.deposit_money(self.account_id, amount)
            self._refresh_ui()
            self.ent_amount.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido")
        except InvalidAmountError as e:
            messagebox.showwarning("Regla de Negocio", str(e))

    def withdraw(self):
        try:
            amount = float(self.ent_amount.get())
            self.service.withdraw_money(self.account_id, amount)
            self._refresh_ui()
            self.ent_amount.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido")
        except (InsufficientFundsError, InvalidAmountError) as e:
            messagebox.showwarning("Regla de Negocio", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()