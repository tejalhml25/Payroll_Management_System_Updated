# Payroll Management System — Streamlit UI

## Features
- Dashboard, add/search/display employees
- Attendance and absence tracking
- Automatic salary deduction for absent days
- Payslip generation and download
- Permanent employee records in `employees.csv`
- Download payroll report as CSV

## Salary formula
- HRA = Basic Salary × 20%
- DA = Basic Salary × 10%
- Tax = Basic Salary × 5%
- Gross Salary = Basic Salary + HRA + DA
- Daily Salary = Basic Salary ÷ Total Working Days
- Absence Deduction = Daily Salary × Absent Days
- Net Salary = Gross Salary − Tax − Absence Deduction

## Run
1. Extract the ZIP and open its folder in VS Code.
2. Run `pip install -r requirements.txt`
3. Run `streamlit run app.py`

The app creates `employees.csv` automatically and saves employee/attendance changes to it.
Keep the CSV file in the same folder as `app.py` to retain records.
