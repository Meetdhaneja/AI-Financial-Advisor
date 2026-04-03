# Personal Spending Dataset EDA Report

## 1. Dataset Overview

- Source file analyzed: `monthly_spending_dataset_2020_2025.csv`
- Record count: `69` monthly observations
- Date range: `2020-01-01` to `2025-09-01`
- Granularity: monthly
- Missing values: none detected in any column

Columns:

- `Month`
- `Groceries`
- `Rent`
- `Transportation`
- `Gym`
- `Utilities`
- `Healthcare`
- `Investments`
- `Savings`
- `EMI/Loans`
- `Dining & Entertainment`
- `Shopping & Wants`
- `Total Expenditure`
- `Income`

## 2. Data Quality And Structure

### 2.1 Important Accounting Rule

The biggest structural finding is:

`Total Expenditure = sum(all categories except Savings)`

This relationship holds for all 69 rows.

Interpretation:

- `Savings` is tracked separately from expenditure.
- `Investments` are included inside `Total Expenditure`.
- If this dataset is used in a product, the app should not treat `Savings` as spending.

### 2.2 Dataset Shape

This appears to be a curated or synthetic personal-finance dataset rather than raw bank transaction data.

Signals:

- No missing values
- Perfect monthly cadence
- Income appears in a small set of stepwise values: `36000, 40000, 43200, 48000, 56000, 64000`
- Category values are smooth and well-behaved

This is useful for prototyping and modeling, but it is not fully representative of messy real-world personal finance data.

## 3. High-Level Financial Summary

### 3.1 Overall Totals

- Total income: `₹34,80,800`
- Total expenditure: `₹25,32,579`
- Total surplus: `₹9,48,221`

### 3.2 Monthly Averages

- Average monthly income: `₹50,446`
- Average monthly expenditure: `₹36,704`
- Average monthly surplus: `₹13,742`
- Average expense-to-income ratio: `74.0%`

### 3.3 Best And Worst Months

- Highest expenditure month: `2024-06` at `₹49,167`
- Lowest expenditure month: `2020-06` at `₹28,791`
- Worst spending pressure month: `2020-07`, spending at `96.9%` of income
- Best spending pressure month: `2023-06`, spending at `58.8%` of income

## 4. Category Analysis

### 4.1 Category Totals Across Full Dataset

- Rent: `₹7,59,000`
- Savings: `₹5,25,266`
- Investments: `₹4,35,873`
- Groceries: `₹4,33,797`
- Dining & Entertainment: `₹1,89,032`
- Transportation: `₹1,77,279`
- Utilities: `₹1,36,544`
- Shopping & Wants: `₹1,35,499`
- Healthcare: `₹1,20,779`
- EMI/Loans: `₹78,000`
- Gym: `₹66,776`

### 4.2 Share Of Total Expenditure

Since `Savings` is not part of expenditure, the expenditure mix is best interpreted without it.

- Rent: about `30.1%`
- Investments: about `17.2%`
- Groceries: about `17.1%`
- Dining & Entertainment: about `7.6%`
- Transportation: about `7.1%`
- Utilities: about `5.5%`
- Shopping & Wants: about `5.4%`
- Healthcare: about `4.7%`
- EMI/Loans: about `2.4%`
- Gym: about `2.7%`

### 4.3 Monthly Spending Buckets

Average monthly amounts:

- Essentials (`Rent + Groceries + Utilities + Transportation + Healthcare + EMI`): `₹24,716`
- Discretionary (`Dining & Entertainment + Shopping & Wants + Gym`): `₹5,671`
- Future-focused (`Savings + Investments`): `₹13,930`

In the latest 12 months:

- Essentials average: `₹29,438`
- Discretionary average: `₹5,289`
- Future-focused average: `₹18,296`

This suggests that over time the budget expanded mainly in essentials and long-term allocations, not lifestyle inflation.

## 5. Trend Analysis

### 5.1 Income vs Expenditure

Comparing the first 12 months with the latest 12 months:

- Income increased by about `74.5%`
- Total expenditure increased by about `33.6%`

This is a healthy long-term trend. Income growth materially outpaced expenditure growth.

### 5.2 Category Growth

First 12 months vs latest 12 months:

- Savings: `+96.8%`
- Investments: `+72.2%`
- Groceries: `+32.8%`
- Rent: `+30.0%`
- Transportation: `-4.0%`
- Dining & Entertainment: `-4.9%`
- Shopping & Wants: `-1.0%`

Interpretation:

- The household became more future-oriented over time.
- Discretionary categories stayed flat or slightly declined.
- Core living costs increased, especially rent and groceries.

### 5.3 Yearly Progression

Average monthly income by year:

- 2020: `₹36,667`
- 2021: `₹41,400`
- 2022: `₹48,000`
- 2023: `₹54,000`
- 2024: `₹62,000`
- 2025 YTD: `₹64,000`

Average monthly expenditure by year:

- 2020: `₹32,041`
- 2021: `₹32,666`
- 2022: `₹33,907`
- 2023: `₹34,402`
- 2024: `₹47,052`
- 2025 YTD: `₹41,308`

Surplus rate by year:

- 2020: `12.6%`
- 2021: `21.1%`
- 2022: `29.4%`
- 2023: `36.3%`
- 2024: `24.1%`
- 2025 YTD: `35.5%`

