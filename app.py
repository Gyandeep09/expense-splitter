import random

import customtkinter as ctk

from splitter import Group, SplitError, format_money

BG = "#0D0D12"
CARD = "#16161F"
CARD2 = "#1E1E2A"
BORDER = "#2A2A3A"
TEXT = "#F4F4F5"
MUTED = "#8E8EA3"
ACCENT = "#A855F7"
ACCENT_DARK = "#7E3FC2"
PINK = "#F472B6"
GREEN = "#34D399"
RED = "#FB7185"

ICONS = [
    ("pizza", "🍕"), ("burger", "🍔"), ("dinner", "🍽️"), ("lunch", "🥪"),
    ("food", "🍜"), ("coffee", "☕"), ("boba", "🧋"), ("beer", "🍺"),
    ("drink", "🍹"), ("uber", "🚕"), ("taxi", "🚕"), ("cab", "🚕"),
    ("gas", "⛽"), ("rent", "🏠"), ("movie", "🎬"), ("ticket", "🎟️"),
    ("grocer", "🛒"), ("flight", "✈️"), ("trip", "🧳"), ("hotel", "🏨"),
    ("game", "🎮"), ("party", "🎉"), ("gift", "🎁"), ("snack", "🍿"),
]

ROASTS = [
    "{n} is the main character of this debt arc 💀",
    "{n}, the group chat is watching 👀",
    "{n} said they would pay later. It is later 🫠",
    "{n} owes the most. Pay up, king 👑",
]


def icon_for(text):
    lowered = text.lower()
    for key, icon in ICONS:
        if key in lowered:
            return icon
    return "🧾"


def font(size, bold=False):
    return ctk.CTkFont(family="Segoe UI", size=size, weight="bold" if bold else "normal")


