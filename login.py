"""
login.py — Secure admin login window.
"""

import tkinter as tk
from tkinter import messagebox
import database as db
from styles import C, F, styled_entry, action_button


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PayrollPro — Login")
        self.geometry("860x940")
        self.resizable(False, False)
        self.configure(bg=C["bg_dark"])
        self._center()

        self._user = None
        self._build_ui()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - 860) // 2
        y = (sh - 940) // 2
        self.geometry(f"860x940+{x}+{y}")

    # ── UI ────────────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self, bg=C["bg_dark"])
        outer.pack(fill="both", expand=True, padx=40, pady=40)

        # Logo / brand
        tk.Canvas(outer, width=60, height=60, bg=C["bg_dark"],
                  highlightthickness=0).pack(pady=(0, 6))
        logo_c = tk.Canvas(outer, width=64, height=64, bg=C["bg_dark"],
                           highlightthickness=0)
        logo_c.pack()
        logo_c.create_oval(4, 4, 60, 60, fill=C["accent"], outline="")
        logo_c.create_text(32, 32, text="₹", font=("Segoe UI", 28, "bold"),
                           fill=C["bg_dark"])

        tk.Label(outer, text="PayrollPro", bg=C["bg_dark"],
                 fg=C["text_prim"], font=("Segoe UI", 22, "bold")).pack(pady=(10, 2))
        tk.Label(outer, text="Workforce & Salary Management", bg=C["bg_dark"],
                 fg=C["text_sec"], font=F["small"]).pack()

        # Card
        card = tk.Frame(outer, bg=C["bg_card"], padx=28, pady=28,
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", pady=24)

        tk.Label(card, text="Sign in to your account", bg=C["bg_card"],
                 fg=C["text_prim"], font=F["heading"]).pack(anchor="w", pady=(0, 18))

        # Username
        tk.Label(card, text="Username", bg=C["bg_card"],
                 fg=C["text_sec"], font=F["small"]).pack(anchor="w")
        self.var_user = tk.StringVar()
        e_user = styled_entry(card, textvariable=self.var_user)
        e_user.pack(fill="x", ipady=7, pady=(3, 14))

        # Password
        tk.Label(card, text="Password", bg=C["bg_card"],
                 fg=C["text_sec"], font=F["small"]).pack(anchor="w")
        self.var_pass = tk.StringVar()
        e_pass = styled_entry(card, textvariable=self.var_pass, show="●")
        e_pass.pack(fill="x", ipady=7, pady=(3, 6))

        # Show/hide password
        self._show_pass = tk.BooleanVar(value=False)

        def toggle_pass():
            e_pass.config(show="" if self._show_pass.get() else "●")

        tk.Checkbutton(
            card, text="Show password", variable=self._show_pass,
            command=toggle_pass,
            bg=C["bg_card"], fg=C["text_sec"], selectcolor=C["bg_input"],
            activebackground=C["bg_card"], activeforeground=C["text_prim"],
            font=F["tiny"], bd=0, highlightthickness=0,
        ).pack(anchor="w", pady=(0, 16))

        # Error message label
        self.lbl_error = tk.Label(card, text="", bg=C["bg_card"],
                                   fg=C["error"], font=F["small"])
        self.lbl_error.pack(anchor="w")

        # Login button
        btn = action_button(card, "  Sign In  →", command=self._login,
                            color="primary", width=0)
        btn.pack(fill="x", ipady=4, pady=(4, 0))

        # Hint
        hint = tk.Label(outer, text="Default: admin / admin123",
                        bg=C["bg_dark"], fg=C["text_muted"], font=F["tiny"])
        hint.pack()

        # Bindings
        e_user.bind("<Return>", lambda e: e_pass.focus_set())
        e_pass.bind("<Return>", lambda e: self._login())
        e_user.focus_set()

    # ── Logic ─────────────────────────────────
    def _login(self):
        username = self.var_user.get().strip()
        password = self.var_pass.get().strip()

        if not username or not password:
            self.lbl_error.config(text="⚠  Please enter username and password.")
            return

        user = db.verify_login(username, password)
        if user:
            self._user = user
            self.destroy()
        else:
            self.lbl_error.config(text="✗  Invalid username or password.")
            self.var_pass.set("")

    def get_user(self):
        return self._user


def run_login():
    """Show login window and return authenticated user dict or None."""
    db.init_db()
    win = LoginWindow()
    win.mainloop()
    return win.get_user()
