"""
styles.py — Centralised colour palette, fonts, and widget style helpers.
All UI files import from here so a single change updates the whole app.
"""

import tkinter as tk
from tkinter import ttk


# ─────────────────────────────────────────────
#  Colour Palette  (dark navy + electric teal)
# ─────────────────────────────────────────────
C = {
    # Backgrounds
    "bg_dark":    "#0D1117",   # main window
    "bg_sidebar": "#161B22",   # sidebar
    "bg_card":    "#1C2128",   # cards / frames
    "bg_input":   "#21262D",   # entry fields
    "bg_table":   "#161B22",   # treeview rows

    # Accents
    "accent":     "#00D4AA",   # teal primary
    "accent2":    "#0070F3",   # blue secondary
    "accent3":    "#F78166",   # coral warning/delete
    "accent4":    "#F1E05A",   # yellow highlight

    # Text
    "text_prim":  "#E6EDF3",   # primary white
    "text_sec":   "#8B949E",   # secondary grey
    "text_muted": "#484F58",   # muted/disabled

    # Borders
    "border":     "#30363D",
    "border_acc": "#00D4AA",

    # Status colours
    "success":    "#3FB950",
    "warning":    "#D29922",
    "error":      "#F85149",
    "info":       "#58A6FF",

    # Sidebar active
    "sidebar_active": "#1F2937",
    "sidebar_hover":  "#1A2332",
}

# ─────────────────────────────────────────────
#  Fonts
# ─────────────────────────────────────────────
F = {
    "title":   ("Segoe UI", 22, "bold"),
    "heading": ("Segoe UI", 14, "bold"),
    "subhead": ("Segoe UI", 12, "bold"),
    "body":    ("Segoe UI", 11),
    "small":   ("Segoe UI", 10),
    "tiny":    ("Segoe UI", 9),
    "mono":    ("Consolas", 11),
    "card_num": ("Segoe UI", 26, "bold"),
    "card_lbl": ("Segoe UI", 10),
    "nav":     ("Segoe UI", 12),
    "nav_bold":("Segoe UI", 12, "bold"),
}

# ─────────────────────────────────────────────
#  Shared padding / sizing
# ─────────────────────────────────────────────
PAD   = 12
PAD_S = 6
RADIUS = 6   # not native tkinter but used in Canvas rects


# ─────────────────────────────────────────────
#  TTK Style Setup
# ─────────────────────────────────────────────

def apply_theme(root: tk.Tk):
    """Apply dark theme to ttk widgets globally."""
    style = ttk.Style()
    style.theme_use("clam")

    # ── Treeview ──
    style.configure("Dark.Treeview",
        background=C["bg_table"],
        foreground=C["text_prim"],
        fieldbackground=C["bg_table"],
        rowheight=32,
        font=F["body"],
        borderwidth=0,
    )
    style.configure("Dark.Treeview.Heading",
        background=C["bg_card"],
        foreground=C["accent"],
        font=F["subhead"],
        relief="flat",
        borderwidth=0,
    )
    style.map("Dark.Treeview",
        background=[("selected", C["accent2"])],
        foreground=[("selected", C["text_prim"])],
    )
    style.map("Dark.Treeview.Heading",
        background=[("active", C["bg_input"])],
    )

    # ── Scrollbar ──
    style.configure("Dark.Vertical.TScrollbar",
        background=C["bg_card"],
        troughcolor=C["bg_dark"],
        borderwidth=0,
        arrowcolor=C["text_sec"],
    )
    style.configure("Dark.Horizontal.TScrollbar",
        background=C["bg_card"],
        troughcolor=C["bg_dark"],
        borderwidth=0,
        arrowcolor=C["text_sec"],
    )

    # ── Notebook (tabs) ──
    style.configure("Dark.TNotebook",
        background=C["bg_dark"],
        tabmargins=[2, 5, 2, 0],
        borderwidth=0,
    )
    style.configure("Dark.TNotebook.Tab",
        background=C["bg_card"],
        foreground=C["text_sec"],
        font=F["nav"],
        padding=[16, 8],
        borderwidth=0,
    )
    style.map("Dark.TNotebook.Tab",
        background=[("selected", C["bg_sidebar"]), ("active", C["bg_input"])],
        foreground=[("selected", C["accent"]), ("active", C["text_prim"])],
    )

    # ── Combobox ──
    style.configure("Dark.TCombobox",
        fieldbackground=C["bg_input"],
        background=C["bg_input"],
        foreground=C["text_prim"],
        arrowcolor=C["accent"],
        borderwidth=1,
        relief="flat",
        font=F["body"],
    )
    style.map("Dark.TCombobox",
        fieldbackground=[("readonly", C["bg_input"])],
        selectbackground=[("readonly", C["bg_input"])],
    )

    # ── Separator ──
    style.configure("Dark.TSeparator", background=C["border"])

    # ── Frame ──
    style.configure("Card.TFrame", background=C["bg_card"])
    style.configure("Dark.TFrame", background=C["bg_dark"])
    style.configure("Sidebar.TFrame", background=C["bg_sidebar"])