def clear(frame):
    for child in frame.winfo_children():
        child.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Splitzy")
        self.geometry("1120x740")
        self.minsize(980, 660)
        self.configure(fg_color=BG)

        self.group = Group()
        self.symbol = "$"
        self.picks = {}
        self.payer_var = ctk.StringVar(value="")
        self.message_job = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.build_sidebar()
        self.build_main()
        self.refresh_all()

    def build_sidebar(self):
        side = ctk.CTkFrame(self, fg_color="transparent", width=380)
        side.grid(row=0, column=0, sticky="ns", padx=(20, 10), pady=20)
        side.grid_propagate(False)

        head = ctk.CTkFrame(side, fg_color="transparent")
        head.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(head, text="Splitzy 💸", font=font(30, True), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(
            head, text="split bills, keep the friendship", font=font(13), text_color=MUTED
        ).pack(anchor="w")
        self.currency = ctk.CTkSegmentedButton(
            head, values=["$", "€", "£", "₹"], command=self.change_symbol,
            selected_color=ACCENT, selected_hover_color=ACCENT_DARK,
            unselected_color=CARD2, unselected_hover_color=BORDER, fg_color=CARD2,
        )
        self.currency.set("$")
        self.currency.pack(anchor="w", pady=(10, 0))

        squad = ctk.CTkFrame(side, fg_color=CARD, corner_radius=20)
        squad.pack(fill="both", expand=True, pady=(0, 12))
        squad_head = ctk.CTkFrame(squad, fg_color="transparent")
        squad_head.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(squad_head, text="👯 the squad", font=font(16, True), text_color=TEXT).pack(
            side="left"
        )
        ctk.CTkButton(
            squad_head, text="everyone's in", width=96, height=26, corner_radius=8,
            fg_color=CARD2, hover_color=BORDER, text_color=TEXT, command=self.toggle_all,
        ).pack(side="right")
        add_row = ctk.CTkFrame(squad, fg_color="transparent")
        add_row.pack(fill="x", padx=16)
        self.name_entry = ctk.CTkEntry(
            add_row, placeholder_text="add a friend", height=38, corner_radius=12,
            fg_color=CARD2, border_color=BORDER, text_color=TEXT,
        )
        self.name_entry.pack(side="left", fill="x", expand=True)
        self.name_entry.bind("<Return>", lambda event: self.add_member())
        ctk.CTkButton(
            add_row, text="➕", width=44, height=38, corner_radius=12,
            fg_color=ACCENT, hover_color=ACCENT_DARK, command=self.add_member,
        ).pack(side="left", padx=(8, 0))
        self.squad_list = ctk.CTkScrollableFrame(squad, fg_color="transparent")
        self.squad_list.pack(fill="both", expand=True, padx=8, pady=(6, 10))

        bill = ctk.CTkFrame(side, fg_color=CARD, corner_radius=20)
        bill.pack(side="bottom", fill="x", before=squad)
        ctk.CTkLabel(bill, text="🧾 new receipt", font=font(16, True), text_color=TEXT).pack(
            anchor="w", padx=16, pady=(14, 8)
        )
        self.desc_entry = ctk.CTkEntry(
            bill, placeholder_text="what was it? 🍕", height=38, corner_radius=12,
            fg_color=CARD2, border_color=BORDER, text_color=TEXT,
        )
        self.desc_entry.pack(fill="x", padx=16, pady=(0, 8))
        self.amount_entry = ctk.CTkEntry(
            bill, placeholder_text="how much? 💰", height=38, corner_radius=12,
            fg_color=CARD2, border_color=BORDER, text_color=TEXT,
        )
        self.amount_entry.pack(fill="x", padx=16, pady=(0, 8))
        self.desc_entry.bind("<Return>", lambda event: self.add_expense())
        self.amount_entry.bind("<Return>", lambda event: self.add_expense())

        pay_row = ctk.CTkFrame(bill, fg_color="transparent")
        pay_row.pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkLabel(pay_row, text="who paid 💳", font=font(13), text_color=MUTED).pack(side="left")
        self.payer_menu = ctk.CTkOptionMenu(
            pay_row, variable=self.payer_var, values=["add friends first"], height=32,
            corner_radius=10, fg_color=CARD2, button_color=ACCENT,
            button_hover_color=ACCENT_DARK, dropdown_fg_color=CARD2,
        )
        self.payer_menu.pack(side="right")

        self.message = ctk.CTkLabel(bill, text="", font=font(12), text_color=RED, wraplength=320)
        self.message.pack(padx=16, pady=(0, 4))
        ctk.CTkButton(
            bill, text="add it 🔥", height=42, corner_radius=14, font=font(15, True),
            fg_color=ACCENT, hover_color=ACCENT_DARK, command=self.add_expense,
        ).pack(fill="x", padx=16, pady=(4, 14))

    def build_main(self):
        self.tabs = ctk.CTkTabview(
            self, fg_color=CARD, corner_radius=24,
            segmented_button_fg_color=CARD2, segmented_button_selected_color=ACCENT,
            segmented_button_selected_hover_color=ACCENT_DARK,
            segmented_button_unselected_color=CARD2,
            segmented_button_unselected_hover_color=BORDER,
        )
        self.tabs.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        receipts_tab = self.tabs.add("🧾 Receipts")
        settle_tab = self.tabs.add("💸 Settle up")
        self.receipts = ctk.CTkScrollableFrame(receipts_tab, fg_color="transparent")
        self.receipts.pack(fill="both", expand=True)
        self.settle = ctk.CTkScrollableFrame(settle_tab, fg_color="transparent")
        self.settle.pack(fill="both", expand=True)

    def say(self, text, ok=False):
        self.message.configure(text=text, text_color=GREEN if ok else RED)
        if self.message_job:
            self.after_cancel(self.message_job)
        self.message_job = self.after(4500, lambda: self.message.configure(text=""))

    def change_symbol(self, value):
        self.symbol = value
        self.refresh_receipts()
        self.refresh_settle()

    def add_member(self):
        try:
            name = self.group.add_member(self.name_entry.get())
        except SplitError as error:
            self.say(str(error))
            return
        self.name_entry.delete(0, "end")
        self.picks[name] = ctk.BooleanVar(value=True)
        self.refresh_all()
        self.say(f"{name} joined the squad 🎉", ok=True)

    def remove_member(self, name):
        try:
            self.group.remove_member(name)
        except SplitError as error:
            self.say(str(error))
            return
        self.picks.pop(name, None)
        self.refresh_all()

    def toggle_all(self):
        turn_on = not all(var.get() for var in self.picks.values())
        for var in self.picks.values():
            var.set(turn_on)

    def add_expense(self):
        chosen = [name for name, var in self.picks.items() if var.get()]
        try:
            expense = self.group.add_expense(
                self.desc_entry.get(), self.amount_entry.get(), self.payer_var.get(), chosen
            )
        except SplitError as error:
            self.say(str(error))
            return
        self.desc_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.refresh_receipts()
        self.refresh_settle()
        self.say(f"{icon_for(expense.description)} logged. {expense.payer} is carrying 🫡", ok=True)

    def delete_expense(self, index):
        self.group.remove_expense(index)
        self.refresh_receipts()
        self.refresh_settle()

    def refresh_all(self):
        self.refresh_squad()
        self.refresh_form()
        self.refresh_receipts()
        self.refresh_settle()

    def refresh_squad(self):
        clear(self.squad_list)
        if not self.group.members:
            ctk.CTkLabel(
                self.squad_list, text="nobody here yet.\nadd your friends 👀",
                font=font(12), text_color=MUTED,
            ).pack(pady=14)
            return
        for name in self.group.members:
            row = ctk.CTkFrame(self.squad_list, fg_color=CARD2, corner_radius=12)
            row.pack(fill="x", pady=2)
            ctk.CTkCheckBox(
                row, text=name, variable=self.picks[name], font=font(13), text_color=TEXT,
                fg_color=ACCENT, hover_color=ACCENT_DARK, border_color=MUTED, corner_radius=6,
            ).pack(side="left", padx=12, pady=8)
            ctk.CTkButton(
                row, text="✖", width=28, height=28, corner_radius=8, fg_color="transparent",
                hover_color=BORDER, text_color=MUTED, command=lambda n=name: self.remove_member(n),
            ).pack(side="right", padx=6)

    def refresh_form(self):
        members = self.group.members
        self.payer_menu.configure(values=members or ["add friends first"])
        if self.payer_var.get() not in members:
            self.payer_var.set(members[0] if members else "add friends first")

    def refresh_receipts(self):
        clear(self.receipts)
        if not self.group.expenses:
            ctk.CTkLabel(
                self.receipts, text="🫥\nno receipts yet\nyour wallet is safe, for now",
                font=font(16), text_color=MUTED, justify="center",
            ).pack(pady=80)
            return
        for index in range(len(self.group.expenses) - 1, -1, -1):
            expense = self.group.expenses[index]
            ways = len(expense.participants)
            card = ctk.CTkFrame(self.receipts, fg_color=CARD2, corner_radius=16)
            card.pack(fill="x", pady=4, padx=4)
            card.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(card, text=icon_for(expense.description), font=font(28)).grid(
                row=0, column=0, rowspan=2, padx=16, pady=12
            )
            ctk.CTkLabel(
                card, text=expense.description, font=font(15, True), text_color=TEXT, anchor="w"
            ).grid(row=0, column=1, sticky="w", pady=(12, 0))
            ctk.CTkLabel(
                card, text=f"{expense.payer} paid · split {ways} way{'s' if ways != 1 else ''}",
                font=font(12), text_color=MUTED, anchor="w",
            ).grid(row=1, column=1, sticky="w", pady=(0, 12))
            ctk.CTkLabel(
                card, text=format_money(expense.amount, self.symbol), font=font(17, True),
                text_color=PINK,
            ).grid(row=0, column=2, rowspan=2, padx=8)
            ctk.CTkButton(
                card, text="🗑", width=36, height=36, corner_radius=10, fg_color="transparent",
                hover_color=BORDER, command=lambda i=index: self.delete_expense(i),
            ).grid(row=0, column=3, rowspan=2, padx=(0, 12))

    def stat_card(self, parent, column, value, label):
        card = ctk.CTkFrame(parent, fg_color=CARD2, corner_radius=16)
        card.grid(row=0, column=column, sticky="ew", padx=4)
        ctk.CTkLabel(card, text=value, font=font(20, True), text_color=TEXT).pack(pady=(12, 0))
        ctk.CTkLabel(card, text=label, font=font(12), text_color=MUTED).pack(pady=(0, 12))

    def section_title(self, text):
        ctk.CTkLabel(self.settle, text=text, font=font(16, True), text_color=TEXT, anchor="w").pack(
            fill="x", padx=8, pady=(16, 6)
        )

    def refresh_settle(self):
        clear(self.settle)
        group = self.group
        stats = ctk.CTkFrame(self.settle, fg_color="transparent")
        stats.pack(fill="x")
        for column in range(3):
            stats.grid_columnconfigure(column, weight=1, uniform="stat")
        self.stat_card(stats, 0, format_money(group.total(), self.symbol), "total spent 💰")
        self.stat_card(stats, 1, str(len(group.expenses)), "receipts 🧾")
        self.stat_card(stats, 2, str(len(group.members)), "in the squad 👯")

        balances = group.balances()
        transfers = group.settlements()

        if not group.expenses:
            caption = "add a receipt and the math happens for you 🧠"
        elif not transfers:
            caption = "everyone is even. no cap, that is rare ✅"
        else:
            worst = min(balances, key=lambda name: balances[name])
            caption = random.choice(ROASTS).format(n=worst)
        ctk.CTkLabel(self.settle, text=caption, font=font(13), text_color=MUTED).pack(pady=(14, 0))

        self.section_title("💸 who pays who")
        if not transfers:
            ctk.CTkLabel(
                self.settle, text="nothing to settle 🎉", font=font(13), text_color=MUTED
            ).pack(pady=8)
        for transfer in transfers:
            row = ctk.CTkFrame(self.settle, fg_color=CARD2, corner_radius=16)
            row.pack(fill="x", pady=4, padx=4)
            ctk.CTkLabel(row, text=transfer.sender, font=font(15, True), text_color=RED).pack(
                side="left", padx=(16, 8), pady=14
            )
            ctk.CTkLabel(row, text="➜", font=font(15, True), text_color=ACCENT).pack(side="left")
            ctk.CTkLabel(row, text=transfer.receiver, font=font(15, True), text_color=GREEN).pack(
                side="left", padx=8
            )
            ctk.CTkLabel(
                row, text=format_money(transfer.amount, self.symbol), font=font(16, True),
                text_color=TEXT,
            ).pack(side="right", padx=16)

        self.section_title("📊 the vibes")
        for name in group.members:
            balance = balances[name]
            if balance > 0:
                text, color = f"gets back {format_money(balance, self.symbol)} 🤑", GREEN
            elif balance < 0:
                text, color = f"owes {format_money(-balance, self.symbol)} 💀", RED
            else:
                text, color = "all good ✅", MUTED
            row = ctk.CTkFrame(self.settle, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(row, text=f"😎  {name}", font=font(14), text_color=TEXT).pack(side="left")
            ctk.CTkLabel(row, text=text, font=font(13, True), text_color=color).pack(side="right")

        ctk.CTkButton(
            self.settle, text="📋 copy for the group chat", height=42, corner_radius=14,
            font=font(14, True), fg_color=ACCENT, hover_color=ACCENT_DARK, command=self.copy_summary,
        ).pack(fill="x", padx=4, pady=20)

    def copy_summary(self):
        self.clipboard_clear()
        self.clipboard_append(self.group.summary_text(self.symbol))
        self.say("copied. go post it in the group chat 📲", ok=True)


if __name__ == "__main__":
    App().mainloop()
