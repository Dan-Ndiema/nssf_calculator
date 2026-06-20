import streamlit as st
import pandas as pd
from datetime import date
import plotly.graph_objects as go
from fpdf import FPDF
import io

#---Constants
TIER_1_LIMIT = 8_000
TIER_2_LIMIT = 72_000
RATE = 0.06

#---Core functions (from phase 1, 2, 3)
def calculate_contribution(gross_salary):
    tier1_base = min(gross_salary, TIER_1_LIMIT)
    tier1_employee = round(tier1_base * RATE, 2)
    tier1_employer = round(tier1_base * RATE, 2)    

    if gross_salary > TIER_1_LIMIT:
        tier2_base = min(gross_salary, TIER_2_LIMIT) - TIER_1_LIMIT
        tier2_employee = round(tier2_base * RATE, 2)
        tier2_employer = round(tier2_base * RATE, 2)
    else:
        tier2_base = 0
        tier2_employee = 0.0
        tier2_employer = 0.0

    total_employee = tier1_employee + tier2_employee
    total_employer = tier1_employer + tier2_employer    
    net_pay = gross_salary - total_employee

    return {
        "gross-salary": gross_salary,
        "tier1_base": tier1_base,
        "tier1_employee": tier1_employee,
        "tier1_employer": tier1_employer,
        "tier2_base": tier2_base,
        "tier2_employee": tier2_employee,
        "tier2_employer": tier2_employer,
        "total_employee": total_employee,   
        "total_employer": total_employer,
        "net_pay": net_pay  
    }  
def project_savings(gross_salary, years, annual_rate=0.17):
    c = calculate_contribution(gross_salary)
    monthly_contribution = c["total_employee"] + c["total_employer"]
    monthly_rate = annual_rate / 12

    projection = []
    balance = 0.0

    for year in range(1, years + 1):
        for month in range(12):
            balance = (balance + monthly_contribution) * (1 + monthly_rate)
        projection.append({
            "Year": year,
            "Annual Contribution (KSh)": round(monthly_contribution * 12, 2),
            "Balance (KSh)": round(balance, 2)
        })
    return pd.DataFrame(projection)
def register_member(member_id, name, id_number, employer, gross_salary, start_date):
    c = calculate_contribution(gross_salary)
    return {
        "member_id": member_id,
        "name": name,
        "id_number": id_number,
        "employer": employer,
        "gross_salary": gross_salary,
        "total_employee": c["total_employee"],
        "total_employer": c["total_employer"],
        "net_pay": c["net_pay"],
        "start_date": str(start_date),
        "registered_on": str(date.today()),
    }
