"""
main.py — PayrollPro main application window.
Sidebar navigation + tabbed content area.
"""

import tkinter as tk
from tkinter import messagebox
from styles import C, F, apply_theme
from dashboard import DashboardTab
from employees import EmployeeTab
from payroll import PayrollTab
import database as db


class MainApp:
    def __init__(self, user: dict):
        self.root = tk.Tk()
        self.user = user
        self.root.title("PayrollPro — Workforce & Salary Management")
        self.root.state("zoomed")          # start maximised
        self.root.minsize(1100, 650)
        self.root.configure(bg=C["bg_dark"])

        # Initialize attributes
        self._pages = {}
        self._nav_buttons = {}
        self._active_page = None

        self._build_ui()
        apply_theme(self.root)
        self._nav_to("dashboard")

    # ═══════════════════════════════════════════
    #  UI skeleton
    # ═══════════════════════════════════════════
    def _build_ui(self):
        # ── Sidebar ───────────────────────────
        self.sidebar = tk.Frame(self.root, bg=C["bg_sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # ── Main area ─────────────────────────
        self.main_area = tk.Frame(self.root, bg=C["bg_dark"])
        self.main_area.pack(side="left", fill="both", expand=True)

    # ── Sidebar ──────────────────────────────
    def _build_sidebar(self):
        sb = self.sidebar

        # Brand / Logo
        brand = tk.Frame(sb, bg=C["bg_sidebar"], pady=20)
        brand.pack(fill="x")

        logo_c = tk.Canvas(brand, width=40, height=40, bg=C["bg_sidebar"],
                           highlightthickness=0)
        logo_c.pack()
        logo_c.create_oval(2, 2, 38, 38, fill=C["accent"], outline="")
        logo_c.create_text(20, 20, text="₹", font=("Segoe UI", 18, "bold"),
                           fill=C["bg_dark"])

        tk.Label(brand, text="PayrollPro", bg=C["bg_sidebar"],
                 fg=C["text_prim"], font=("Segoe UI", 15, "bold")).pack(pady=(6, 0))
        tk.Label(brand, text="v2.0 Professional", bg=C["bg_sidebar"],
                 fg=C["text_muted"], font=F["tiny"]).pack()

        # Divider
        tk.Frame(sb, bg=C["border"], height=1).pack(fill="x", padx=16, pady=8)

        # Nav items: (key, icon, label)
        nav_items = [
            ("dashboard", "◉", "Dashboard"),
            ("employees", "👥", "Employees"),
            ("payroll",   "💰", "Payroll"),
        ]
        for key, icon, label in nav_items:
            btn = self._nav_btn(sb, key, icon, label)
            self._nav_buttons[key] = btn

        # Bottom section
        tk.Frame(sb, bg=C["border"], height=1).pack(fill="x", padx=16, pady=8)

        # User info
        user_frame = tk.Frame(sb, bg=C["bg_sidebar"], padx=16, pady=12)
        user_frame.pack(fill="x", side="bottom")

        tk.Frame(sb, bg=C["border"], height=1).pack(fill="x", padx=16,
                                                      side="bottom", pady=4)

        # Logout button
        logout_btn = tk.Button(
            user_frame, text="⏻  Sign Out",
            bg=C["bg_sidebar"], fg=C["accent3"],
            font=F["small"], relief="flat", bd=0,
            cursor="hand2", anchor="w",
            command=self._logout, width=20
        )
        logout_btn.pack(fill="x", pady=(8, 0))

        # Username display
        avatar = tk.Canvas(user_frame, width=32, height=32,
                           bg=C["bg_sidebar"], highlightthickness=0)
        avatar.pack(side="left")
        avatar.create_oval(2, 2, 30, 30, fill=C["accent2"], outline="")
        avatar.create_text(16, 16,
                           text=self.user.get("username", "?")[0].upper(),
                           font=("Segoe UI", 12, "bold"), fill="white")

        info = tk.Frame(user_frame, bg=C["bg_sidebar"])
        info.pack(side="left", padx=(8, 0))
        tk.Label(info, text=self.user.get("username", ""), bg=C["bg_sidebar"],
                 fg=C["text_prim"], font=F["small"]).pack(anchor="w")
        role = self.user.get("role", "admin").capitalize()
        tk.Label(info, text=role, bg=C["bg_sidebar"],
                 fg=C["text_muted"], font=F["tiny"]).pack(anchor="w")

    def _nav_btn(self, parent, key, icon, label):
        frame = tk.Frame(parent, bg=C["bg_sidebar"], cursor="hand2")
        frame.pack(fill="x", padx=8, pady=2)

        indicator = tk.Canvas(frame, width=4, height=36,
                               bg=C["bg_sidebar"], highlightthickness=0)
        indicator.pack(side="left")

        content = tk.Frame(frame, bg=C["bg_sidebar"], padx=12, pady=8)
        content.pack(side="left", fill="x", expand=True)

        icon_lbl = tk.Label(content, text=icon, bg=C["bg_sidebar"],
                             fg=C["text_sec"], font=F["body"])
        icon_lbl.pack(side="left")

        text_lbl = tk.Label(content, text=label, bg=C["bg_sidebar"],
                             fg=C["text_sec"], font=F["nav"])
        text_lbl.pack(side="left", padx=(8, 0))

        def on_click(e=None):
            self._nav_to(key)

        def on_enter(e):
            if self._active_page != key:
                frame.config(bg=C["sidebar_hover"])
                content.config(bg=C["sidebar_hover"])
                icon_lbl.config(bg=C["sidebar_hover"])
                text_lbl.config(bg=C["sidebar_hover"])

        def on_leave(e):
            if self._active_page != key:
                frame.config(bg=C["bg_sidebar"])
                content.config(bg=C["bg_sidebar"])
                icon_lbl.config(bg=C["bg_sidebar"])
                text_lbl.config(bg=C["bg_sidebar"])

        for widget in (frame, content, icon_lbl, text_lbl):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return {
            "frame": frame, "content": content,
            "icon": icon_lbl, "text": text_lbl,
            "indicator": indicator,
        }

    # ── Navigation ────────────────────────────
    def _nav_to(self, key: str):
        if self._active_page == key:
            return

        # Deactivate old
        if self._active_page and self._active_page in self._nav_buttons:
            old = self._nav_buttons[self._active_page]
            for widget in (old["frame"], old["content"], old["icon"], old["text"]):
                widget.config(bg=C["bg_sidebar"])
            old["text"].config(fg=C["text_sec"], font=F["nav"])
            old["icon"].config(fg=C["text_sec"])
            old["indicator"].config(bg=C["bg_sidebar"])

        # Activate new
        btn = self._nav_buttons[key]
        for widget in (btn["frame"], btn["content"], btn["icon"], btn["text"]):
            widget.config(bg=C["sidebar_active"])
        btn["text"].config(fg=C["text_prim"], font=F["nav_bold"])
        btn["icon"].config(fg=C["accent"])
        btn["indicator"].delete("all")
        btn["indicator"].create_rectangle(0, 4, 4, 32, fill=C["accent"], outline="")

        self._active_page = key

        # Hide all pages
        for pg in self._pages.values():
            pg.pack_forget()

        # Show or create page
        if key not in self._pages:
            if key == "dashboard":
                page = DashboardTab(self.main_area)
                self._dash = page
            elif key == "employees":
                page = EmployeeTab(self.main_area,
                                    on_data_change=self._refresh_all)
                self._emp = page
            elif key == "payroll":
                page = PayrollTab(self.main_area,
                                   on_data_change=self._refresh_all)
                self._pay = page
            else:
                return
            self._pages[key] = page

        self._pages[key].pack(fill="both", expand=True)

        # Refresh data when switching to dashboard
        if key == "dashboard" and hasattr(self, "_dash"):
            self._dash.refresh()

    def _refresh_all(self):
        """Called when any CRUD happens — refresh dashboard."""
        if "dashboard" in self._pages and hasattr(self, "_dash"):
            self._dash.refresh()

    def _logout(self):
        if messagebox.askyesno("Sign Out", "Sign out of PayrollPro?", parent=self.root):
            self.root.destroy()


# ═══════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════

def launch(user: dict):
    app = MainApp(user)
    app.root.mainloop()