# ─────────────────────────────────────────────
#  Reusable widget builders
# ─────────────────────────────────────────────

def styled_entry(parent, textvariable=None, width=None, **kw):
    """Dark-themed tk.Entry."""
    cfg = dict(
        bg=C["bg_input"],
        fg=C["text_prim"],
        insertbackground=C["accent"],
        relief="flat",
        font=F["body"],
        bd=0,
        highlightthickness=1,
        highlightbackground=C["border"],
        highlightcolor=C["accent"],
    )
    cfg.update(kw)
    if textvariable:
        cfg["textvariable"] = textvariable
    e = tk.Entry(parent, **cfg)
    if width:
        e.config(width=width)
    return e


def styled_label(parent, text="", style="body", fg=None, **kw):
    """Dark-themed tk.Label."""
    cfg = dict(
        text=text,
        bg=C["bg_card"],
        fg=fg or C["text_prim"],
        font=F.get(style, F["body"]),
    )
    cfg.update(kw)
    return tk.Label(parent, **cfg)


def action_button(parent, text, command=None, color=None, width=14, **kw):
    """
    A flat, coloured button with hover effect.
    color: 'primary'|'danger'|'warning'|'success'|'secondary'
    """
    colour_map = {
        "primary":   (C["accent"],  C["bg_dark"]),
        "danger":    (C["accent3"], C["bg_dark"]),
        "warning":   (C["warning"], C["bg_dark"]),
        "success":   (C["success"], C["bg_dark"]),
        "secondary": (C["accent2"], C["bg_dark"]),
        "muted":     (C["bg_input"], C["text_prim"]),
    }
    bg, fg = colour_map.get(color or "primary", colour_map["primary"])

    btn = tk.Button(
        parent,
        text=text,
        bg=bg, fg=fg,
        activebackground=C["bg_input"],
        activeforeground=C["text_prim"],
        font=F["subhead"],
        relief="flat",
        bd=0,
        cursor="hand2",
        width=width,
        padx=8, pady=6,
    )
    if command:
        btn.config(command=command)

    # Hover effects
    def on_enter(e): btn.config(bg=C["bg_input"], fg=C["text_prim"])
    def on_leave(e): btn.config(bg=bg, fg=fg)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn


def section_label(parent, text, bg=None):
    """Section header label with teal left border via canvas."""
    bg = bg or C["bg_card"]
    frame = tk.Frame(parent, bg=bg)

    bar = tk.Canvas(frame, width=4, height=22, bg=C["accent"], highlightthickness=0)
    bar.pack(side="left", padx=(0, 8))

    lbl = tk.Label(frame, text=text, bg=bg, fg=C["text_prim"], font=F["heading"])
    lbl.pack(side="left")

    return frame


def separator(parent, bg=None):
    bg = bg or C["bg_card"]
    return tk.Frame(parent, height=1, bg=C["border"])


def make_card(parent, title, value, subtitle="", color=None):
    """
    A dashboard summary card.
    Returns the frame widget (caller packs/grids it).
    """
    color = color or C["accent"]
    card = tk.Frame(parent, bg=C["bg_card"], padx=16, pady=14,
                    highlightthickness=1, highlightbackground=C["border"])

    top = tk.Frame(card, bg=C["bg_card"])
    top.pack(fill="x")

    tk.Label(top, text=title, bg=C["bg_card"], fg=C["text_sec"],
             font=F["card_lbl"]).pack(side="left")

    # coloured dot indicator
    dot = tk.Canvas(top, width=8, height=8, bg=C["bg_card"], highlightthickness=0)
    dot.create_oval(0, 0, 8, 8, fill=color, outline="")
    dot.pack(side="right")

    tk.Label(card, text=str(value), bg=C["bg_card"], fg=color,
             font=F["card_num"]).pack(anchor="w", pady=(4, 0))

    if subtitle:
        tk.Label(card, text=subtitle, bg=C["bg_card"], fg=C["text_muted"],
                 font=F["small"]).pack(anchor="w")

    return card
