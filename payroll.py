"""
payroll.py — Payroll Management tab (Calculate / Save / Payslip / Export).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database as db
from styles import (C, F, styled_entry, action_button,
                    section_label, separator)

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]
YEARS  = [str(y) for y in range(2020, datetime.now().year + 3)]


class PayrollTab(tk.Frame):
    def __init__(self, parent, on_data_change=None):
        super().__init__(parent, bg=C["bg_dark"])
        self.on_data_change = on_data_change
        self._selected_record_id = None
        self._build()

    # ═══════════════════════════════════════════
    #  Layout
    # ═══════════════════════════════════════════
    def _build(self):
        top = tk.Frame(self, bg=C["bg_dark"])
        top.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(top, text="Payroll Management", bg=C["bg_dark"],
                 fg=C["text_prim"], font=F["title"]).pack(side="left")
        separator(self, bg=C["bg_dark"]).pack(fill="x", padx=24, pady=(0, 12))

        split = tk.Frame(self, bg=C["bg_dark"])
        split.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        split.columnconfigure(0, weight=2)
        split.columnconfigure(1, weight=3)
        split.rowconfigure(0, weight=1)

        self._build_form(split)
        self._build_records(split)

    # ── Calculator form (left) ─────────────────
    def _build_form(self, parent):
        left = tk.Frame(parent, bg=C["bg_card"],
                        highlightthickness=1, highlightbackground=C["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        canvas = tk.Canvas(left, bg=C["bg_card"], highlightthickness=0)
        sb = ttk.Scrollbar(left, orient="vertical", command=canvas.yview,
                           style="Dark.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.form = tk.Frame(canvas, bg=C["bg_card"], padx=18, pady=18)
        wid = canvas.create_window((0, 0), window=self.form, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(wid, width=canvas.winfo_width())
        self.form.bind("<Configure>", _resize)

        # ── Title ────
        tk.Label(self.form, text="Salary Calculator", bg=C["bg_card"],
                 fg=C["accent"], font=F["heading"]).pack(anchor="w", pady=(0, 16))

        # ── Employee ID lookup ────
        tk.Label(self.form, text="Employee ID *", bg=C["bg_card"],
                 fg=C["text_sec"], font=F["small"]).pack(anchor="w")
        row = tk.Frame(self.form, bg=C["bg_card"])
        row.pack(fill="x", pady=(2, 10))
        self.var_emp_id = tk.StringVar()
        styled_entry(row, textvariable=self.var_emp_id).pack(side="left",
                     fill="x", expand=True, ipady=6)
        action_button(row, "🔍", self._lookup_employee, "muted", width=3).pack(
            side="right", padx=(6, 0))

        # Employee info display
        self.lbl_emp_info = tk.Label(self.form, text="", bg=C["bg_card"],
                                      fg=C["accent"], font=F["small"])
        self.lbl_emp_info.pack(anchor="w", pady=(0, 10))

        # ── Month / Year ────
        row2 = tk.Frame(self.form, bg=C["bg_card"])
        row2.pack(fill="x", pady=(0, 10))
        row2.columnconfigure(0, weight=1)
        row2.columnconfigure(1, weight=1)

        tk.Label(row2, text="Month *", bg=C["bg_card"],
                 fg=C["text_sec"], font=F["small"]).grid(row=0, column=0, sticky="w")
        self.var_month = tk.StringVar(value=datetime.now().strftime("%B"))
        ttk.Combobox(row2, textvariable=self.var_month, values=MONTHS,
                     state="readonly", style="Dark.TCombobox",
                     font=F["body"]).grid(row=1, column=0, sticky="ew", padx=(0, 6), ipady=4)

        tk.Label(row2, text="Year *", bg=C["bg_card"],
                 fg=C["text_sec"], font=F["small"]).grid(row=0, column=1, sticky="w")
        self.var_year = tk.StringVar(value=str(datetime.now().year))
        ttk.Combobox(row2, textvariable=self.var_year, values=YEARS,
                     state="readonly", style="Dark.TCombobox",
                     font=F["body"]).grid(row=1, column=1, sticky="ew", ipady=4)

        # ── Salary fields ────
        fields_top = [
            ("var_basic",      "Basic Salary (₹) *"),
            ("var_total_days", "Total Working Days *"),
            ("var_absents",    "Absent Days"),
        ]
        for attr, label in fields_top:
            self._form_field(attr, label)

        # Separator
        separator(self.form, bg=C["bg_card"]).pack(fill="x", pady=8)
        tk.Label(self.form, text="Allowances & Deductions",
                 bg=C["bg_card"], fg=C["text_muted"], font=F["small"]).pack(anchor="w")

        fields_bot = [
            ("var_medical",    "Medical Allowance (₹)"),
            ("var_conveyance", "Conveyance Allowance (₹)"),
            ("var_bonus",      "Bonus (₹)"),
            ("var_pf",         "PF Deduction (₹)"),
        ]
        for attr, label in fields_bot:
            self._form_field(attr, label)

        separator(self.form, bg=C["bg_card"]).pack(fill="x", pady=8)

        # ── Net salary display ────
        net_frame = tk.Frame(self.form, bg=C["bg_input"],
                             highlightthickness=1, highlightbackground=C["accent"],
                             padx=14, pady=10)
        net_frame.pack(fill="x")
        tk.Label(net_frame, text="NET SALARY", bg=C["bg_input"],
                 fg=C["text_sec"], font=F["tiny"]).pack(anchor="w")
        self.var_net = tk.StringVar(value="₹ 0.00")
        tk.Label(net_frame, textvariable=self.var_net, bg=C["bg_input"],
                 fg=C["accent"], font=("Segoe UI", 20, "bold")).pack(anchor="w")

        # ── Action buttons ────
        separator(self.form, bg=C["bg_card"]).pack(fill="x", pady=12)
        row3 = tk.Frame(self.form, bg=C["bg_card"])
        row3.pack(fill="x")
        action_button(row3, "⚡ Calculate", self._calculate,
                      "primary", width=0).pack(side="left", fill="x",
                      expand=True, ipady=6)
        action_button(row3, "💾 Save", self._save_payroll,
                      "secondary", width=0).pack(side="left", fill="x",
                      expand=True, ipady=6, padx=(6, 0))

        row4 = tk.Frame(self.form, bg=C["bg_card"])
        row4.pack(fill="x", pady=(6, 0))
        action_button(row4, "🧾 Payslip", self._show_payslip,
                      "success", width=0).pack(side="left", fill="x",
                      expand=True, ipady=6)
        action_button(row4, "⟳ Clear", self._clear_form,
                      "muted", width=0).pack(side="left", fill="x",
                      expand=True, ipady=6, padx=(6, 0))

    def _form_field(self, attr, label):
        tk.Label(self.form, text=label, bg=C["bg_card"],
                 fg=C["text_sec"], font=F["small"]).pack(anchor="w")
        var = tk.StringVar()
        setattr(self, attr, var)
        styled_entry(self.form, textvariable=var).pack(fill="x", ipady=6, pady=(2, 10))

    # ── Records table (right) ──────────────────
    def _build_records(self, parent):
        right = tk.Frame(parent, bg=C["bg_dark"])
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Search
        search_row = tk.Frame(right, bg=C["bg_dark"])
        search_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.var_search = tk.StringVar()
        self.var_search.trace("w", lambda *a: self._load_records())
        tk.Label(search_row, text="🔍", bg=C["bg_input"],
                 fg=C["text_sec"], font=F["body"], padx=8).pack(side="left")
        e = styled_entry(search_row, textvariable=self.var_search)
        e.pack(side="left", fill="x", expand=True, ipady=7)

        # Table
        cols = ("ID", "Emp ID", "Name", "Month", "Year",
                "Basic", "Absents", "PF", "Net Salary")
        self.tree = ttk.Treeview(right, columns=cols, show="headings",
                                  style="Dark.Treeview")
        widths = {"ID": 50, "Emp ID": 80, "Name": 120, "Month": 90,
                  "Year": 60, "Basic": 90, "Absents": 70, "PF": 80, "Net Salary": 100}
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 90), anchor="center")
        self.tree.tag_configure("odd",  background=C["bg_table"])
        self.tree.tag_configure("even", background=C["bg_card"])

        vsb = ttk.Scrollbar(right, orient="vertical",
                            command=self.tree.yview, style="Dark.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(right, orient="horizontal",
                            command=self.tree.xview, style="Dark.Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        hsb.grid(row=2, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._on_record_select)

        # Bottom actions
        btn_row = tk.Frame(right, bg=C["bg_dark"])
        btn_row.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        action_button(btn_row, "🗑 Delete Record", self._delete_record,
                      "danger", width=15).pack(side="right")
        action_button(btn_row, "📤 Export CSV", self._export_csv,
                      "muted", width=14).pack(side="right", padx=(0, 6))
        self.lbl_total = tk.Label(btn_row, text="", bg=C["bg_dark"],
                                   fg=C["text_muted"], font=F["tiny"])
        self.lbl_total.pack(side="left")

        self._load_records()

    # ═══════════════════════════════════════════
    #  Data helpers
    # ═══════════════════════════════════════════
    def _load_records(self):
        q = self.var_search.get().strip()
        rows = db.get_all_payroll(q)
        for c in self.tree.get_children():
            self.tree.delete(c)
        total = 0
        for i, r in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            total += r.get("net_salary", 0)
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r["id"], r["emp_id"], r.get("name", ""),
                r["month"], r["year"],
                f"₹{r.get('basic', 0):,.0f}",
                r.get("absents", 0),
                f"₹{r.get('pf', 0):,.0f}",
                f"₹{r.get('net_salary', 0):,.2f}",
            ), tags=(tag,))
        self.lbl_total.config(text=f"{len(rows)} records  |  Total paid: ₹{total:,.2f}")

    def _on_record_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        self._selected_record_id = int(sel[0])

    def _lookup_employee(self):
        emp_id = self.var_emp_id.get().strip()
        if not emp_id:
            messagebox.showwarning("Input", "Enter an Employee ID first.", parent=self)
            return
        emp = db.get_employee(emp_id)
        if emp:
            self.lbl_emp_info.config(
                text=f"✓ {emp['name']} — {emp.get('designation','')}"
            )
            if emp.get("basic_salary"):
                self.var_basic.set(str(emp["basic_salary"]))
        else:
            self.lbl_emp_info.config(text="✗ Employee not found", fg=C["error"])

    # ── Calculate ─────────────────────────────
    def _calculate(self):
        try:
            basic       = float(self.var_basic.get() or 0)
            total_days  = int(self.var_total_days.get() or 26)
            absents     = int(self.var_absents.get() or 0)
            medical     = float(self.var_medical.get() or 0)
            conveyance  = float(self.var_conveyance.get() or 0)
            bonus       = float(self.var_bonus.get() or 0)
            pf          = float(self.var_pf.get() or 0)

            if total_days <= 0:
                raise ValueError("Total working days must be > 0")
            if absents < 0 or absents > total_days:
                raise ValueError("Absent days must be between 0 and total days")

            per_day    = basic / total_days
            worked     = total_days - absents
            earned     = per_day * worked
            gross      = earned + medical + conveyance + bonus
            net        = gross - pf

            self.var_net.set(f"₹ {net:,.2f}")
            self._calculated_net = round(net, 2)

        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex), parent=self)
        except Exception as ex:
            messagebox.showerror("Error", str(ex), parent=self)

    # ── Save ──────────────────────────────────
    def _save_payroll(self):
        emp_id = self.var_emp_id.get().strip()
        month  = self.var_month.get().strip()
        year   = self.var_year.get().strip()

        if not emp_id:
            messagebox.showerror("Error", "Employee ID is required.", parent=self)
            return
        if not db.get_employee(emp_id):
            messagebox.showerror("Error", "Employee not found in database.", parent=self)
            return

        if not hasattr(self, "_calculated_net"):
            self._calculate()
        if not hasattr(self, "_calculated_net"):
            return

        data = {
            "emp_id":      emp_id,
            "month":       month,
            "year":        year,
            "basic":       float(self.var_basic.get() or 0),
            "total_days":  int(self.var_total_days.get() or 26),
            "absents":     int(self.var_absents.get() or 0),
            "medical":     float(self.var_medical.get() or 0),
            "conveyance":  float(self.var_conveyance.get() or 0),
            "bonus":       float(self.var_bonus.get() or 0),
            "pf":          float(self.var_pf.get() or 0),
            "net_salary":  self._calculated_net,
        }
        ok = db.save_payroll(data)
        if ok:
            messagebox.showinfo("Saved", "Payroll record saved successfully!", parent=self)
            self._load_records()
            if self.on_data_change:
                self.on_data_change()
        else:
            messagebox.showerror("Error", "Failed to save payroll.", parent=self)

    # ── Payslip ───────────────────────────────
    def _show_payslip(self):
        emp_id = self.var_emp_id.get().strip()
        emp = db.get_employee(emp_id) if emp_id else None

        if not emp_id or not emp:
            messagebox.showwarning("Missing", "Look up a valid employee first.", parent=self)
            return

        if not hasattr(self, "_calculated_net"):
            self._calculate()
        if not hasattr(self, "_calculated_net"):
            return

        PayslipWindow(self, emp, {
            "month":      self.var_month.get(),
            "year":       self.var_year.get(),
            "basic":      float(self.var_basic.get() or 0),
            "total_days": int(self.var_total_days.get() or 26),
            "absents":    int(self.var_absents.get() or 0),
            "medical":    float(self.var_medical.get() or 0),
            "conveyance": float(self.var_conveyance.get() or 0),
            "bonus":      float(self.var_bonus.get() or 0),
            "pf":         float(self.var_pf.get() or 0),
            "net":        self._calculated_net,
        })

    def _delete_record(self):
        if not self._selected_record_id:
            messagebox.showwarning("No Selection", "Select a payroll record first.", parent=self)
            return
        if not messagebox.askyesno("Confirm", "Delete this payroll record?", parent=self):
            return
        ok = db.delete_payroll(self._selected_record_id)
        if ok:
            self._selected_record_id = None
            self._load_records()
            if self.on_data_change:
                self.on_data_change()
        else:
            messagebox.showerror("Error", "Delete failed.", parent=self)

    def _clear_form(self):
        for attr in ("var_emp_id", "var_basic", "var_total_days", "var_absents",
                     "var_medical", "var_conveyance", "var_bonus", "var_pf"):
            getattr(self, attr).set("")
        self.var_net.set("₹ 0.00")
        self.lbl_emp_info.config(text="", fg=C["accent"])
        if hasattr(self, "_calculated_net"):
            del self._calculated_net

    def _export_csv(self):
        import csv
        from tkinter import filedialog
        rows = db.get_all_payroll()
        if not rows:
            messagebox.showinfo("No Data", "No payroll records to export.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            parent=self
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Exported {len(rows)} records.", parent=self)

    def refresh(self):
        self._load_records()


# ═══════════════════════════════════════════════
#  Payslip popup window
# ═══════════════════════════════════════════════

class PayslipWindow(tk.Toplevel):
    def __init__(self, parent, emp: dict, pay: dict):
        super().__init__(parent)
        self.title("Salary Payslip")
        self.geometry("500x620")
        self.resizable(False, False)
        self.configure(bg=C["bg_dark"])
        self.grab_set()
        self._center()
        self._build(emp, pay)

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"500x620+{(sw-500)//2}+{(sh-620)//2}")

    def _build(self, emp, pay):
        outer = tk.Frame(self, bg=C["bg_dark"])
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        hdr = tk.Frame(outer, bg=C["accent"], padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="SALARY PAYSLIP", bg=C["accent"],
                 fg=C["bg_dark"], font=("Segoe UI", 16, "bold")).pack(side="left")
        tk.Label(hdr, text=f"{pay['month']} {pay['year']}", bg=C["accent"],
                 fg=C["bg_dark"], font=F["subhead"]).pack(side="right")

        # Employee info
        info_frame = tk.Frame(outer, bg=C["bg_card"], padx=20, pady=12)
        info_frame.pack(fill="x", pady=(12, 0))
        for label, val in [
            ("Employee ID",  emp.get("emp_id", "")),
            ("Name",         emp.get("name", "")),
            ("Designation",  emp.get("designation", "")),
            ("Department",   emp.get("department", "")),
        ]:
            row = tk.Frame(info_frame, bg=C["bg_card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label+":", bg=C["bg_card"], fg=C["text_sec"],
                     font=F["small"], width=14, anchor="w").pack(side="left")
            tk.Label(row, text=str(val), bg=C["bg_card"], fg=C["text_prim"],
                     font=F["small"]).pack(side="left")

        # Pay table
        table = tk.Frame(outer, bg=C["bg_card"])
        table.pack(fill="x", pady=10)

        def row(lbl, val, bold=False, color=None):
            r = tk.Frame(table, bg=C["bg_card"])
            r.pack(fill="x", padx=20, pady=3)
            font = F["subhead"] if bold else F["body"]
            tk.Label(r, text=lbl, bg=C["bg_card"], fg=color or C["text_prim"],
                     font=font, anchor="w").pack(side="left")
            tk.Label(r, text=f"₹ {val:,.2f}", bg=C["bg_card"],
                     fg=color or C["text_prim"], font=font).pack(side="right")

        tk.Frame(table, bg=C["border"], height=1).pack(fill="x", padx=20, pady=4)
        tk.Label(table, text="EARNINGS", bg=C["bg_card"], fg=C["text_sec"],
                 font=F["tiny"], padx=20).pack(anchor="w")
        tk.Frame(table, bg=C["border"], height=1).pack(fill="x", padx=20, pady=4)

        worked = pay["total_days"] - pay["absents"]
        per_day = pay["basic"] / pay["total_days"] if pay["total_days"] else 0
        earned = per_day * worked
        row(f"Basic (worked {worked}/{pay['total_days']} days)", earned)
        row("Medical Allowance",  pay["medical"])
        row("Conveyance Allowance", pay["conveyance"])
        row("Bonus", pay["bonus"])

        tk.Frame(table, bg=C["border"], height=1).pack(fill="x", padx=20, pady=4)
        tk.Label(table, text="DEDUCTIONS", bg=C["bg_card"], fg=C["text_sec"],
                 font=F["tiny"], padx=20).pack(anchor="w")
        tk.Frame(table, bg=C["border"], height=1).pack(fill="x", padx=20, pady=4)
        row("Provident Fund (PF)", pay["pf"], color=C["accent3"])

        tk.Frame(table, bg=C["accent"], height=2).pack(fill="x", padx=20, pady=8)
        row("NET SALARY", pay["net"], bold=True, color=C["accent"])
        tk.Frame(table, bg=C["accent"], height=2).pack(fill="x", padx=20, pady=2)

        # Footer buttons
        btn_row = tk.Frame(outer, bg=C["bg_dark"])
        btn_row.pack(fill="x", pady=10)
        action_button(btn_row, "💾 Save PDF", self._save_pdf, "primary", width=0).pack(
            side="left", fill="x", expand=True, ipady=6)
        action_button(btn_row, "✕ Close", self.destroy, "muted", width=0).pack(
            side="right", fill="x", expand=True, ipady=6, padx=(6, 0))

        self._emp = emp
        self._pay = pay

    def _save_pdf(self):
        from tkinter import filedialog, messagebox
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Missing Library",
                "Install fpdf2 first:\n  pip install fpdf2", parent=self)
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            parent=self
        )
        if not path:
            return

        emp, pay = self._emp, self._pay
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "SALARY PAYSLIP", ln=True, align="C")
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, f"Period: {pay['month']} {pay['year']}", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Employee Details", ln=True)
        pdf.set_font("Arial", size=11)
        for k, v in [("Employee ID", emp.get("emp_id","")),
                     ("Name", emp.get("name","")),
                     ("Designation", emp.get("designation","")),
                     ("Department", emp.get("department",""))]:
            pdf.cell(60, 7, k+":", border=0)
            pdf.cell(0, 7, str(v), ln=True)
        pdf.ln(5)
        worked = pay["total_days"] - pay["absents"]
        per_day = pay["basic"] / pay["total_days"] if pay["total_days"] else 0
        earned = per_day * worked
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Earnings", ln=True)
        pdf.set_font("Arial", size=11)
        for k, v in [
            (f"Basic (worked {worked}/{pay['total_days']} days)", earned),
            ("Medical Allowance", pay["medical"]),
            ("Conveyance", pay["conveyance"]),
            ("Bonus", pay["bonus"]),
        ]:
            pdf.cell(100, 7, k)
            pdf.cell(0, 7, f"Rs {v:,.2f}", ln=True)
        pdf.ln(3)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Deductions", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(100, 7, "Provident Fund (PF)")
        pdf.cell(0, 7, f"Rs {pay['pf']:,.2f}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", "B", 13)
        pdf.cell(100, 10, "NET SALARY")
        pdf.cell(0, 10, f"Rs {pay['net']:,.2f}", ln=True)
        pdf.output(path)
        messagebox.showinfo("Saved", f"PDF saved to:\n{path}", parent=self)
