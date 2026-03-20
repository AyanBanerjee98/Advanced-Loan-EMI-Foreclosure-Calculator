# Advanced Loan / EMI & Foreclosure Calculator

A comprehensive web-based tool built with **Streamlit** to calculate EMI (Equated Monthly Installment), analyze loan amortization schedules, and evaluate the financial impact of loan foreclosure at different time points.

## 📋 Features

### Core Calculations
- **EMI Calculation**: Computes monthly EMI using the reducing-balance method
- **Amortization Schedule**: Generates month-by-month breakdown of:
  - Opening & closing balances
  - Interest paid
  - Principal paid
  - EMI amount
- **Foreclosure Analysis**: Evaluates the cost-benefit of foreclosing at any point during the loan tenure

### Interactive Features
- **Real-time Adjustments**: Modify loan parameters and instantly see results
- **What-If Scenarios**: Test different foreclosure charges and GST rates without recalculating the full profile
- **Visual Analytics**:
  - EMI breakdown (Interest vs Principal over time)
  - Outstanding principal curve
  - Net savings from foreclosure at different months
  - Side-by-side comparison (Foreclose vs Continue)

### Detailed Insights
- Total interest payable over full tenure
- Outstanding principal at any given month
- Foreclosure charges calculation
- GST on foreclosure charges
- Net savings/cost of foreclosing vs continuing with EMIs

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AyanBanerjee98/Advanced-Loan-EMI-Foreclosure-Calculator.git
   cd Advanced-Loan-EMI-Foreclosure-Calculator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   If `requirements.txt` doesn't exist, install manually:
   ```bash
   pip install streamlit pandas plotly
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

   The app will open in your default browser at `http://localhost:8501`

## 📖 How to Use

### Step 1: Enter Loan Parameters (Sidebar)
- **Loan Amount (Principal)**: The initial loan amount in rupees
- **Annual Interest Rate (%)**: Your yearly interest rate (e.g., 13.5%)
- **Tenure (months)**: Total loan duration in months
- **Instalments Already Paid**: How many EMIs you've already paid (for mid-tenure analysis)
- **Foreclosure Interest/Charges (%)**: Penalty as % of outstanding principal
- **GST on Foreclosure Interest (%)**: Tax on foreclosure charges (typically 18%)

### Step 2: Click "Calculate"
The app processes all calculations and displays results.

### Step 3: Explore Results

#### Summary Section
- Monthly EMI amount
- Total interest payable over the full tenure
- Total amount payable (Principal + Interest)

#### Foreclosure Analysis
1. **Select a Month**: Use the slider to pick the month at which you want to foreclose
2. **What-If Adjustments**: Temporarily adjust foreclosure % and GST % to see impact
3. **View Snapshot**: See detailed metrics for the selected month:
   - Outstanding principal
   - Foreclosure charges
   - GST amount
   - Total foreclosure payment
   - Savings comparison

#### Visualizations
- **Amortization Table**: Detailed month-by-month breakdown
- **EMI Breakdown Chart**: Visual split of interest vs principal over time
- **Outstanding Principal Curve**: How your outstanding balance decreases
- **Foreclosure Savings Chart**: Net savings at each possible foreclosure month
- **Comparison Bar Chart**: Side-by-side comparison of continuing vs foreclosing

## 🧮 Calculation Methodology

### EMI Formula (Reducing Balance)
```
Monthly Rate = Annual Rate / 12 / 100
EMI = (Principal × Monthly Rate × (1 + Monthly Rate)^n) / ((1 + Monthly Rate)^n - 1)
```
Where `n` = number of months

### Foreclosure Cost
```
Foreclosure Charges = Outstanding Principal × Foreclosure Rate / 100
GST on Charges = Foreclosure Charges × GST Rate / 100
Foreclosure Final Amount = Outstanding Principal + Foreclosure Charges + GST
```

### Net Savings
```
Net Savings = (Remaining EMIs if No Foreclosure) - (Foreclosure Final Amount)
```
- **Positive value**: Foreclosing saves money
- **Negative value**: Foreclosing costs more than continuing

## 📊 Example Scenario

**Loan Details:**
- Principal: ₹5,00,000
- Annual Rate: 13.5%
- Tenure: 48 months
- Foreclosure Rate: 5%
- GST: 18%

**Results (after 24 months):**
- Monthly EMI: ₹12,500
- Outstanding Principal: ₹2,50,000
- Foreclosure Charges: ₹12,500
- Total Foreclosure Amount: ₹14,750 (with GST)
- Remaining EMIs: ₹1,50,000
- **Net Savings: ₹1,35,250** (beneficial to foreclose)

## 🔧 Technical Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Data Processing | pandas |
| Visualization | Plotly Express & Plotly Graph Objects |
| Language | Python 3.8+ |

## 📁 Project Structure

```
Advanced-Loan-EMI-Foreclosure-Calculator/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎯 Key Functions

### `calculate_emi(principal, annual_rate, tenure_months)`
Calculates the monthly EMI using the reducing-balance method.

### `build_amortization_schedule(principal, annual_rate, tenure_months, emi)`
Generates a month-by-month amortization table with all details.

### `compute_foreclosure_profile(principal, annual_rate, tenure_months, emi, foreclosure_rate, gst_rate)`
Computes foreclosure viability for all possible foreclosure months.

## ⚠️ Important Notes

1. **Calculations assume reducing-balance interest**: This is the standard method used by most Indian lenders
2. **Rounding handling**: The calculator adjusts the final payment to avoid negative balances due to rounding errors
3. **What-If sliders**: Local overrides only affect the snapshot for the selected month; they don't recalculate the full profile
4. **Session state**: The app remembers your calculation status during a session

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Improve documentation
- Optimize calculations

## 📝 License

This project is open source and available under the MIT License.

## 💡 Tips for Best Results

1. **Accurate Input**: Ensure your loan parameters are precise for accurate calculations
2. **Mid-tenure Analysis**: Use "Instalments already paid" if you want to analyze from your current loan position
3. **Scenario Testing**: Use the what-if sliders to explore different foreclosure scenarios before deciding
4. **Export Data**: You can copy tables directly from the app for further analysis in Excel

## 🐛 Known Limitations

- Does not account for late-payment penalties or other charges
- Assumes fixed interest rate (no floating rate scenarios)
- Does not include prepayment options for partial payments
- GST calculation is simplified; actual may vary by region/lender

## 📧 Contact & Support

For questions, issues, or suggestions, please open an issue on the repository or contact the maintainer.

---

**Made with ❤️ by Ayan Banerjee**