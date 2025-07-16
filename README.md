# Actuarial Cashflow Processor – AInsurCo Assessment Tool

A web-based application built using Streamlit for processing and analyzing actuarial cashflows from Excel files. This tool extracts unit movement data, performs detailed investment computations, and generates clean output reports for insurance or actuarial reporting purposes.

---

## 🚀 Features

- Upload Excel file with cashflow data
- Detects and reads custom-formatted headers from the "Inputs" sheet
- Allows selection of a reporting period based on effective dates
- Filters and computes unit-based financial movements including:
  - Transfers In
  - Policy Charges (AMC/FBC)
  - Imputed Distributions
  - ValueShare Additions (VSA)
  - Normal Withdrawals
  - Regular Encashments
  - Opening & Closing Balances
  - Investment Growth
- Outputs clean summary reports with download option (Excel format)

---

## 📁 File Format Expectations

- Input file must contain a sheet named `Inputs`
- Expected columns:  
  `Eff. Dt.`, `Description`, `Tranche`, `Fund`, `Price`, `Amount`, `No. of Units`
- The tool intelligently detects header location within the first 10 rows

---

## 🖥️ Tech Stack

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/)

---
