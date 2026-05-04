"""
database.py — SQLite database layer for PayrollPro
Handles all DB connections, schema creation, and CRUD operations.
"""

import sqlite3
import hashlib
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), "payroll.db")


def get_connection():
    """Return a new SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    """SHA-256 hash a password string."""
    return hashlib.sha256(password.encode()).hexdigest()


# ─────────────────────────────────────────────
#  Schema initialisation
# ─────────────────────────────────────────────

def init_db():
    """Create all tables and seed default admin if they don't exist."""
    conn = get_connection()
    c = conn.cursor()

    # Admin / users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT    NOT NULL UNIQUE,
            password  TEXT    NOT NULL,
            role      TEXT    NOT NULL DEFAULT 'admin',
            created_at TEXT   DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Employees table
    c.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            emp_id        TEXT PRIMARY KEY,
            name          TEXT NOT NULL,
            designation   TEXT,
            department    TEXT,
            age           INTEGER,
            gender        TEXT,
            email         TEXT,
            contact       TEXT,
            address       TEXT,
            hired_location TEXT,
            dob           TEXT,
            doj           TEXT,
            experience    TEXT,
            proof_id      TEXT,
            status        TEXT DEFAULT 'Active',
            basic_salary  REAL DEFAULT 0.0,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Payroll records table
    c.execute("""
        CREATE TABLE IF NOT EXISTS payroll (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id      TEXT NOT NULL,
            month       TEXT NOT NULL,
            year        TEXT NOT NULL,
            basic       REAL DEFAULT 0.0,
            total_days  INTEGER DEFAULT 26,
            absents     INTEGER DEFAULT 0,
            medical     REAL DEFAULT 0.0,
            conveyance  REAL DEFAULT 0.0,
            pf          REAL DEFAULT 0.0,
            bonus       REAL DEFAULT 0.0,
            net_salary  REAL DEFAULT 0.0,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    """)

    # Seed default admin  (admin / admin123)
    c.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "admin")
        )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
#  Auth
# ─────────────────────────────────────────────

def verify_login(username: str, password: str):
    """Return user row if credentials match, else None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def change_password(username: str, new_password: str) -> bool:
    try:
        conn = get_connection()
        conn.execute(
            "UPDATE users SET password=? WHERE username=?",
            (hash_password(new_password), username)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
#  Employee CRUD
# ─────────────────────────────────────────────

def add_employee(data: dict) -> bool:
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO employees
            (emp_id, name, designation, department, age, gender, email, contact,
             address, hired_location, dob, doj, experience, proof_id, status, basic_salary)
            VALUES (:emp_id,:name,:designation,:department,:age,:gender,:email,:contact,
                    :address,:hired_location,:dob,:doj,:experience,:proof_id,:status,:basic_salary)
        """, data)
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def update_employee(data: dict) -> bool:
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE employees SET
                name=:name, designation=:designation, department=:department,
                age=:age, gender=:gender, email=:email, contact=:contact,
                address=:address, hired_location=:hired_location, dob=:dob,
                doj=:doj, experience=:experience, proof_id=:proof_id,
                status=:status, basic_salary=:basic_salary
            WHERE emp_id=:emp_id
        """, data)
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def delete_employee(emp_id: str) -> bool:
    try:
        conn = get_connection()
        conn.execute("DELETE FROM payroll WHERE emp_id=?", (emp_id,))
        conn.execute("DELETE FROM employees WHERE emp_id=?", (emp_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_all_employees(search: str = "") -> list:
    conn = get_connection()
    if search:
        rows = conn.execute(
            "SELECT * FROM employees WHERE emp_id LIKE ? OR name LIKE ? ORDER BY name",
            (f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM employees ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_employee(emp_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM employees WHERE emp_id=?", (emp_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─────────────────────────────────────────────
#  Payroll CRUD
# ─────────────────────────────────────────────

def save_payroll(data: dict) -> bool:
    try:
        conn = get_connection()
        # Upsert: delete old record for same month/year then insert
        conn.execute(
            "DELETE FROM payroll WHERE emp_id=? AND month=? AND year=?",
            (data["emp_id"], data["month"], data["year"])
        )
        conn.execute("""
            INSERT INTO payroll
            (emp_id, month, year, basic, total_days, absents, medical, conveyance, pf, bonus, net_salary)
            VALUES (:emp_id,:month,:year,:basic,:total_days,:absents,:medical,:conveyance,:pf,:bonus,:net_salary)
        """, data)
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_payroll_history(emp_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM payroll WHERE emp_id=? ORDER BY year DESC, month DESC",
        (emp_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_payroll(search: str = "") -> list:
    conn = get_connection()
    query = """
        SELECT p.*, e.name, e.designation, e.department
        FROM payroll p
        JOIN employees e ON p.emp_id = e.emp_id
    """
    if search:
        query += " WHERE p.emp_id LIKE ? OR e.name LIKE ?"
        rows = conn.execute(query + " ORDER BY p.year DESC, p.month", (f"%{search}%", f"%{search}%")).fetchall()
    else:
        rows = conn.execute(query + " ORDER BY p.year DESC, p.month").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_payroll(record_id: int) -> bool:
    try:
        conn = get_connection()
        conn.execute("DELETE FROM payroll WHERE id=?", (record_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
#  Dashboard statistics
# ─────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    conn = get_connection()
    total_emp    = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    active_emp   = conn.execute("SELECT COUNT(*) FROM employees WHERE status='Active'").fetchone()[0]
    total_paid   = conn.execute("SELECT COALESCE(SUM(net_salary),0) FROM payroll").fetchone()[0]
    this_month   = datetime.now().strftime("%B")
    this_year    = str(datetime.now().year)
    month_paid   = conn.execute(
        "SELECT COALESCE(SUM(net_salary),0) FROM payroll WHERE month=? AND year=?",
        (this_month, this_year)
    ).fetchone()[0]
    avg_salary   = conn.execute("SELECT COALESCE(AVG(basic_salary),0) FROM employees").fetchone()[0]
    dept_counts  = conn.execute(
        "SELECT department, COUNT(*) as cnt FROM employees GROUP BY department ORDER BY cnt DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return {
        "total_employees": total_emp,
        "active_employees": active_emp,
        "total_paid": round(total_paid, 2),
        "month_paid": round(month_paid, 2),
        "avg_salary": round(avg_salary, 2),
        "dept_breakdown": [dict(d) for d in dept_counts],
        "current_month": this_month,
        "current_year": this_year,
    }
