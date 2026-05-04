# PayrollPro — Professional Payroll Management System
## Upgraded from basic Tkinter project to a modern, modular application

---

## 📁 Project Structure

```
payroll_system/
├── app.py          # ← Entry point (run this)
├── database.py     # SQLite layer — all CRUD operations
├── styles.py       # Colours, fonts, widget builders
├── login.py        # Secure login window
├── main.py         # Main window + sidebar navigation
├── dashboard.py    # Dashboard overview tab
├── employees.py    # Employee management tab
├── payroll.py      # Payroll calculator + payslip tab
├── payroll.db      # SQLite DB (auto-created on first run)
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Python 3.8+
https://www.python.org/downloads/

### 2. Install dependencies
```bash
pip install fpdf2
```
> Tkinter is included with Python on Windows/macOS.  
> On Ubuntu/Debian: `sudo apt install python3-tk`

### 3. Run the app
```bash
cd payroll_system
python app.py
```

### 4. Default login credentials
| Username | Password  |
|----------|-----------|
| `admin`  | `admin123`|

> Change your password via `database.change_password("admin", "newpassword")`

---

## ✨ Features

### 🔐 Login Portal
- SHA-256 hashed passwords stored in SQLite
- Show/hide password toggle
- Input validation with inline error messages

### 📊 Dashboard
- Live stats cards: Total employees, Active staff, Monthly payout, All-time total
- Department breakdown with visual bars
- Recent payroll activity table
- Auto-refreshes when data changes

### 👥 Employee Management
- Add / Edit / Delete employees with full CRUD
- Searchable, sortable table
- Dropdown fields (Designation, Department, Gender, Status)
- Input validation (email format, numeric age/salary)
- Export all employees to CSV

### 💰 Payroll Management
- Auto-fill basic salary from employee record
- Net salary formula:  
  `Net = (Basic/TotalDays × WorkedDays) + Medical + Conveyance + Bonus − PF`
- Save payroll record (upserts per employee/month/year)
- Printable payslip popup with PDF export
- Searchable payroll history table
- Export payroll records to CSV

### 🎨 UI/UX
- Dark navy + electric teal design language
- Sidebar navigation with active indicators + hover effects
- Scrollable forms
- Alternating table row colours
- Responsive layout (starts maximised)

---

## 🔮 Suggested Future Improvements

| Feature | Description |
|---------|-------------|
| **Role-based access** | Manager vs HR vs Admin roles with permission gates |
| **Multi-user login** | Add/manage users from within the app |
| **Leave management** | Track leave types, balances, approvals |
| **Attendance import** | Import attendance from CSV/Excel |
| **Email payslips** | Send payslip PDFs directly via SMTP |
| **Charts/graphs** | Matplotlib salary trends, headcount charts |
| **Web version** | FastAPI + React for browser-based access |
| **Department budgets** | Track salary budgets per department |
| **Tax calculation** | Auto-compute Income Tax / TDS slabs |

---

## 🛠 Tech Stack
- **Python 3.8+**
- **Tkinter + ttk** — GUI framework
- **SQLite3** — embedded database (no setup needed)
- **fpdf2** (optional) — PDF payslip export
- **hashlib** — password hashing (SHA-256)
- **csv** — CSV export
