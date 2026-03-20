import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ---------- Core calculation functions ----------

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate EMI for a reducing-balance loan.
    annual_rate is in % per annum, tenure_months is in months.
    """
    if tenure_months <= 0:
        return 0.0

    monthly_rate = annual_rate / 12 / 100

    if monthly_rate == 0:
        return principal / tenure_months

    emi = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** tenure_months
        / ((1 + monthly_rate) ** tenure_months - 1)
    )
    return emi


def build_amortization_schedule(
    principal: float, annual_rate: float, tenure_months: int, emi: float
) -> pd.DataFrame:
    """
    Build a month-wise amortization schedule:
    Opening balance, EMI, interest, principal, closing balance.
    """
    monthly_rate = annual_rate / 12 / 100
    balance = principal

    rows = []
    for m in range(1, tenure_months + 1):
        interest = balance * monthly_rate
        principal_component = emi - interest

        # Last payment adjustment to avoid negative balance due to rounding
        if principal_component > balance:
            principal_component = balance
            emi_effective = interest + principal_component
        else:
            emi_effective = emi

        closing_balance = balance - principal_component

        rows.append(
            {
                "Month": m,
                "Opening_Balance": balance,
                "EMI": emi_effective,
                "Interest": interest,
                "Principal": principal_component,
                "Closing_Balance": closing_balance,
            }
        )

        balance = closing_balance
        if balance <= 0:
            # Loan fully paid; break early
            break

    df = pd.DataFrame(rows)
    return df


def compute_foreclosure_profile(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    emi: float,
    foreclosure_rate: float,
    gst_rate: float,
):
    """
    For every possible foreclosure month (0..tenure-1),
    compute outstanding principal, foreclosure charges, GST,
    final foreclosure amount, remaining amount if no foreclosure,
    and net savings vs continuing normally.
    """
    schedule = build_amortization_schedule(principal, annual_rate, tenure_months, emi)

    # Total payable if we do NOT foreclose
    total_payable_full = schedule["EMI"].sum()

    results = []
    for k in range(0, tenure_months):
        # Outstanding principal after k EMIs
        if k == 0:
            outstanding = principal
            total_paid_till_k = 0.0
        else:
            row_k = schedule[schedule["Month"] == k]
            if row_k.empty:
                break
            outstanding = float(row_k["Closing_Balance"].values[0])
            total_paid_till_k = float(
                schedule[schedule["Month"] <= k]["EMI"].sum()
            )

        foreclosure_charge = outstanding * foreclosure_rate / 100
        foreclosure_gst = foreclosure_charge * gst_rate / 100
        foreclosure_final_amount = outstanding + foreclosure_charge + foreclosure_gst

        remaining_if_no_foreclosure = total_payable_full - total_paid_till_k
        net_savings = remaining_if_no_foreclosure - foreclosure_final_amount

        results.append(
            {
                "Foreclosure_Month": k,
                "Outstanding_Principal": outstanding,
                "Foreclosure_Charges": foreclosure_charge,
                "GST_on_Charges": foreclosure_gst,
                "Foreclosure_Final_Amount": foreclosure_final_amount,
                "Amount_Remaining_if_No_Foreclosure": remaining_if_no_foreclosure,
                "Net_Savings_vs_No_Foreclosure": net_savings,
                "Total_Paid_Till_Month": total_paid_till_k,
            }
        )

    profile_df = pd.DataFrame(results)
    return profile_df, schedule


# ---------- Streamlit app ----------

def main():
    st.set_page_config(
        page_title="Advanced Loan / EMI & Foreclosure Calculator",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Session state to remember that Calculate was pressed
    if "calculated" not in st.session_state:
        st.session_state.calculated = False

    st.title("Advanced Loan / EMI & Foreclosure Calculator")

    st.markdown(
        """
This tool calculates your EMI, full-tenure interest, and detailed foreclosure impact.

