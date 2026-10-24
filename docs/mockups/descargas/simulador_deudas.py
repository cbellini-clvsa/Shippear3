"""
Simulador de deudas: método avalancha vs. bola de nieve.

Portado del zip "Asesoría financiera para principiantes" (traducción directa de lib/debt.ts).
Solo usa la librería estándar de Python (3.9 o superior), no hay que instalar nada.

Doble uso en finanzas-app:
  - Descargable para el usuario (lo enlaza el prototipo docs/mockups/simulador-deudas.html).
  - Referencia de la lógica para el futuro backend: en la app Django se convierte en un
    servicio de la app `herramientas` o en un comando de management (misma función).

Cómo ejecutarlo:
    python simulador_deudas.py
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Literal

Method = Literal["avalanche", "snowball"]

# Tope de seguridad: evita un bucle infinito si el pago no alcanza ni para los intereses.
MAX_MONTHS = 600

# Por debajo de este saldo la deuda se considera saldada (evita restos de centavos).
PAYOFF_THRESHOLD = 0.5


@dataclass
class Debt:
    id: str
    name: str
    balance: float  # saldo actual
    annual_rate: float  # tasa anual en porcentaje, por ejemplo 45 = 45 %
    min_payment: float  # pago mínimo mensual


@dataclass
class Payoff:
    id: str
    name: str
    month: int  # mes en el que se terminó de pagar


@dataclass
class Simulation:
    months: int
    total_interest: float
    total_paid: float
    payoffs: list[Payoff] = field(default_factory=list)
    completed: bool = True  # False si llegó al tope de MAX_MONTHS sin saldar todo


def simulate_debts(debts: list[Debt], extra: float, method: Method) -> Simulation:
    """
    Simula mes a mes el pago de todas las deudas.

    Cada mes:
      1. Se suman los intereses a cada deuda.
      2. Se paga el mínimo de cada una (sin pasarse del presupuesto del mes).
      3. El dinero que sobra (el "extra") va a la deuda objetivo:
           - avalanche: la de mayor tasa de interés.
           - snowball:  la de menor saldo.
      4. Se registra qué deudas quedaron saldadas.

    El presupuesto mensual es constante: suma de mínimos + extra. Cuando una deuda
    se salda, su mínimo "rueda" automáticamente hacia las demás.
    """
    # Copias para no modificar la lista original que recibe la función.
    active = [replace(debt) for debt in debts if debt.balance > 0]

    monthly_budget = sum(debt.min_payment for debt in active) + max(0, extra)

    payoffs: list[Payoff] = []
    total_interest = 0.0
    total_paid = 0.0
    month = 0

    if not active:
        return Simulation(
            months=0,
            total_interest=0.0,
            total_paid=0.0,
            payoffs=payoffs,
            completed=True,
        )

    while any(d.balance > PAYOFF_THRESHOLD for d in active) and month < MAX_MONTHS:
        month += 1
        budget = monthly_budget

        # 1) Intereses del mes
        for debt in active:
            if debt.balance <= 0:
                continue
            interest = debt.balance * (debt.annual_rate / 100 / 12)
            debt.balance += interest
            total_interest += interest

        # 2) Pagos mínimos
        for debt in active:
            if debt.balance <= 0:
                continue
            payment = min(debt.balance, debt.min_payment, budget)
            debt.balance -= payment
            budget -= payment
            total_paid += payment

        # 3) El dinero extra va a la deuda objetivo según el método
        targets = [d for d in active if d.balance > PAYOFF_THRESHOLD]
        if method == "avalanche":
            targets.sort(key=lambda d: d.annual_rate, reverse=True)
        else:
            targets.sort(key=lambda d: d.balance)

        for debt in targets:
            if budget <= 0:
                break
            payment = min(debt.balance, budget)
            debt.balance -= payment
            budget -= payment
            total_paid += payment

        # 4) Registrar las deudas que se terminaron de pagar este mes
        already_paid = {p.id for p in payoffs}
        for debt in active:
            if debt.balance <= PAYOFF_THRESHOLD and debt.id not in already_paid:
                debt.balance = 0
                payoffs.append(Payoff(id=debt.id, name=debt.name, month=month))

    return Simulation(
        months=month,
        total_interest=total_interest,
        total_paid=total_paid,
        payoffs=payoffs,
        completed=month < MAX_MONTHS,
    )


def format_months(months: int) -> str:
    """Convierte una cantidad de meses en texto: 14 -> '1 año y 2 meses'."""
    if months <= 0:
        return "0 meses"

    years, rest = divmod(months, 12)
    parts: list[str] = []
    if years > 0:
        parts.append(f"{years} {'año' if years == 1 else 'años'}")
    if rest > 0:
        parts.append(f"{rest} {'mes' if rest == 1 else 'meses'}")
    return " y ".join(parts)


def print_simulation(title: str, sim: Simulation) -> None:
    print(f"\n=== {title} ===")
    print(f"Tiempo total:      {format_months(sim.months)}")
    print(f"Intereses totales: ${sim.total_interest:,.2f}")
    print(f"Total pagado:      ${sim.total_paid:,.2f}")
    if not sim.completed:
        print("Atención: con este pago no se llega a saldar todo en 50 años.")
    print("Orden de cancelación:")
    for payoff in sim.payoffs:
        print(f"  - {payoff.name}: mes {payoff.month} ({format_months(payoff.month)})")


if __name__ == "__main__":
    mis_deudas = [
        Debt("tarjeta", "Tarjeta de crédito", balance=450000, annual_rate=120, min_payment=45000),
        Debt("prestamo", "Préstamo personal", balance=800000, annual_rate=75, min_payment=60000),
        Debt("celular", "Cuotas del celular", balance=150000, annual_rate=0, min_payment=25000),
    ]
    pago_extra = 50000

    avalancha = simulate_debts(mis_deudas, pago_extra, "avalanche")
    bola_de_nieve = simulate_debts(mis_deudas, pago_extra, "snowball")

    print_simulation("Método avalancha (mayor tasa primero)", avalancha)
    print_simulation("Método bola de nieve (menor saldo primero)", bola_de_nieve)

    ahorro = bola_de_nieve.total_interest - avalancha.total_interest
    print(f"\nDiferencia en intereses (nieve - avalancha): ${ahorro:,.2f}")
