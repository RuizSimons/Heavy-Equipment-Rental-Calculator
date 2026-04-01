import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Heavy Equipment Rental Calculator",
    page_icon="🚜",
    layout="wide",
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: INPUT PARAMETERS ---
st.sidebar.header("🚜 Machine Configuration")
machine_model = st.sidebar.selectbox("Equipment Model", ["Caterpillar 730", "Caterpillar 745", "Other"])
landed_cost = st.sidebar.number_input("Landed Cost ($)", value=500000, step=10000)
economic_life_yrs = st.sidebar.slider("Economic Life (Years)", 1, 10, 5)
residual_value_pct = st.sidebar.slider("Residual Value (%)", 0, 100, 40)

st.sidebar.header("📄 Contract Terms")
contract_term_months = st.sidebar.number_input("Contract Duration (Months)", value=24, step=1)
base_hours_monthly = st.sidebar.number_input("Base Hours per Month", value=176, step=1)
margin_pct = st.sidebar.slider("Profit Margin (%)", 0, 50, 15)

st.sidebar.header("🛠 Maintenance & CVA")
cva_hourly = st.sidebar.number_input("CVA Hourly Rate ($/hr)", value=12.50)
tires_hourly = st.sidebar.number_input("Tires & Wear Hourly Rate ($/hr)", value=8.00)
repair_reserve = st.sidebar.number_input("Repair Reserve ($/hr)", value=5.50)

st.sidebar.header("💰 Finance")
interest_rate = st.sidebar.number_input("Annual Interest Rate (%)", value=8.0)

# --- CALCULATIONS ---
# 1. Ownership Costs
total_residual = landed_cost * (residual_value_pct / 100)
total_depreciation = landed_cost - total_residual
monthly_depreciation = total_depreciation / (economic_life_yrs * 12)

# Average Investment Interest (Industry Standard)
avg_investment = (landed_cost + total_residual) / 2
monthly_interest = (avg_investment * (interest_rate / 100)) / 12

# 2. Operating Costs (Variable)
hourly_op_cost = cva_hourly + tires_hourly + repair_reserve
monthly_op_cost = hourly_op_cost * base_hours_monthly

# 3. Totals
subtotal_monthly = monthly_depreciation + monthly_interest + monthly_op_cost
total_monthly_rate = subtotal_monthly * (1 + (margin_pct / 100))
total_contract_value = total_monthly_rate * contract_term_months
overage_rate = (hourly_op_cost + (monthly_depreciation / base_hours_monthly)) * (1 + (margin_pct / 100))

# --- DASHBOARD MAIN SECTION ---
st.title("🚜 Equipment Rental Calculator")
st.subheader(f"Rental Rate Analysis for {machine_model}")

# Top Row Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Rental Rate", f"${total_monthly_rate:,.2f}")
col2.metric("Hourly Overage Rate", f"${overage_rate:,.2f}")
col3.metric("Total Contract Value", f"${total_contract_value:,.0f}")
col4.metric("Breakeven (Monthly)", f"${subtotal_monthly:,.2f}")

st.divider()

# Mid Section: Visuals
left_col, right_col = st.columns([1, 1])

with left_col:
    st.write("### Monthly Cost Breakdown")
    labels = ['Depreciation', 'Interest/Financing', 'Maintenance (CVA/Tires)', 'Profit Margin']
    values = [monthly_depreciation, monthly_interest, monthly_op_cost, total_monthly_rate - subtotal_monthly]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=['#FFC107', '#212121', '#757575', '#4CAF50'])])
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.write("### Cumulative Cash Flow (Contract Life)")
    months = list(range(1, int(contract_term_months) + 1))
    revenue = [total_monthly_rate * m for m in months]
    costs = [subtotal_monthly * m for m in months]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=months, y=revenue, name='Gross Revenue', line=dict(color='#4CAF50', width=4)))
    fig2.add_trace(go.Scatter(x=months, y=costs, name='Total Costs', line=dict(color='#F44336', width=2, dash='dash')))
    fig2.update_layout(xaxis_title="Month", yaxis_title="USD ($)", margin=dict(t=20, b=20, l=0, r=0))
    st.plotly_chart(fig2, use_container_width=True)

# Bottom Section: Summary Table
st.write("### 📊 Detailed Financial Summary")
data = {
    "Description": [
        "Landed Cost", "Residual Value (End of 5 Years)", "Monthly Depreciation", 
        "Monthly Interest", "Monthly Operating Cost (CVA + Wear)", 
        "Base Hours Included", "Profit Margin Applied"
    ],
    "Value": [
        f"${landed_cost:,.2d}", f"${total_residual:,.2d}", f"${monthly_depreciation:,.2f}",
        f"${monthly_interest:,.2f}", f"${monthly_op_cost:,.2f}",
        f"{base_hours_monthly} hrs", f"{margin_pct}%"
    ]
}
st.table(pd.DataFrame(data))

# Warning/Note for the 2-year vs 5-year gap
if contract_term_months < (economic_life_yrs * 12):
    st.warning(f"**Note:** The contract term ({contract_term_months} months) is shorter than the machine's economic life ({economic_life_yrs * 12} months). Ensure the residual value at Month {contract_term_months} is strictly monitored for fleet re-deployment.")
