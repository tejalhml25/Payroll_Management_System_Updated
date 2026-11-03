import random
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Payroll Management System", page_icon="💼", layout="wide")
CSV_FILE = Path(__file__).parent / "employees.csv"
COLUMNS = ["Employee ID", "Employee Name", "Basic Salary", "HRA", "DA", "Tax", "Working Days", "Absent Days"]

def load_employees():
    if not CSV_FILE.exists():
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)
        return []
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return []
    return [[int(r["Employee ID"]), str(r["Employee Name"]), float(r["Basic Salary"]),
             float(r["HRA"]), float(r["DA"]), float(r["Tax"]),
             int(r["Working Days"]), int(r["Absent Days"])] for _, r in df.iterrows()]

def save_employees():
    pd.DataFrame(st.session_state.employees, columns=COLUMNS).to_csv(CSV_FILE, index=False)

if "employees" not in st.session_state:
    st.session_state.employees = load_employees()

def calculate_salary(emp):
    emp_id, name, basic, hra, da, tax, working, absent = emp
    gross = basic + hra + da
    absence_deduction = (basic / working) * absent if working else 0
    net = gross - tax - absence_deduction
    return {"Employee ID": emp_id, "Employee Name": name, "Basic Salary": basic,
            "HRA": hra, "DA": da, "Gross Salary": gross, "Tax": tax,
            "Working Days": working, "Absent Days": absent,
            "Absence Deduction": absence_deduction, "Net Salary": net}

def add_employee(emp_id, name, basic, working, absent):
    employees = st.session_state.employees
    if emp_id is None:
        while True:
            emp_id = random.randint(1000, 9999)
            if all(e[0] != emp_id for e in employees):
                break
    elif any(e[0] == emp_id for e in employees):
        return False, "Employee ID already exists!"
    employees.append([emp_id, name, basic, basic*.20, basic*.10, basic*.05, working, absent])
    save_employees()
    return True, f"Employee added successfully! Employee ID: {emp_id}"

st.title("💼 Payroll Management System")
st.caption("Manage employee details, attendance and salary calculations.")
page = st.sidebar.radio("Navigation", ["Dashboard", "Add Employee", "Employee Records",
    "Search Employee", "Attendance & Absence", "Generate Payslip"])
st.sidebar.metric("Total Employees", len(st.session_state.employees))
st.sidebar.caption("Records are saved in employees.csv")

if page == "Dashboard":
    rows = [calculate_salary(e) for e in st.session_state.employees]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Employees", len(rows))
    c2.metric("Total Net Payroll", f"₹{sum(r['Net Salary'] for r in rows):,.2f}")
    basics = [e[2] for e in st.session_state.employees]
    c3.metric("Average Basic Salary", f"₹{sum(basics)/len(basics):,.2f}" if basics else "₹0.00")
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No employee records yet. Add your first employee.")

elif page == "Add Employee":
    st.subheader("➕ Add New Employee")
    with st.form("add_form", clear_on_submit=True):
        mode = st.radio("Employee ID", ["Generate automatically", "Enter manually"], horizontal=True)
        emp_id = st.number_input("Employee ID", min_value=1, step=1) if mode == "Enter manually" else None
        name = st.text_input("Employee Name")
        basic = st.number_input("Basic Salary (₹)", min_value=0.0, step=1000.0)
        working = st.number_input("Total Working Days", min_value=1, max_value=31, value=30)
        absent = st.number_input("Absent Days", min_value=0, max_value=31, value=0)
        submit = st.form_submit_button("Add Employee", type="primary")
    if submit:
        if not name.strip():
            st.error("Please enter employee name.")
        elif basic <= 0:
            st.error("Basic salary must be greater than zero.")
        elif absent > working:
            st.error("Absent days cannot exceed working days.")
        else:
            ok, msg = add_employee(int(emp_id) if emp_id is not None else None,
                                   name.strip(), float(basic), int(working), int(absent))
            st.success(msg) if ok else st.error(msg)

elif page == "Employee Records":
    rows = [calculate_salary(e) for e in st.session_state.employees]
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download Payroll Report (CSV)", df.to_csv(index=False).encode(),
                           "payroll_report.csv", "text/csv")
    else:
        st.info("No employees found.")

elif page == "Search Employee":
    if not st.session_state.employees:
        st.info("Add an employee first.")
    else:
        search_id = st.number_input("Enter Employee ID", min_value=1, step=1)
        if st.button("Search", type="primary"):
            found = next((e for e in st.session_state.employees if e[0] == int(search_id)), None)
            if found:
                st.success("Employee found!")
                st.table(pd.DataFrame([calculate_salary(found)]).set_index("Employee ID"))
            else:
                st.error("Employee not found.")

elif page == "Attendance & Absence":
    st.subheader("📅 Attendance & Absence Management")
    if not st.session_state.employees:
        st.info("Add an employee first.")
    else:
        opts = {f"{e[1]} (ID: {e[0]})": e for e in st.session_state.employees}
        label = st.selectbox("Select Employee", list(opts))
        emp = opts[label]
        with st.form("attendance_form"):
            working = st.number_input("Total Working Days", min_value=1, max_value=31, value=int(emp[6]))
            absent = st.number_input("Absent Days", min_value=0, max_value=31, value=int(emp[7]))
            save = st.form_submit_button("Save Attendance", type="primary")
        if save:
            if absent > working:
                st.error("Absent days cannot exceed working days.")
            else:
                emp[6], emp[7] = int(working), int(absent)
                save_employees()
                st.success("Attendance saved to employees.csv.")
                st.rerun()
        daily = emp[2] / emp[6]
        st.info(f"Current absence deduction: ₹{daily * emp[7]:,.2f} "
                f"({emp[7]} absent day(s) × ₹{daily:,.2f} per day).")

elif page == "Generate Payslip":
    if not st.session_state.employees:
        st.info("Add an employee first.")
    else:
        opts = {f"{e[1]} (ID: {e[0]})": e for e in st.session_state.employees}
        label = st.selectbox("Select Employee", list(opts))
        d = calculate_salary(opts[label])
        st.subheader("🧾 Employee Payslip")
        st.write(f"**Employee:** {d['Employee Name']}  |  **ID:** {d['Employee ID']}")
        for key in ["Basic Salary", "HRA", "DA", "Gross Salary", "Tax",
                    "Working Days", "Absent Days", "Absence Deduction"]:
            value = d[key]
            st.write(f"{key}: " + (f"₹{value:,.2f}" if "Days" not in key else str(value)))
        st.metric("Final Net Salary", f"₹{d['Net Salary']:,.2f}")
        payslip = "\\n".join([f"{k}: {v}" for k, v in d.items()])
        st.download_button("Download Payslip (.txt)", payslip,
                           f"payslip_{d['Employee ID']}.txt", "text/plain")