Interpretation:

- Financial health improves steadily from 2020 to 2023.
- 2024 is a stress year with a noticeable expense jump.
- 2025 recovers well, showing stronger control or normalization after 2024.

## 6. Volatility And Stability

Most stable categories:

- Rent
- Utilities
- Gym
- Groceries

More volatile categories:

- Healthcare
- Savings
- Shopping & Wants
- Dining & Entertainment

Special case:

- `EMI/Loans` is extremely volatile because it is zero for most of the dataset and appears heavily in 2024.

Interpretation:

- Rent is highly predictable and ideal for baseline budgeting models.
- Healthcare and discretionary categories need more flexible forecasting bands.
- EMI should be modeled as an episodic commitment rather than a stable monthly cost.

## 7. Correlation With Income

Categories most positively correlated with income:

- Investments: `0.856`
- Rent: `0.820`
- Savings: `0.806`
- Total expenditure: `0.805`
- Healthcare: `0.593`
- Groceries: `0.574`

Categories with weak or near-zero relationship to income:

- Shopping & Wants: `0.015`
- Gym: `0.051`
- Utilities: `0.048`
- Dining & Entertainment: `-0.051`
- Transportation: `-0.120`

Interpretation:

- As income rises, the strongest behavioral response is increased investing and saving.
- Lifestyle categories do not scale much with income in this dataset.
- This profile represents a financially disciplined user rather than a highly consumption-driven one.

## 8. Seasonality And Outliers

### 8.1 Seasonality

Average expenditure by calendar month is fairly stable.

- Highest average spending month: December, about `₹37,807`
- Lowest average spending month: November, about `₹35,776`

Seasonality is mild. There is no strong festival- or travel-shaped spike pattern in the data.

### 8.2 Outlier Period

The main outlier cluster is `2024-01` through `2025-01`, especially:

- `2024-01`
- `2024-03`
- `2024-05`
- `2024-06`
- `2024-09`
- `2024-12`
- `2025-01`

These months are elevated mostly because of:

- Higher rent level
- Higher groceries
- Higher investments
- Introduction of EMI/Loans in 2024
- Higher healthcare in parts of 2024

## 9. What This Means For An AI Financial Advisor

### 9.1 Product Opportunities Supported By This Dataset

This dataset is well-suited for building and demoing:

- Monthly budget summaries
- Spending category breakdowns
- Income vs expenditure tracking
- Savings and investment habit tracking
- Trend detection and simple forecasting
- Expense-to-income health scoring
- Alerts for unusually high spending months
- Personalized recommendations based on category drift

### 9.2 Features The AI Advisor Should Definitely Support

#### Budget Health Layer

The advisor should compute:

- Expense-to-income ratio
- Savings rate
- Investment rate
- Essential vs discretionary split
- Surplus trend over time

These metrics explain financial health better than raw totals.

#### Category Intelligence

The advisor should identify:

- Largest cost drivers
- Rising categories over time
- Stable fixed obligations vs flexible spending
- One-off anomalies like the EMI spike in 2024

#### Behavioral Coaching

This dataset supports advice such as:

- Income increased faster than spending, which is positive
- Savings and investments are trending well
- 2024 looks like a financial stress year that deserves explanation
- Discretionary spending is relatively controlled, so optimization may matter more in essentials and debt planning

#### Forecasting

Simple forecast targets can be generated for:

- Next month total expenditure
- Next month savings range
- Future surplus if current behavior continues
- What-if scenarios for rent, EMI, or grocery inflation

### 9.3 Schema Recommendations Before Using This In Production

For a stronger AI financial advisor, the data model should ideally be expanded with:

- Real transaction-level data instead of monthly aggregates only
- Merchant names
- Payment mode
- Cash vs card vs UPI
- Location
- Category hierarchies and subcategories
- Goal metadata for savings and investments
- Debt account details for EMI
- Labels for recurring vs one-time expenses
- Ground-truth financial goals and user preferences

Without these, the advisor can summarize and coach, but not deeply explain causal behavior.

### 9.4 Modeling Cautions

If you use this dataset for ML or product demos:

- Do not treat `Savings` as expenditure
- Treat `EMI/Loans` as a regime change beginning in 2024
- Be careful with forecasting across the 2024 shift because the behavior pattern changes
- Avoid assuming this distribution represents all users; it reflects one financially improving profile
- Expect weaker generalization because the dataset is small and highly regular

## 10. Recommended Next Steps For This Project

Best immediate uses of this dataset in your AI financial advisor:

1. Build a monthly financial health dashboard.
2. Add natural-language insights like "Your essentials rose faster than discretionary spending."
3. Create anomaly alerts for expense spikes and EMI onset.
4. Add savings and investment coaching as a separate layer from spending analysis.
5. Use simple forecasting first, then only move to ML once you have richer data.

## 11. Final Assessment

This is a solid dataset for prototyping an AI financial advisor because it is:

- clean,
- interpretable,
- time-based,
- category-rich,
- and financially meaningful.

Its main limitation is realism. It is excellent for demonstrating budgeting, trend analysis, and recommendation logic, but limited for production-grade personalization unless you supplement it with transaction-level behavioral data.
