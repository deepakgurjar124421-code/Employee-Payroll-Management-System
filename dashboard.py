"""
dashboard.py — Dashboard overview tab.
"""

import tkinter as tk
from styles import C, F, make_card, section_label, separator
import database as db
from datetime import datetime


class DashboardTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["bg_dark"])
        self._build()

    # ── Build ─────────────────────────────────
    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(hdr, text="Dashboard Overview", bg=C["bg_dark"],
                 fg=C["text_prim"], font=F["title"]).pack(side="left")
        self.lbl_time = tk.Label(hdr, text="", bg=C["bg_dark"],
                                  fg=C["text_muted"], font=F["small"])
        self.lbl_time.pack(side="right")

        separator(self, bg=C["bg_dark"]).pack(fill="x", padx=24, pady=(0, 16))

        # ── Stat cards ────────────────────────
        self.card_frame = tk.Frame(self, bg=C["bg_dark"])
        self.card_frame.pack(fill="x", padx=24)

        self.cards = {}  # name → card widget

        card_defs = [
            ("total_employees", "Total Employees", "0", C["accent"]),
            ("active_employees", "Active Staff",   "0", C["success"]),
            ("month_paid",       "This Month Paid","₹0", C["accent2"]),
            ("total_paid",       "All-Time Paid",  "₹0", C["accent4"]),
        ]
        for i, (key, title, val, color) in enumerate(card_defs):
            card = make_card(self.card_frame, title, val, color=color)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
            self.card_frame.columnconfigure(i, weight=1)
            self.cards[key] = card

        # ── Department breakdown ───────────────
        sec = section_label(self, "Department Breakdown", bg=C["bg_dark"])
        sec.pack(fill="x", padx=24, pady=(20, 8))

        self.dept_frame = tk.Frame(self, bg=C["bg_dark"])
        self.dept_frame.pack(fill="x", padx=24)

        # ── Recent payroll ─────────────────────
        sec2 = section_label(self, "Recent Payroll Activity", bg=C["bg_dark"])
        sec2.pack(fill="x", padx=24, pady=(20, 8))

        from tkinter import ttk
        cols = ("Employee", "Designation", "Month", "Year", "Net Salary")
        self.tree = ttk.Treeview(self, columns=cols, show="headings",
                                  style="Dark.Treeview", height=8)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor="center")
        self.tree.pack(fill="x", padx=24, pady=(0, 12))

        # Refresh button
        refresh_btn = tk.Button(self, text="⟳  Refresh", bg=C["bg_input"],
                                 fg=C["accent"], font=F["small"],
                                 relief="flat", bd=0, cursor="hand2",
                                 command=self.refresh)
        refresh_btn.pack(padx=24, anchor="e")

        self._tick()
        self.refresh()

    # ── Refresh data ──────────────────────────
    def refresh(self):
        stats = db.get_dashboard_stats()

        # Update cards
        def update_card(card_widget, new_val):
            """Find and update the value label inside a card."""
            for child in card_widget.winfo_children():
                if child.winfo_class() == "Label":
                    txt = child.cget("text")
                    # The big number label has card_num font
                    if child.cget("font") == " ".join(map(str, F["card_num"])):
                        child.config(text=str(new_val))
                        return

        # Rebuild cards with fresh values
        for w in self.card_frame.winfo_children():
            w.destroy()

        card_defs = [
            ("total_employees", "Total Employees", stats["total_employees"], C["accent"],    ""),
            ("active_employees","Active Staff",     stats["active_employees"],C["success"],   ""),
            ("month_paid",      "This Month Paid",  f"₹{stats['month_paid']:,.0f}", C["accent2"],
             stats["current_month"]),
            ("total_paid",      "All-Time Paid",    f"₹{stats['total_paid']:,.0f}", C["accent4"],
             f"Avg ₹{stats['avg_salary']:,.0f}"),
        ]
        for i, (key, title, val, color, sub) in enumerate(card_defs):
            card = make_card(self.card_frame, title, val, subtitle=sub, color=color)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
            self.card_frame.columnconfigure(i, weight=1)

        # Dept breakdown bars
        for w in self.dept_frame.winfo_children():
            w.destroy()

        colors = [C["accent"], C["accent2"], C["success"], C["warning"], C["accent3"]]
        total = stats["total_employees"] or 1
        for i, dept in enumerate(stats["dept_breakdown"]):
            row = tk.Frame(self.dept_frame, bg=C["bg_dark"])
            row.pack(fill="x", pady=2)
            name = dept.get("department") or "Unknown"
            cnt  = dept["cnt"]
            pct  = cnt / total

            tk.Label(row, text=name, bg=C["bg_dark"], fg=C["text_prim"],
                     font=F["small"], width=18, anchor="w").pack(side="left")

            bar_bg = tk.Frame(row, bg=C["bg_card"], height=10)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(4, 8))
            bar_bg.update_idletasks()

            clr = colors[i % len(colors)]
            bar_fill = tk.Frame(row, bg=clr, height=10,
                                width=int(bar_bg.winfo_width() * pct or 60))
            bar_fill.place(in_=bar_bg, relx=0, rely=0, relwidth=pct, relheight=1)

            tk.Label(row, text=str(cnt), bg=C["bg_dark"], fg=C["text_sec"],
                     font=F["tiny"]).pack(side="left")

        # Recent payroll
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = db.get_all_payroll()[:10]
        for r in rows:
            self.tree.insert("", "end", values=(
                r.get("name", ""),
                r.get("designation", ""),
                r.get("month", ""),
                r.get("year", ""),
                f"₹{r.get('net_salary', 0):,.2f}",
            ))

    def _tick(self):
        now = datetime.now().strftime("%a, %d %b %Y  %I:%M %p")
        self.lbl_time.config(text=now)
        self.after(60000, self._tick)
