from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal, InvalidOperation

CENT = Decimal("0.01")
MAX_AMOUNT = Decimal("1000000000")


class SplitError(Exception):
    pass


@dataclass(frozen=True)
class Expense:
    description: str
    amount: Decimal
    payer: str
    participants: tuple


@dataclass(frozen=True)
class Transfer:
    sender: str
    receiver: str
    amount: Decimal


def to_money(value):
    text = str(value).strip()
    for symbol in "$€£₹ ":
        text = text.replace(symbol, "")
    if "," in text and "." not in text:
        head, _, tail = text.rpartition(",")
        text = head.replace(",", "") + (tail if len(tail) == 3 else "." + tail)
    else:
        text = text.replace(",", "")
    try:
        amount = Decimal(text)
    except InvalidOperation:
        raise SplitError("That is not a valid amount.") from None
    if not amount.is_finite():
        raise SplitError("That is not a valid amount.")
    if amount > MAX_AMOUNT:
        raise SplitError("That is a lot of money. Try a smaller amount.")
    amount = amount.quantize(CENT, rounding=ROUND_HALF_UP)
    if amount <= 0:
        raise SplitError("Amount must be more than zero.")
    return amount


def split_amount(amount, count, offset=0):
    if count < 1:
        raise SplitError("Pick at least one person.")
    base = (amount / count).quantize(CENT, rounding=ROUND_DOWN)
    extra = int((amount - base * count) / CENT)
    shares = [base] * count
    for step in range(extra):
        shares[(offset + step) % count] += CENT
    return shares


def format_money(amount, symbol="$"):
    return f"{symbol}{amount:,.2f}"


class Group:
    def __init__(self):
        self.members = []
        self.expenses = []

    def add_member(self, name):
        name = " ".join(name.split())
        if not name:
            raise SplitError("Type a name first.")
        if len(name) > 24:
            raise SplitError("Keep names under 24 characters.")
        if name.casefold() in {m.casefold() for m in self.members}:
            raise SplitError(f"{name} is already in the squad.")
        self.members.append(name)
        return name

    def remove_member(self, name):
        for expense in self.expenses:
            if name == expense.payer or name in expense.participants:
                raise SplitError(f"{name} is on a receipt. Delete it first.")
        self.members.remove(name)

    def add_expense(self, description, amount, payer, participants):
        description = " ".join(description.split())
        if not self.members:
            raise SplitError("Add your friends first.")
        if not description:
            raise SplitError("What was it for? Add a description.")
        money = to_money(amount)
        if payer not in self.members:
            raise SplitError("Pick who paid.")
        chosen = tuple(m for m in self.members if m in set(participants))
        if not chosen:
            raise SplitError("Pick at least one person to split with.")
        expense = Expense(description, money, payer, chosen)
        self.expenses.append(expense)
        return expense

    def remove_expense(self, index):
        del self.expenses[index]

    def total(self):
        return sum((e.amount for e in self.expenses), Decimal("0.00"))

    def balances(self):
        balances = {m: Decimal("0.00") for m in self.members}
        for index, expense in enumerate(self.expenses):
            balances[expense.payer] += expense.amount
            shares = split_amount(expense.amount, len(expense.participants), index)
            for person, share in zip(expense.participants, shares):
                balances[person] -= share
        return balances

    def settlements(self):
        balances = self.balances()
        creditors = [[n, b] for n, b in balances.items() if b > 0]
        debtors = [[n, -b] for n, b in balances.items() if b < 0]
        transfers = []
        while creditors and debtors:
            creditors.sort(key=lambda p: (-p[1], p[0]))
            debtors.sort(key=lambda p: (-p[1], p[0]))
            creditor, debtor = creditors[0], debtors[0]
            amount = min(creditor[1], debtor[1])
            transfers.append(Transfer(debtor[0], creditor[0], amount))
            creditor[1] -= amount
            debtor[1] -= amount
            if creditor[1] == 0:
                creditors.pop(0)
            if debtor[1] == 0:
                debtors.pop(0)
        return transfers

    def summary_text(self, symbol="$"):
        lines = ["💸 Splitzy recap", f"total spent: {format_money(self.total(), symbol)}"]
        transfers = self.settlements()
        if not transfers:
            lines.append("everyone is even. no cap ✅")
        for t in transfers:
            lines.append(f"{t.sender} ➜ {t.receiver}: {format_money(t.amount, symbol)}")
        return "\n".join(lines)
