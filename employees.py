"""
employees.py — Employee Management tab (Add / Edit / Delete / Search / View).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
import database as db
from styles import (C, F, styled_entry, action_button,
                    section_label, separator)


DESIGNATIONS = ["Software Engineer", "Senior Engineer", "Manager", "HR Executive",
                "Accountant", "Sales Executive", "Team Lead", "Director", "Intern", "Other"]
DEPARTMENTS   = ["Engineering", "HR", "Finance", "Sales", "Marketing",
                 "Operations", "Admin", "Legal", "Support", "Other"]
GENDERS       = ["Male", "Female", "Other", "Prefer not to say"]
STATUSES      = ["Active", "Inactive", "On Leave", "Terminated"]


class EmployeeTab(tk.Frame):
    def __init__(self, parent, on_data_change=None):
        super().__init__(parent, bg=C["bg_dark"])
        self.on_data_change = on_data_change  # callback to refresh dashboard
        self._selected_id = None
        self._build()

    # ═══════════════════════════════════════════
    #  Layout
    # ═══════════════════════════════════════════
    def _build(self):
        # ── Top bar ───────────────────────────
        top = tk.Frame(self, bg=C["bg_dark"])
        top.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(top, text="Employee Management", bg=C["bg_dark"],
                 fg=C["text_prim"], font=F["title"]).pack(side="left")

        separator(self, bg=C["bg_dark"]).pack(fill="x", padx=24, pady=(0, 12))

        # ── Main split ────────────────────────
        split = tk.Frame(self, bg=C["bg_dark"])
        split.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        split.columnconfigure(0, weight=3)
        split.columnconfigure(1, weight=2)
        split.rowconfigure(0, weight=1)

        self._build_table(split)
        self._build_form(split)

    # ── Table (left) ──────────────────────────
    def _build_table(self, parent):
        left = tk.Frame(parent, bg=C["bg_dark"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Search bar
        search_row = tk.Frame(left, bg=C["bg_dark"])
        search_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.var_search = tk.StringVar()
        self.var_search.trace("w", lambda *a: self._load_employees())
        search_icon = tk.Label(search_row, text="🔍", bg=C["bg_input"],
                               fg=C["text_sec"], font=F["body"], padx=8)
        search_icon.pack(side="left")
        search_e = styled_entry(search_row, textvariable=self.var_search,
                                highlightbackground=C["border"])
        search_e.pack(side="left", fill="x", expand=True, ipady=7)
        search_e.insert(0, "Search by ID or name…")
        search_e.config(fg=C["text_muted"])
        search_e.bind("<FocusIn>", lambda e: (
            search_e.delete(0, "end"), search_e.config(fg=C["text_prim"])
        ) if search_e.get() == "Search by ID or name…" else None)

        # Treeview
        cols = ("ID", "Name", "Designation", "Department", "Contact", "Status", "Salary")
        self.tree = ttk.Treeview(left, columns=cols, show="headings",
                                  style="Dark.Treeview")
        widths = {"ID": 90, "Name": 140, "Designation": 130,
                  "Department": 110, "Contact": 110, "Status": 80, "Salary": 90}
        for col in cols:
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_tree(c))
            self.tree.column(col, width=widths.get(col, 100), anchor="center")

        vsb = ttk.Scrollbar(left, orient="vertical",
                            command=self.tree.yview, style="Dark.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")

        # Tag rows for alternating colours
        self.tree.tag_configure("odd",  background=C["bg_table"])
        self.tree.tag_configure("even", background=C["bg_card"])
        self.tree.tag_configure("inactive", foreground=C["text_muted"])

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self._load_employees()

        # Bottom action row
        btn_row = tk.Frame(left, bg=C["bg_dark"])
        btn_row.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        action_button(btn_row, "🗑  Delete", self._delete_employee,
                      "danger", width=12).pack(side="right")
        action_button(btn_row, "📤 Export CSV", self._export_csv,
                      "muted", width=14).pack(side="right", padx=(0, 6))
        self.lbl_count = tk.Label(btn_row, text="", bg=C["bg_dark"],
                                   fg=C["text_muted"], font=F["tiny"])
        self.lbl_count.pack(side="left")

    # ── Form (right) ──────────────────────────
    def _build_form(self, parent):
        right = tk.Frame(parent, bg=C["bg_card"],
                         highlightthickness=1, highlightbackground=C["border"])
        right.grid(row=0, column=1, sticky="nsew")

        # Scrollable inner
        canvas = tk.Canvas(right, bg=C["bg_card"], highlightthickness=0)
        sb = ttk.Scrollbar(right, orient="vertical", command=canvas.yview,
                           style="Dark.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.form = tk.Frame(canvas, bg=C["bg_card"], padx=18, pady=18)
        win_id = canvas.create_window((0, 0), window=self.form, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())
        self.form.bind("<Configure>", _resize)

        # ── Form title ────
        hdr = tk.Frame(self.form, bg=C["bg_card"])
        hdr.pack(fill="x", pady=(0, 16))
        self.lbl_form_title = tk.Label(hdr, text="Add New Employee",
                                        bg=C["bg_card"], fg=C["accent"],
                                        font=F["heading"])
        self.lbl_form_title.pack(side="left")
        tk.Button(hdr, text="✕ Clear", bg=C["bg_card"], fg=C["text_muted"],
                  font=F["tiny"], relief="flat", bd=0, cursor="hand2",
                  command=self._clear_form).pack(side="right")

        # ── Field definitions ────
        self._vars = {}
        fields = [
            ("emp_id",        "Employee ID *",     "entry"),
            ("name",          "Full Name *",        "entry"),
            ("designation",   "Designation",        "combo",  DESIGNATIONS),
            ("department",    "Department",         "combo",  DEPARTMENTS),
            ("gender",        "Gender",             "combo",  GENDERS),
            ("age",           "Age",                "entry"),
            ("email",         "Email",              "entry"),
            ("contact",       "Contact",            "entry"),
            ("dob",           "Date of Birth",      "entry"),
            ("doj",           "Date of Joining",    "entry"),
            ("experience",    "Experience (yrs)",   "entry"),
            ("proof_id",      "Proof ID / Aadhar",  "entry"),
            ("hired_location","Hired Location",     "entry"),
            ("basic_salary",  "Basic Salary (₹) *", "entry"),
            ("status",        "Status",             "combo",  STATUSES),
            ("address",       "Address",            "text"),
        ]

        for field_key, label, kind, *rest in fields:
            self._add_field(field_key, label, kind, rest[0] if rest else None)

        # ── Buttons ───────────────────────────
        separator(self.form, bg=C["bg_card"]).pack(fill="x", pady=12)
        btn_f = tk.Frame(self.form, bg=C["bg_card"])
        btn_f.pack(fill="x")
        self.btn_save = action_button(btn_f, "💾  Save Employee",
                                       self._save_employee, "primary", width=0)
        self.btn_save.pack(side="left", fill="x", expand=True, ipady=6)
        action_button(btn_f, "⟳", self._clear_form, "muted", width=3).pack(
            side="right", padx=(6, 0), ipady=6)

    def _add_field(self, key, label, kind, options=None):
        tk.Label(self.form, text=label, bg=C["bg_card"],
                 fg=C["text_sec"], font=F["small"]).pack(anchor="w")

        if kind == "entry":
            var = tk.StringVar()
            e = styled_entry(self.form, textvariable=var)
            e.pack(fill="x", ipady=6, pady=(2, 10))
            self._vars[key] = var

        elif kind == "combo":
            var = tk.StringVar()
            cb = ttk.Combobox(self.form, textvariable=var,
                               values=options or [], state="readonly",
                               style="Dark.TCombobox", font=F["body"])
            cb.pack(fill="x", pady=(2, 10), ipady=4)
            self._vars[key] = var

        elif kind == "text":
            txt = tk.Text(self.form, height=3,
                          bg=C["bg_input"], fg=C["text_prim"],
                          insertbackground=C["accent"], font=F["body"],
                          relief="flat", bd=0,
                          highlightthickness=1, highlightbackground=C["border"])
            txt.pack(fill="x", pady=(2, 10))
            self._vars[key] = txt   # Text widget, not StringVar

    # ═══════════════════════════════════════════
    #  Data helpers
    # ═══════════════════════════════════════════
    def _load_employees(self):
        query = self.var_search.get()
        if query in ("Search by ID or name…", ""):
            query = ""
        rows = db.get_all_employees(query)
        for child in self.tree.get_children():
            self.tree.delete(child)
        for i, r in enumerate(rows):
            tag = ("even" if i % 2 == 0 else "odd",)
            if r["status"] in ("Inactive", "Terminated"):
                tag = ("inactive",)
            self.tree.insert("", "end", iid=r["emp_id"], values=(
                r["emp_id"], r["name"], r["designation"] or "",
                r["department"] or "", r["contact"] or "",
                r["status"] or "", f"₹{(r['basic_salary'] or 0):,.0f}"
            ), tags=tag)
        self.lbl_count.config(text=f"{len(rows)} employee(s)")

    def _sort_tree(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children()]
        items.sort(key=lambda x: x[0].lower() if isinstance(x[0], str) else x[0])
        for idx, (_, k) in enumerate(items):
            self.tree.move(k, "", idx)

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        emp_id = sel[0]
        emp = db.get_employee(emp_id)
        if not emp:
            return
        self._selected_id = emp_id
        self.lbl_form_title.config(text="Edit Employee")
        self.btn_save.config(text="✏  Update Employee")

        for key, var_or_widget in self._vars.items():
            val = emp.get(key, "") or ""
            if isinstance(var_or_widget, tk.StringVar):
                var_or_widget.set(str(val))
            elif isinstance(var_or_widget, tk.Text):
                var_or_widget.delete("1.0", "end")
                var_or_widget.insert("1.0", str(val))

    # ── Validation ────────────────────────────
    def _collect_form(self):
        data = {}
        for key, v in self._vars.items():
            if isinstance(v, tk.StringVar):
                data[key] = v.get().strip()
            elif isinstance(v, tk.Text):
                data[key] = v.get("1.0", "end").strip()

        errors = []
        if not data.get("emp_id"):
            errors.append("Employee ID is required.")
        if not data.get("name"):
            errors.append("Full Name is required.")
        if data.get("email") and not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
            errors.append("Invalid email address.")
        if data.get("age") and not data["age"].isdigit():
            errors.append("Age must be a number.")
        if data.get("basic_salary"):
            try:
                float(data["basic_salary"])
            except ValueError:
                errors.append("Basic Salary must be a number.")
        return data, errors

    # ── CRUD actions ──────────────────────────
    def _save_employee(self):
        data, errors = self._collect_form()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors), parent=self)
            return

        # Convert types
        data["age"]          = int(data["age"]) if data.get("age") else None
        data["basic_salary"] = float(data["basic_salary"]) if data.get("basic_salary") else 0.0

        if self._selected_id:
            ok = db.update_employee(data)
            msg = "Employee updated successfully!" if ok else "Update failed — check employee ID."
        else:
            ok = db.add_employee(data)
            msg = "Employee added successfully!" if ok else "Failed — Employee ID may already exist."

        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            self._clear_form()
            self._load_employees()
            if self.on_data_change:
                self.on_data_change()
        else:
            messagebox.showerror("Error", msg, parent=self)

    def _delete_employee(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an employee first.", parent=self)
            return
        emp_id = sel[0]
        if not messagebox.askyesno("Confirm Delete",
                                    f"Delete employee '{emp_id}' and all their payroll records?\n"
                                    "This cannot be undone.", parent=self):
            return
        ok = db.delete_employee(emp_id)
        if ok:
            messagebox.showinfo("Deleted", "Employee deleted.", parent=self)
            self._clear_form()
            self._load_employees()
            if self.on_data_change:
                self.on_data_change()
        else:
            messagebox.showerror("Error", "Delete failed.", parent=self)

    def _clear_form(self):
        self._selected_id = None
        self.lbl_form_title.config(text="Add New Employee")
        self.btn_save.config(text="💾  Save Employee")
        for v in self._vars.values():
            if isinstance(v, tk.StringVar):
                v.set("")
            elif isinstance(v, tk.Text):
                v.delete("1.0", "end")
        self.tree.selection_remove(self.tree.selection())

    def _export_csv(self):
        import csv
        from tkinter import filedialog
        rows = db.get_all_employees()
        if not rows:
            messagebox.showinfo("No Data", "No employees to export.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            parent=self
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Exported {len(rows)} records to:\n{path}", parent=self)

    def refresh(self):
        self._load_employees()
