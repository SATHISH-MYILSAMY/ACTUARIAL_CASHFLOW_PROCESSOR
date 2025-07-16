import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Actuarial Cashflow Processor", layout="wide")
st.title("Actuarial Cashflow Processor (AInsurCo Assessment)")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        raw_df = pd.read_excel(uploaded_file, sheet_name='Inputs', header=None)

        expected_cols = ["Eff. Dt.", "Description", "Tranche", "Fund", "Price", "Amount", "No. of Units"]

        header_row_index = None
        for i in range(10):
            row = raw_df.iloc[i].astype(str).str.strip().tolist()
            if all(col in row for col in expected_cols):
                header_row_index = i
                break

        if header_row_index is None:
            st.error("Unable to detect header row. Please check your file.")
            st.stop()

        headers = raw_df.iloc[header_row_index].astype(str).str.strip()
        data_df = raw_df.iloc[header_row_index + 1:].copy()
        data_df.columns = headers
        data_df = data_df.reset_index(drop=True)

        st.write("Detected Columns:", list(data_df.columns))

        if not all(col in data_df.columns for col in expected_cols):
            st.error(f"Missing expected columns: {expected_cols}")
            st.stop()

        data_df["Eff. Dt."] = pd.to_datetime(data_df["Eff. Dt."], errors='coerce')
        data_df.dropna(subset=["Eff. Dt."], inplace=True)

        st.subheader("Select Reporting Period")
        min_date = data_df["Eff. Dt."].min()
        max_date = data_df["Eff. Dt."].max()
        start_date = st.date_input("Start Date", value=min_date.date(), min_value=min_date.date(), max_value=max_date.date())
        end_date = st.date_input("End Date", value=max_date.date(), min_value=min_date.date(), max_value=max_date.date())

        reporting_df = data_df[(data_df["Eff. Dt."] >= pd.to_datetime(start_date)) &
                               (data_df["Eff. Dt."] <= pd.to_datetime(end_date))].copy()

        st.subheader("Data Preview")
        st.dataframe(reporting_df, use_container_width=True)

        previous_df = data_df[data_df["Eff. Dt."] < pd.to_datetime(start_date)].copy()
        latest_prices = previous_df.sort_values("Eff. Dt.").groupby(["Tranche", "Fund"])["Price"].last()

        output_rows = []

        for key, group in reporting_df.groupby(["Tranche", "Fund"]):
            tranche, fund = key
            filtered = group.copy()

            opening_units = previous_df[(previous_df["Tranche"] == tranche) &
                                        (previous_df["Fund"] == fund)]["No. of Units"].sum()
            opening_price = latest_prices.get(key, 0)
            opening_balance = opening_units * opening_price

            transfers_in = filtered[filtered["Description"].str.contains("Buy Units : Transfer In", na=False)]["Amount"].sum()
            charges = filtered[filtered["Description"].str.contains("AMC|FBC|Sell Units : AMC|Sell Units : FBC", na=False)]["Amount"].sum()
            imputed = filtered[filtered["Description"].str.contains("Sell Units : Imputed Distribution", na=False)]["Amount"].sum()
            vsa = filtered[filtered["Description"].str.contains("Buy Units : VSA", na=False)]["Amount"].sum()
            normal_withdrawals = filtered[filtered["Description"].str.contains("Sell Units : Withdrawal", na=False)]["Amount"].sum()
            reg_encash = filtered[filtered["Description"].str.contains("Sell Units : Reg.Enc", na=False)]["Amount"].sum()

            closing_units = filtered[filtered["Tranche"] == tranche]["No. of Units"].sum()
            closing_price = filtered[filtered["Tranche"] == tranche]["Price"].iloc[-1] if not filtered.empty else 0
            closing_balance = closing_units * closing_price

            inflow_outflow = transfers_in + imputed + vsa - charges - normal_withdrawals - reg_encash
            investment_growth = closing_balance - (opening_balance + inflow_outflow)

            output_rows.append({
                "Tranche": tranche,
                "Fund": fund,
                "Opening Balance": round(opening_balance, 2),
                "Transfers In": round(transfers_in, 2),
                "Policy Charges": round(charges, 2),
                "Imputed Distribution": round(imputed, 2),
                "ValueShare Additions": round(vsa, 2),
                "Normal Withdrawals": round(normal_withdrawals, 2),
                "Regular Encashments": round(reg_encash, 2),
                "Closing Balance": round(closing_balance, 2),
                "Investment Growth": round(investment_growth, 2)
            })

        result_df = pd.DataFrame(output_rows)

        st.subheader("Computed Cashflow Report")
        st.dataframe(result_df, use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_df.to_excel(writer, index=False, sheet_name="Unit Movements - From Start")
        output.seek(0)

        st.download_button(
            label="Download Output as Excel",
            data=output,
            file_name="unit_movements_from_start.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload your Excel file to begin.")