def generate_pdf_statement(name, member_id, salary, c, projection_df=None, years=None, rate=None):
    """Generate a member contribution/projection statement as PDF bytes."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "NSSF Member Statement", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Member: {name}", ln=True)
    pdf.cell(0, 8, f"Member ID: {member_id}", ln=True)
    pdf.cell(0, 8, f"Gross Salary: KSh {salary:,.2f}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Monthly Contribution Breakdown", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Tier I  - Employee: KSh {c['tier1_employee']:,.2f}  |  Employer: KSh {c['tier1_employer']:,.2f}", ln=True)
    pdf.cell(0, 8, f"Tier II - Employee: KSh {c['tier2_employee']:,.2f}  |  Employer: KSh {c['tier2_employer']:,.2f}", ln=True)
    pdf.cell(0, 8, f"Total   - Employee: KSh {c['total_employee']:,.2f}  |  Employer: KSh {c['total_employer']:,.2f}", ln=True)
    pdf.cell(0, 8, f"Net Take-Home Pay: KSh {c['net_pay']:,.2f}", ln=True)

    if projection_df is not None:
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Savings Projection ({years} years at {rate}% annual return)", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(40, 7, "Year", border=1)
        pdf.cell(70, 7, "Annual Contribution (KSh)", border=1)
        pdf.cell(70, 7, "Balance (KSh)", border=1, ln=True)

        for _, row in projection_df.iterrows():
            pdf.cell(40, 7, str(int(row["Year"])), border=1)
            pdf.cell(70, 7, f"{row['Annual Contribution (KSh)']:,.2f}", border=1)
            pdf.cell(70, 7, f"{row['Balance (KSh)']:,.2f}", border=1, ln=True)

    return bytes(pdf.output())

# Streamlit App
st.set_page_config(page_title="NSSF Calculator", page_icon="KE", layout="centered")
st.title("KE NSSF Contribution Calculator")
st.caption("Based on NSSF Act 2013-2026 rates")

page = st.sidebar.radio(
    "Navigate",
    ["Contribution Calculator", "Savings Projection", "Member Registration"]
)

# Page 1: Contribution Calculator
if page == "Contribution Calculator":
    st.header("Contribution Calculator")
    st.write("Enter a gross monthly salary to see the NSSF deduction breakdown.")

    salary = st.number_input(
        "Gross Monthly Salary (Ksh)",
        min_value=0,
        max_value=500_000,
        value=50_000,
        step=1_000
    )

    if salary > 0:
        c = calculate_contribution(salary)
    st.subheader("Contribution Breakdown")
    col1, col2 = st.columns(2)
    col1.metric("Employee Deduction", f"Ksh {c['total_employee']:,.0f}")
    col2.metric("Employer Contribution", f"Ksh {c['total_employer']:,.0f}")

    st.table(pd.DataFrame({
            "Tier":       ["Tier I", "Tier II", "Total"],
            "Base (KSh)": [f"{c['tier1_base']:,}", f"{c['tier2_base']:,}", ""],
            "Employee":   [f"KSh {c['tier1_employee']:,.0f}",
                           f"KSh {c['tier2_employee']:,.0f}",
                           f"KSh {c['total_employee']:,.0f}"],
            "Employer":   [f"KSh {c['tier1_employer']:,.0f}",
                           f"KSh {c['tier2_employer']:,.0f}",
                           f"KSh {c['total_employer']:,.0f}"]
        }))
    st.success(f"Net Take-Home Pay: KSh {c['net_pay']:,.2f}")

# Page 2: savings Projection
elif page == "Savings Projection":
    st.header("Savings Projection")
    st.write("See how your NSSF savings grow over time.")

    salary = st.number_input(
        "Gross Monthly Salary (KSh)",
        min_value=0,
        max_value=500_000,
        value=50_000,
        step=1_000
    )
    years = st.slider("Years to Retirement", min_value=1, max_value=40, value=30)
    rate = st.slider("Annual Return Rate (%)", min_value=1, max_value=30, value=17)

    if salary > 0:
        df = project_savings(salary, years, annual_rate=rate/100)
        final = df["Balance (KSh)"].iloc[-1]
        st.metric("Projected Balance at Retirement", f"KSh {final:,.2f}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Year"], y=df["Balance (KSh)"],
            mode="lines+markers", name="Balance",
            line=dict(color="#2ecc71", width=3)
        ))
        fig.update_layout(
            title="Projected Savings Growth",
            xaxis_title="Year",
            yaxis_title="Balance (KSh)",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df.style.format({
            "Annual Contribution (KSh)": "KSh {:,.2f}",
            "Balance (KSh)": "KSh {:,.2f}"
        }), use_container_width=True)

        c = calculate_contribution(salary)
        pdf_bytes = generate_pdf_statement(
            name="Member", member_id="N/A", salary=salary, c=c,
            projection_df=df, years=years, rate=rate
        )
        st.download_button(
            label="Download PDF Statement",
            data=pdf_bytes,
            file_name="nssf_statement.pdf",
            mime="application/pdf"
        )

# ── PAGE 3: Member Registration ──────────────────────
elif page == "Member Registration":
    st.header("Member Registration")
    st.write("Register a new NSSF member and save to Excel.")

    with st.form("registration_form"):
        member_id   = st.text_input("NSSF Member ID", placeholder="e.g. NSSF004")
        name        = st.text_input("Full Name", placeholder="e.g. John Kamau")
        id_number   = st.text_input("National ID Number")
        employer    = st.text_input("Employer Name")
        salary      = st.number_input("Gross Monthly Salary (KSh)",
                                      min_value=0, max_value=500_000,
                                      value=30_000, step=1_000)
        start_date  = st.date_input("Contribution Start Date")
        submitted   = st.form_submit_button("Register Member")

    if submitted:
        if not member_id or not name or not id_number or not employer:
            st.error("Please fill in all fields before registering.")
        else:
            member = register_member(member_id, name, id_number,
                                     employer, salary, start_date)
            new_row = pd.DataFrame([member])

            try:
                existing = pd.read_excel("nssf_records.xlsx",
                                         sheet_name="Members")
                updated = pd.concat([existing, new_row], ignore_index=True)
            except Exception:
                updated = new_row

            with pd.ExcelWriter("nssf_records.xlsx", engine="openpyxl",
                                mode="w") as writer:
                updated.to_excel(writer, sheet_name="Members", index=False)

            st.success(f"Member {name} registered successfully!")
            st.table(new_row[["member_id", "name", "employer",
                               "gross_salary", "total_employee",
                               "total_employer", "net_pay"]])
            