It assumes **reducing-balance interest** and foreclosure charges as a percentage of outstanding principal.
        """
    )

    # ----- Sidebar inputs -----
    st.sidebar.header("Loan Inputs")

    loan_amount = st.sidebar.number_input(
        "Loan Amount (Principal)",
        min_value=1000,
        value=495151,
        step=10000,
        format="%d",
    )

    annual_interest = st.sidebar.number_input(
        "Annual Interest Rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=13.5,
        step=0.1,
        format="%.3f",
    )

    tenure_months = st.sidebar.number_input(
        "Tenure (months)",
        min_value=1,
        max_value=600,
        value=48,
        step=1,
    )

    instalments_paid_default = st.sidebar.number_input(
        "Instalments already paid (months)",
        min_value=0,
        max_value=tenure_months - 1,
        value=0,
        step=1,
    )

    foreclosure_rate = st.sidebar.number_input(
        "Foreclosure Interest / Charges (% of outstanding principal)",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.1,
        format="%.2f",
    )

    gst_rate = st.sidebar.number_input(
        "GST on Foreclosure Interest / Charges (%)",
        min_value=0.0,
        max_value=100.0,
        value=18.0,
        step=0.1,
        format="%.2f",
    )

    st.sidebar.markdown("---")

    # Calculate button: only flips session_state.calculated
    calculate_btn = st.sidebar.button("Calculate")
    if calculate_btn:
        st.session_state.calculated = True

    # If never calculated yet, show hint and stop
    if not st.session_state.calculated:
        st.info("Set your parameters in the sidebar and click **Calculate**.")
        return

    # ----- Core calculations (run on every rerun once calculated is True) -----
    emi = calculate_emi(loan_amount, annual_interest, tenure_months)
    profile_df, schedule_df = compute_foreclosure_profile(
        loan_amount,
        annual_interest,
        tenure_months,
        emi,
        foreclosure_rate,
        gst_rate,
    )

    total_payable_full = schedule_df["EMI"].sum()
    total_interest_full = total_payable_full - loan_amount

    # ----- High-level metrics -----
    st.subheader("High-level Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly EMI", f"₹{emi:,.2f}")
    with col2:
        st.metric("Total Interest (Full Tenure)", f"₹{total_interest_full:,.2f}")
    with col3:
        st.metric("Total Payable (P + Interest)", f"₹{total_payable_full:,.2f}")

    st.markdown("---")

    # ----- Interactive focus month selection -----
    st.subheader("Select Foreclosure Month for Detailed Snapshot")

    focus_month = st.slider(
        "Foreclosure month (after paying this many EMIs)",
        min_value=0,
        max_value=int(profile_df["Foreclosure_Month"].max()),
        value=int(instalments_paid_default),
        step=1,
    )

    current_row = profile_df[
        profile_df["Foreclosure_Month"] == focus_month
    ].iloc[0]

    outstanding_now = current_row["Outstanding_Principal"]
    foreclosure_charges_base = current_row["Foreclosure_Charges"]
    foreclosure_gst_base = current_row["GST_on_Charges"]
    remaining_if_no_foreclose_now = current_row[
        "Amount_Remaining_if_No_Foreclosure"
    ]
    total_paid_till_now = current_row["Total_Paid_Till_Month"]

    interest_paid_till_now = total_paid_till_now - (
        loan_amount - outstanding_now
    )

    # ----- Quick what‑if on charges (local override) -----
    st.markdown("### Quick What‑If on Charges (local override)")

    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
    with col_f1:
        local_foreclosure_rate = st.slider(
            "Override Foreclosure % (optional)",
            min_value=0.0,
            max_value=max(100.0, foreclosure_rate * 2),
            value=float(foreclosure_rate),
            step=0.25,
            help="Temporarily explore a different foreclosure charge percentage.",
        )
    with col_f2:
        local_gst_rate = st.slider(
            "Override GST % (optional)",
            min_value=0.0,
            max_value=max(100.0, gst_rate * 2),
            value=float(gst_rate),
            step=0.25,
            help="Temporarily explore a different GST rate on foreclosure charges.",
        )
    with col_f3:
        st.caption(
            "These sliders only affect the snapshot below for the selected month; "
            "they don't recalculate the full profile."
        )

    # Recompute snapshot with local overrides
    local_foreclosure_charges_now = outstanding_now * local_foreclosure_rate / 100
    local_foreclosure_gst_now = (
        local_foreclosure_charges_now * local_gst_rate / 100
    )
    local_foreclosure_final_now = (
        outstanding_now + local_foreclosure_charges_now + local_foreclosure_gst_now
    )
    local_net_savings_now = (
        remaining_if_no_foreclose_now - local_foreclosure_final_now
    )

    # ----- Foreclosure snapshot metrics -----
    st.subheader(
        f"Foreclosure Snapshot After {focus_month} Month(s) of EMI Payment"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            label="Outstanding Principal (without charges)",
            value=f"₹{outstanding_now:,.2f}",
        )
        st.caption(
            f"Principal still to be repaid at the time of foreclosure (month {focus_month})."
        )

    with c2:
        st.metric(
            label="Foreclosure Charges",
            value=f"₹{local_foreclosure_charges_now:,.2f}",
            delta=f"{local_foreclosure_rate:.2f}%",
        )
        st.caption(
            "Charges calculated as a percentage of outstanding principal "
            f"(base: ₹{foreclosure_charges_base:,.2f})."
        )

    with c3:
        st.metric(
            label="GST on Foreclosure Charges",
            value=f"₹{local_foreclosure_gst_now:,.2f}",
            delta=f"{local_gst_rate:.2f}%",
        )
        st.caption(
            "GST applied on foreclosure charges "
            f"(base: ₹{foreclosure_gst_base:,.2f})."
        )

    with c4:
        st.metric(
            label="Foreclosure Final Amount",
            value=f"₹{local_foreclosure_final_now:,.2f}",
        )
        st.caption(
            "Total one-shot amount to close the loan now, including charges and GST."
        )

    d1, d2, d3 = st.columns(3)
    with d1:
        st.metric(
            "Total Paid Till Now (EMIs)",
            f"₹{total_paid_till_now:,.2f}",
        )
    with d2:
        st.metric(
            "Interest Paid Till Now",
            f"₹{interest_paid_till_now:,.2f}",
        )
    with d3:
        st.metric(
            "Remaining Payable if No Foreclosure",
            f"₹{remaining_if_no_foreclose_now:,.2f}",
        )

    st.markdown("### Net impact if you foreclose in this month")

    if local_net_savings_now >= 0:
        st.success(
            f"Net Savings vs Not Foreclosing: **₹{local_net_savings_now:,.2f}** "
            "- foreclosing is beneficial at this point under current charges."
        )
    else:
        st.error(
            f"Net Savings vs Not Foreclosing: **₹{local_net_savings_now:,.2f}** "
            "- foreclosing costs more than continuing EMIs under current charges."
        )

    # ----- Comparison chart: Foreclose now vs continue -----
    st.subheader("Foreclose Now vs Continue (This Month)")

    compare_fig = go.Figure(
        data=[
            go.Bar(
                name="Pay if Continue",
                x=["Scenario"],
                y=[remaining_if_no_foreclose_now],
                marker_color="steelblue",
            ),
            go.Bar(
                name="Pay if Foreclose Now",
                x=["Scenario"],
                y=[local_foreclosure_final_now],
                marker_color="seagreen",
            ),
        ]
    )
    compare_fig.update_layout(
        barmode="group",
        yaxis_title="Amount (₹)",
        title="Remaining Outflow Comparison",
        legend_title="Option",
    )
    st.plotly_chart(compare_fig, use_container_width=True)

    st.markdown("---")

    # ----- Amortization schedule and EMI breakdown -----
    st.subheader("Amortization Schedule & EMI Breakdown")

    with st.expander("View Detailed Amortization Table"):
        st.dataframe(
            schedule_df.style.format(
                {
                    "Opening_Balance": "₹{:,.2f}".format,
                    "EMI": "₹{:,.2f}".format,
                    "Interest": "₹{:,.2f}".format,
                    "Principal": "₹{:,.2f}".format,
                    "Closing_Balance": "₹{:,.2f}".format,
                }
            ),
            use_container_width=True,
        )

    fig_emi_breakdown = px.area(
        schedule_df,
        x="Month",
        y=["Interest", "Principal"],
        title="EMI Break-up Over Time (Interest vs Principal)",
        labels={"value": "Amount (₹)", "variable": "Component"},
    )
    fig_emi_breakdown.update_layout(hovermode="x unified")
    st.plotly_chart(fig_emi_breakdown, use_container_width=True)

    # ----- Outstanding principal curve -----
    st.subheader("Outstanding Principal Over Time")

    fig_outstanding = px.line(
        schedule_df,
        x="Month",
        y="Closing_Balance",
        title="Outstanding Principal vs Month",
        labels={"Closing_Balance": "Outstanding Principal (₹)"},
    )
    fig_outstanding.update_traces(line=dict(color="royalblue"))
    st.plotly_chart(fig_outstanding, use_container_width=True)

    # ----- Foreclosure savings chart across months -----
    st.subheader("Net Savings from Foreclosing at Different Months")

    fig_savings = px.line(
        profile_df,
        x="Foreclosure_Month",
        y="Net_Savings_vs_No_Foreclosure",
        title="Net Savings vs Foreclosure Month",
        labels={
            "Foreclosure_Month": "Month of Foreclosure (after paying this many EMIs)",
            "Net_Savings_vs_No_Foreclosure": "Net Savings (₹)",
        },
    )
    fig_savings.add_vline(
        x=focus_month,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Selected month: {focus_month}",
        annotation_position="top left",
    )
    fig_savings.update_layout(hovermode="x unified")
    st.plotly_chart(fig_savings, use_container_width=True)

    with st.expander("Foreclosure Profile Table (All Months)"):
        st.dataframe(
            profile_df.style.format(
                {
                    "Outstanding_Principal": "₹{:,.2f}".format,
                    "Foreclosure_Charges": "₹{:,.2f}".format,
                    "GST_on_Charges": "₹{:,.2f}".format,
                    "Foreclosure_Final_Amount": "₹{:,.2f}".format,
                    "Amount_Remaining_if_No_Foreclosure": "₹{:,.2f}".format,
                    "Net_Savings_vs_No_Foreclosure": "₹{:,.2f}".format,
                    "Total_Paid_Till_Month": "₹{:,.2f}".format,
                }
            ),
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
