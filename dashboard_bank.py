import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime
import re
from streamlit_echarts import st_echarts
from io import BytesIO
#from st_pages import Page, add_page_title, show_pages
import gspread
from google.oauth2.service_account import Credentials
from shillelagh.backends.apsw.db import connect


def fetch_google_sheet(sheet_url):
    csv_url = sheet_url.replace('/edit?gid=', '/export?format=csv&gid=')
    return pd.read_csv(csv_url)

# Google Sheet URL (public link)
google_sheet_url = "https://docs.google.com/spreadsheets/d/1-mHPo2LDptjhvlgXe_-r-yucxQRink_Wfy1HhH2oR4s/edit?gid=1684401121#gid=1684401121"

st.set_page_config(layout="wide", page_title="Daily dashboard", page_icon="https://companieslogo.com/img/orig/VPB.VN-b0a9916f.png?t=1722928514", menu_items={
        'Get Help': 'mailto:anhhungtrinh95@gmail.com',
        'Report a bug': "https://docs.google.com/spreadsheets/d/1-mHPo2LDptjhvlgXe_-r-yucxQRink_Wfy1HhH2oR4s/edit?gid=741377359#gid=741377359",
        'About': "# Seller Capabilities. This is an :red[internal] used only app!"})
col1, col2 = st.columns([6, 1])
col1.title('Banking customer Dashboard')

try:
    data = fetch_google_sheet(google_sheet_url)
    
    # Extract the 'Data_date' from the column
    if 'Data_date' in data.columns:
        update_date = pd.to_datetime(data['Data_date']).max()  # Get the latest date from the column
        col1.caption(f"Data updated successfully on: {update_date.strftime('_:green[%Y-%m-%d]_')}")
    else:
        col1.caption("Data last updated on: Not available (no `data_date` column found)")

except Exception as e:
    col1.error(f"Failed to load data: {e}")
    data = None
col2.image(image="https://brandlogos.net/wp-content/uploads/2021/09/vpbank-logo-svg.svg",width=200)

    # Create "Raw Data" section
    # Function to generate recommendations

tab1, tab2 = st.tabs(["Seller Dashboard", "Help!"])

#visualise dashboard
st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

seller_data = data["Cus_ID"].unique() if "Cus_ID" in data.columns else []
date_data = data["Data_date"].unique() if "Data_date" in data.columns else []
data["Month"] = data["Month"].astype(str)

with tab1:
    with st.container():
        col1, col2 = st.columns([1, 1])
    with col1:
                    # Dropdown to select shopid
                    selected_shopid = st.selectbox('🆔 Select a Customer', seller_data)

    with col2:
                    # Dropdown to select date
                        date_range = st.selectbox("📅 Select a date", date_data)

    st.text("") #Create space between part
    
    if selected_shopid:
        # Filter data for the selected Shop_ID
        shop_data = data[data["Cus_ID"] == selected_shopid]
        # Apply the `calculate_overall_tier` function to compute `overall_tier` for the dataset
        if not shop_data.empty:
            # Determine current and previous closest dates
            current_date = date_range
            previous_data = shop_data[shop_data["Data_date"] < current_date]
            previous_date = previous_data["Data_date"].max() if not previous_data.empty else None

            if current_date:
                # Current data
                current_data = shop_data[shop_data["Data_date"] == current_date].iloc[0]

                # Previous data
                last_date_data = previous_data[previous_data["Data_date"] == previous_date].iloc[0] if previous_date else None

                # Extract dynamic header information
                Cus_name = current_data["Cus_name"] if "Cus_name" in current_data else "N/A"
                category = current_data["Category"] if "Category" in current_data else "N/A"
                Cus_type = current_data["Cus_type"] if "Cus_type" in current_data else "N/A"
                bd_pic = current_data["BD_pic"] if "BD_pic" in current_data else "N/A"

                # Extract infomation metrics
                Pr1_Loan = current_data["Pr1_Loan"] if "Pr1_Loan" in current_data else None
                Pr2_Deposit = current_data["Pr2_Deposit"] if "Pr2_Deposit" in current_data else None
                Pr3_Card = current_data["Pr3_Card"] if "Pr3_Card" in current_data else None
                Badbank_bucket = current_data["Badbank_bucket"] if "Badbank_bucket" in current_data else None
                Acc_latepayment = current_data["Acc_latepayment"] if "Acc_latepayment" in current_data else None
                overall_tier = current_data["Overall_tier"] if "Overall_tier" in current_data else None
                
                # Extract Loan metrics
                Acc_Loan = current_data["Acc_Loan"] if "Acc_Loan" in current_data else None
                New_Loan = current_data["New_Loan"] if "New_Loan" in current_data else None
                LT_Loan = current_data["LT_Loan"] if "LT_Loan" in current_data else None
                ST_Loan = current_data["ST_Loan"] if "ST_Loan" in current_data else None
                TOI_Loan = current_data["TOI_Loan"] if "TOI_Loan" in current_data else None

                # Extract Deposit metrics
                Acc_Deposit = current_data["Acc_Deposit"] if "Acc_Deposit" in current_data else None
                New_Deposit = current_data["New_Deposit"] if "New_Deposit" in current_data else None
                ST_Deposit = current_data["ST_Deposit"] if "ST_Deposit" in current_data else None
                LT_Deposit = current_data["LT_Deposit"] if "LT_Deposit" in current_data else None
                CASA = current_data["CASA"] if "CASA" in current_data else None
                Deposit_wd = current_data["Deposit_wd"] if "Deposit_wd" in current_data else None

                # Extract Card metrics
                Acc_Card = current_data["Acc_Card"] if "Acc_Card" in current_data else None
                New_card = current_data["New_card"] if "New_card" in current_data else None
                Card_close = current_data["Card_close"] if "Card_close" in current_data else None
                Card_rep = current_data["Card_rep"] if "Card_rep" in current_data else None
                Card_tran = current_data["Card_tran"] if "Card_tran" in current_data else None


                # Helper function to calculate delta with late payment special case
                def calculate_delta(current, previous):
                    try:
                        # Convert strings to floats for calculation
                        current = float(current) if current is not None else None
                        previous = float(previous) if previous is not None else None

                        if current is None:
                            return "No data"
                        if previous is None:
                            return "100% growth"  # Assume full growth when no previous data
                        if previous == 0 and current == 0:
                            return "No occurrence "  # Special case for late payment
                        if previous == 0:
                            return "100% growth"  # Handle division by zero

                        # Calculate percentage growth
                        return f"{int(((current - previous) / previous) * 100)}% MOM"
                    except (ValueError, TypeError):
                        return "No data"  # Handle invalid or non-numeric data
                        
                # Calculate deltas for metrics
                pr1_loan_delta = calculate_delta(
                    Pr1_Loan, last_date_data["Pr1_Loan"] if last_date_data is not None and "Pr1_Loan" in last_date_data else None
                )
                pr2_deposit_delta = calculate_delta(
                    Pr2_Deposit, last_date_data["Pr2_Deposit"] if last_date_data is not None and "Pr2_Deposit" in last_date_data else None
                )
                pr3_card_delta = calculate_delta(
                    Pr3_Card, last_date_data["Pr3_Card"] if last_date_data is not None and "Pr3_Card" in last_date_data else None
                )
                acc_latepayment_delta = calculate_delta(
                    Acc_latepayment, last_date_data["Acc_latepayment"] if last_date_data is not None and "Acc_latepayment" in last_date_data else None
                )
                # Calculate deltas for Loan metrics
                acc_loan_delta = calculate_delta(
                    Acc_Loan, last_date_data["Acc_Loan"] if last_date_data is not None and "Acc_Loan" in last_date_data else None
                )
                new_loan_delta = calculate_delta(
                    New_Loan, last_date_data["New_Loan"] if last_date_data is not None and "New_Loan" in last_date_data else None
                )
                ST_Loan_delta = calculate_delta(
                    ST_Loan, last_date_data["ST_Loan"] if last_date_data is not None and "ST_Loan" in last_date_data else None
                )
                LT_Loan_delta = calculate_delta(
                    ST_Loan, last_date_data["LT_Loan"] if last_date_data is not None and "LT_Loan" in last_date_data else None
                )
                TOI_Loan_delta = calculate_delta(
                    TOI_Loan, last_date_data["TOI_Loan"] if last_date_data is not None and "TOI_Loan" in last_date_data else None
                )

                # Calculate deltas for Deposit metrics
                acc_deposit_delta = calculate_delta(
                    Acc_Deposit, last_date_data["Acc_Deposit"] if last_date_data is not None and "Acc_Deposit" in last_date_data else None
                )
                new_deposit_delta = calculate_delta(
                    New_Deposit, last_date_data["New_Deposit"] if last_date_data is not None and "New_Deposit" in last_date_data else None
                )
                st_deposit_delta = calculate_delta(
                    ST_Deposit, last_date_data["ST_Deposit"] if last_date_data is not None and "ST_Deposit" in last_date_data else None
                )
                lt_deposit_delta = calculate_delta(
                    LT_Deposit, last_date_data["LT_Deposit"] if last_date_data is not None and "LT_Deposit" in last_date_data else None
                )
                casa_delta = calculate_delta(
                    CASA, last_date_data["CASA"] if last_date_data is not None and "CASA" in last_date_data else None
                )
                deposit_wd_delta = calculate_delta(
                    Deposit_wd, last_date_data["Deposit_wd"] if last_date_data is not None and "Deposit_wd" in last_date_data else None
                )

                # Calculate deltas for Card metrics
                acc_card_delta = calculate_delta(
                    Acc_Card, last_date_data["Acc_Card"] if last_date_data is not None and "Acc_Card" in last_date_data else None
                )
                new_card_delta = calculate_delta(
                    New_card, last_date_data["New_card"] if last_date_data is not None and "New_card" in last_date_data else None
                )
                card_close_delta = calculate_delta(
                    Card_close, last_date_data["Card_close"] if last_date_data is not None and "Card_close" in last_date_data else None
                )
                card_rep_delta = calculate_delta(
                    Card_rep, last_date_data["Card_rep"] if last_date_data is not None and "Card_rep" in last_date_data else None
                )
                card_tran_delta = calculate_delta(
                    Card_tran, last_date_data["Card_tran"] if last_date_data is not None and "Card_tran" in last_date_data else None
                )
                # Handle Badbank Bucket delta with color
                if last_date_data is not None and not last_date_data.empty and "Badbank_bucket" in last_date_data:
                    if Badbank_bucket > last_date_data["Badbank_bucket"]:
                        badbank_bucket_delta = f"Up from {last_date_data['Badbank_bucket']}"
                        badbank_bucket_color = "inverse"  # Red for increase
                    elif Badbank_bucket < last_date_data["Badbank_bucket"]:
                        badbank_bucket_delta = f"Down from {last_date_data['Badbank_bucket']}"
                        badbank_bucket_color = "normal"  # Green for decrease
                    else:
                        badbank_bucket_delta = "Maintain"
                        badbank_bucket_color = "off"  # Neutral
                else:
                    badbank_bucket_delta = "No data"
                    badbank_bucket_color = "off"  # Neutral

                # Handle Overall Tier delta
                if last_date_data is not None and not last_date_data.empty and "Overall_tier" in last_date_data:
                    if overall_tier < last_date_data["Overall_tier"]:
                        overall_tier_delta = f"Upgrade to {overall_tier}"
                    elif overall_tier > last_date_data["Overall_tier"]:
                        overall_tier_delta = f"Downgrade to {overall_tier}"
                    else:
                        overall_tier_delta = "Maintain tier"
                else:
                    overall_tier_delta = "No data"

                # Display Customer Information
                colored_header(':bookmark_tabs: Customer Information', description="Customer basic information", color_name="blue-green-70")
                st.markdown(f"📌:blue[{Cus_name}] | {category} | {Cus_type} | BD PIC: {bd_pic}")

                # Display Metrics
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns(6)

                    col1.metric(
                        label="Overall Tier",
                        value=overall_tier or "No data",
                        delta=overall_tier_delta,
                        delta_color="off"
                    )
                    col2.metric(
                        label="Loan Program 1",
                        value=f"{Pr1_Loan}%" if Pr1_Loan is not None else "No data",
                        delta=pr1_loan_delta,
                        delta_color="normal"
                    )
                    col3.metric(
                        label="Deposit Program 2",
                        value=f"{Pr2_Deposit}%" if Pr2_Deposit is not None else "No data",
                        delta=pr2_deposit_delta,
                        delta_color="normal"
                    )
                    col4.metric(
                        label="Card Program 3",
                        value=Pr3_Card if Pr3_Card is not None else "No data",
                        delta=pr3_card_delta,
                        delta_color="normal"
                    )
                    col5.metric(
                        label="Badbank Bucket",
                        value=Badbank_bucket if Badbank_bucket is not None else "No data",
                        delta=badbank_bucket_delta,
                        delta_color=badbank_bucket_color
                    )
                    col6.metric(
                        label="Late Payment",
                        value=Acc_latepayment if Acc_latepayment is not None else "No data",
                        delta=acc_latepayment_delta,
                        delta_color="normal"
                    )
                st.text("") #adding space
                colored_header(':one: Loan', description="Data about Cutomer Loan", color_name="blue-green-70")
               # Display Loan Metrics with Charts
                with st.container():
                    st.subheader("Loan Metrics")
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    
                    # Acc Loan
                    with col1:
                        col1.metric("Outstanding Loan", f"{int(Acc_Loan)}" if Acc_Loan is not None else "No data", acc_loan_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_acc_loan = shop_data[["Month", "Acc_Loan"]].dropna().sort_values("Month")
                            with chart_container(data_acc_loan):
                                st.area_chart(data_acc_loan, x="Month", y="Acc_Loan", use_container_width=True, height=150)
                    
                    # New Loan
                    with col2:
                        col2.metric("New Loan", f"{int(New_Loan)}" if New_Loan is not None else "No data", new_loan_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_new_loan = shop_data[["Month", "New_Loan"]].dropna().sort_values("Month")
                            with chart_container(data_new_loan):
                                st.area_chart(data_new_loan, x="Month", y="New_Loan", use_container_width=True, height=150)
                    
                    # LT Loan
                    with col3:
                        col3.metric("Long term Loan", f"{int(TOI_Loan)}" if LT_Loan is not None else "No data", LT_Loan_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_TOI_Loan = shop_data[["Month", "LT_Loan"]].dropna().sort_values("Month")
                            with chart_container(data_TOI_Loan):
                                st.area_chart(data_TOI_Loan, x="Month", y="LT_Loan", use_container_width=True, height=150)
                    
                    # ST Loan
                    with col4:
                        col4.metric("Short term Loan", f"{int(ST_Loan)}" if ST_Loan is not None else "No data", ST_Loan_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_ST_Loan = shop_data[["Month", "ST_Loan"]].dropna().sort_values("Month")
                            with chart_container(data_ST_Loan):
                                st.area_chart(data_ST_Loan, x="Month", y="ST_Loan", use_container_width=True, height=150)
                    
                    # RP Loan
                    with col5:
                        col5.metric("Repayment on Loan", f"{int(ST_Loan)}" if ST_Loan is not None else "No data", ST_Loan_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_ST_Loan = shop_data[["Month", "ST_Loan"]].dropna().sort_values("Month")
                            with chart_container(data_ST_Loan):
                                st.area_chart(data_ST_Loan, x="Month", y="ST_Loan", use_container_width=True, height=150)
                    
                    # TOI Loan
                    with col6:
                        col6.metric("TOI on Loan", f"{int(TOI_Loan)}" if TOI_Loan is not None else "No data", TOI_Loan_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_TOI_Loan = shop_data[["Month", "TOI_Loan"]].dropna().sort_values("Month")
                            with chart_container(data_TOI_Loan):
                                st.area_chart(data_TOI_Loan, x="Month", y="TOI_Loan", use_container_width=True, height=150)

                st.text("") #adding space
                                # Prepare data for the chart
                loan_chart_data = shop_data[["Month", "Acc_Loan", "New_Loan", "TOI_Loan", "ST_Loan", "LT_Loan", "RP_Loan"]].dropna().sort_values("Month")

                # Extract series data
                chart_months = loan_chart_data["Month"].tolist()
                acc_loan_gr = loan_chart_data["Acc_Loan"].astype(float).tolist()
                new_loan_gr = loan_chart_data["New_Loan"].astype(float).tolist()
                TOI_Loan_gr = loan_chart_data["TOI_Loan"].astype(float).tolist()
                st_loan_gr = loan_chart_data["ST_Loan"].astype(float).tolist()
                lt_loan_gr = loan_chart_data["LT_Loan"].astype(float).tolist()
                rp_loan_gr = loan_chart_data["RP_Loan"].astype(float).tolist()

                # Chart options
                loan_options = {
                    "title": {"text": "📊 Loan Metrics Trending"},
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
                    },
                    "legend": {"data": ["Outstanding Loan", "New Loan", "Long term Loan", "Short term Loan", "Repayment on Loan", "TOI on Loan"]},
                    "toolbox": {"feature": {"saveAsImage": {}}},
                    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                    "xAxis": [
                        {
                            "type": "category",
                            "boundaryGap": False,
                            "data": chart_months,
                        }
                    ],
                    "yAxis": [{"type": "value"}],
                    "series": [
                        {
                            "name": "Outstanding Loan",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": acc_loan_gr,
                        },
                        {
                            "name": "New Loan",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": new_loan_gr,
                        },
                        {
                            "name": "Long term Loan",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": TOI_Loan_gr,
                        },
                        {
                            "name": "Short term Loan",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": st_loan_gr,
                        },
                        {
                            "name": "Repayment on Loan",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": rp_loan_gr,
                        },
                    ],
                }

                # Render chart
                st_echarts(options=loan_options, height="400px")

                st.text("") #adding space
                colored_header(':two: Deposit', description="Data about Cutomer Deposit", color_name="blue-green-70")  
                # Display Deposit Metrics with Charts
                with st.container():
                    st.subheader("Deposit Metrics")
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    
                    # Acc Deposit
                    with col1:
                        col1.metric("Accumulate deposit", f"{int(Acc_Deposit)}" if Acc_Deposit is not None else "No data", acc_deposit_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_acc_deposit = shop_data[["Month", "Acc_Deposit"]].dropna().sort_values("Month")
                            with chart_container(data_acc_deposit):
                                st.area_chart(data_acc_deposit, x="Month", y="Acc_Deposit", use_container_width=True, height=150)
                    
                    # New Deposit
                    with col2:
                        col2.metric("New Deposit", f"{int(New_Deposit)}" if New_Deposit is not None else "No data", new_deposit_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_new_deposit = shop_data[["Month", "New_Deposit"]].dropna().sort_values("Month")
                            with chart_container(data_new_deposit):
                                st.area_chart(data_new_deposit, x="Month", y="New_Deposit", use_container_width=True, height=150)
                    
                    # ST Deposit
                    with col3:
                        col3.metric("Short term Deposit", f"{int(ST_Deposit)}" if ST_Deposit is not None else "No data", st_deposit_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_st_deposit = shop_data[["Month", "ST_Deposit"]].dropna().sort_values("Month")
                            with chart_container(data_st_deposit):
                                st.area_chart(data_st_deposit, x="Month", y="ST_Deposit", use_container_width=True, height=150)
                    
                    # LT Deposit
                    with col4:
                        col4.metric("Long term Deposit", f"{int(LT_Deposit)}" if LT_Deposit is not None else "No data", lt_deposit_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_lt_deposit = shop_data[["Month", "LT_Deposit"]].dropna().sort_values("Month")
                            with chart_container(data_lt_deposit):
                                st.area_chart(data_lt_deposit, x="Month", y="LT_Deposit", use_container_width=True, height=150)
                    
                    # CASA
                    with col5:
                        col5.metric("CASA", f"{int(CASA)}" if CASA is not None else "No data", casa_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_casa = shop_data[["Month", "CASA"]].dropna().sort_values("Month")
                            with chart_container(data_casa):
                                st.area_chart(data_casa, x="Month", y="CASA", use_container_width=True, height=150)
                    
                    # Deposit Withdrawals
                    with col6:
                        col6.metric("Deposit Withdrawals", f"{int(Deposit_wd)}" if Deposit_wd is not None else "No data", deposit_wd_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_deposit_wd = shop_data[["Month", "Deposit_wd"]].dropna().sort_values("Month")
                            with chart_container(data_deposit_wd):
                                st.area_chart(data_deposit_wd, x="Month", y="Deposit_wd", use_container_width=True, height=150)

                # Prepare data for the deposit chart
                deposit_chart_data = shop_data[["Month", "Acc_Deposit", "New_Deposit", "ST_Deposit", "LT_Deposit", "CASA", "Deposit_wd"]].dropna().sort_values("Month")

                # Extract series data
                chart_months = deposit_chart_data["Month"].tolist()
                acc_deposit_gr = deposit_chart_data["Acc_Deposit"].astype(float).tolist()
                new_deposit_gr = deposit_chart_data["New_Deposit"].astype(float).tolist()
                st_deposit_gr = deposit_chart_data["ST_Deposit"].astype(float).tolist()
                lt_deposit_gr = deposit_chart_data["LT_Deposit"].astype(float).tolist()
                casa_gr = deposit_chart_data["CASA"].astype(float).tolist()
                deposit_wd_gr = deposit_chart_data["Deposit_wd"].astype(float).tolist()

                # Chart options for deposits
                deposit_options = {
                    "title": {"text": "📊 Deposit Metrics Trending"},
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
                    },
                    "legend": {"data": ["Accumulate deposit", "New Deposit", "Short term Deposit", "Long term Deposit", "CASA", "Deposit Withdrawals"]},
                    "toolbox": {"feature": {"saveAsImage": {}}},
                    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                    "xAxis": [
                        {
                            "type": "category",
                            "boundaryGap": False,
                            "data": chart_months,
                        }
                    ],
                    "yAxis": [{"type": "value"}],
                    "series": [
                        {
                            "name": "Accumulate deposit",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": acc_deposit_gr,
                        },
                        {
                            "name": "New Deposit",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": new_deposit_gr,
                        },
                        {
                            "name": "Short term Deposit",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": st_deposit_gr,
                        },
                        {
                            "name": "Long term Deposit",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": lt_deposit_gr,
                        },
                        {
                            "name": "CASA",
                            "type": "line",
                            "stack": "Total",
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": casa_gr,
                        },
                        {
                            "name": "Deposit Withdrawals",
                            "type": "line",
                            "stack": "Total",
                            "label": {"show": True, "position": "top"},
                            "areaStyle": {},
                            "emphasis": {"focus": "series"},
                            "data": deposit_wd_gr,
                        },
                    ],
                }

                # Render deposit chart
                st_echarts(options=deposit_options, height="400px")

                st.text("")  # Adding space
                colored_header(':three: Card', description="Data about Cutomer Card", color_name="blue-green-70")  

                with st.container():
                    st.subheader("Card Metrics")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    # Acc Card
                    with col1:
                        col1.metric("Accumulate Card", f"{int(Acc_Card)}" if Acc_Card is not None else "No data", acc_card_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_acc_card = shop_data[["Month", "Acc_Card"]].dropna().sort_values("Month")
                            with chart_container(data_acc_card):
                                st.area_chart(data_acc_card, x="Month", y="Acc_Card", use_container_width=True, height=150)
                    
                    # New Card
                    with col2:
                        col2.metric("New Card", f"{int(New_card)}" if New_card is not None else "No data", new_card_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_new_card = shop_data[["Month", "New_card"]].dropna().sort_values("Month")
                            with chart_container(data_new_card):
                                st.area_chart(data_new_card, x="Month", y="New_card", use_container_width=True, height=150)
                    
                    # Card Close
                    with col3:
                        col3.metric("Card Close", f"{int(Card_close)}" if Card_close is not None else "No data", card_close_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_card_close = shop_data[["Month", "Card_close"]].dropna().sort_values("Month")
                            with chart_container(data_card_close):
                                st.area_chart(data_card_close, x="Month", y="Card_close", use_container_width=True, height=150)
                    
                    # Card payment
                    with col4:
                        col4.metric("Card payment", f"{int(Card_rep)}" if Card_rep is not None else "No data", card_rep_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_card_rep = shop_data[["Month", "Card_rep"]].dropna().sort_values("Month")
                            with chart_container(data_card_rep):
                                st.area_chart(data_card_rep, x="Month", y="Card_rep", use_container_width=True, height=150)
                    
                    # Card Transactions
                    with col5:
                        col5.metric("Card Transactions", f"{int(Card_tran)}" if Card_tran is not None else "No data", card_tran_delta, delta_color="normal")
                        if not shop_data.empty:
                            data_card_tran = shop_data[["Month", "Card_tran"]].dropna().sort_values("Month")
                            with chart_container(data_card_tran):
                                st.area_chart(data_card_tran, x="Month", y="Card_tran", use_container_width=True, height=150)

                    # Prepare data for the card chart
                    card_chart_data = shop_data[["Month", "Acc_Card", "New_card", "Card_close", "Card_rep", "Card_tran"]].dropna().sort_values("Month")

                    # Extract series data
                    chart_months = card_chart_data["Month"].tolist()
                    acc_card_gr = card_chart_data["Acc_Card"].astype(float).tolist()
                    new_card_gr = card_chart_data["New_card"].astype(float).tolist()
                    card_close_gr = card_chart_data["Card_close"].astype(float).tolist()
                    card_rep_gr = card_chart_data["Card_rep"].astype(float).tolist()
                    card_tran_gr = card_chart_data["Card_tran"].astype(float).tolist()

                    # Chart options for cards
                    card_options = {
                        "title": {"text": "📊 Card Metrics Trending"},
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
                        },
                        "legend": {"data": ["Accumulate Card", "New Card", "Card Close", "Card payment", "Card Transactions"]},
                        "toolbox": {"feature": {"saveAsImage": {}}},
                        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                        "xAxis": [
                            {
                                "type": "category",
                                "boundaryGap": False,
                                "data": chart_months,
                            }
                        ],
                        "yAxis": [{"type": "value"}],
                        "series": [
                            {
                                "name": "Accumulate Card",
                                "type": "line",
                                "stack": "Total",
                                "areaStyle": {},
                                "emphasis": {"focus": "series"},
                                "data": acc_card_gr,
                            },
                            {
                                "name": "New Card",
                                "type": "line",
                                "stack": "Total",
                                "areaStyle": {},
                                "emphasis": {"focus": "series"},
                                "data": new_card_gr,
                            },
                            {
                                "name": "Card Close",
                                "type": "line",
                                "stack": "Total",
                                "areaStyle": {},
                                "emphasis": {"focus": "series"},
                                "data": card_close_gr,
                            },
                            {
                                "name": "Card payment",
                                "type": "line",
                                "stack": "Total",
                                "areaStyle": {},
                                "emphasis": {"focus": "series"},
                                "data": card_rep_gr,
                            },
                            {
                                "name": "Card Transactions",
                                "type": "line",
                                "stack": "Total",
                                "label": {"show": True, "position": "top"},
                                "areaStyle": {},
                                "emphasis": {"focus": "series"},
                                "data": card_tran_gr,
                            },
                        ],
                    }

                    # Render card chart
                    st_echarts(options=card_options, height="400px")                
            else:
                st.warning(f"No current date found for Shop ID: {selected_shopid}")
        else:
            st.warning(f"No data found for Shop ID: {selected_shopid}")
    else:
        st.info("Please select a Shop ID.")

    colored_header(':four: Comment and Raw data', description="Customer detail comment and data table for download and check data", color_name="blue-green-70")
    def generate_recommendations(current_data, previous_data):
        if previous_data is None:
            return ["No previous data available to compare."], []
        good_recommendations = []
        need_improve_recommendations = []
        # Analyze Loan Metrics
        if "Acc_Loan" in current_data and "Acc_Loan" in previous_data:
            if current_data["Acc_Loan"] > previous_data["Acc_Loan"]:
                good_recommendations.append(
                    f"👍 Increase in loan amount by {current_data['Acc_Loan'] - previous_data['Acc_Loan']}. Focus on maintaining growth."
                )
            elif current_data["Acc_Loan"] < previous_data["Acc_Loan"]:
                need_improve_recommendations.append(
                    f"⚠️ Decrease in loan amount by {previous_data['Acc_Loan'] - current_data['Acc_Loan']}. Consider strategies to attract new loans."
                )

        # Analyze Deposit Metrics
        if "Acc_Deposit" in current_data and "Acc_Deposit" in previous_data:
            if current_data["Acc_Deposit"] > previous_data["Acc_Deposit"]:
                good_recommendations.append(
                    f"👍 Increase in deposit amount by {current_data['Acc_Deposit'] - previous_data['Acc_Deposit']}. Excellent customer retention."
                )
            elif current_data["Acc_Deposit"] < previous_data["Acc_Deposit"]:
                need_improve_recommendations.append(
                    f"⚠️ Decrease in deposit amount by {previous_data['Acc_Deposit'] - current_data['Acc_Deposit']}. Review withdrawal trends."
                )

        # Analyze Late Repayment
        if "Acc_latepayment" in current_data and "Acc_latepayment" in previous_data:
            if current_data["Acc_latepayment"] > previous_data["Acc_latepayment"]:
                need_improve_recommendations.append(
                    f"⚠️ Increase in late repayments by {current_data['Acc_latepayment'] - previous_data['Acc_latepayment']}."
                    f" Consider stricter repayment reminders."
                )
            elif current_data["Acc_latepayment"] < previous_data["Acc_latepayment"]:
                good_recommendations.append(
                    f"👍 Decrease in late repayments by {previous_data['Acc_latepayment'] - current_data['Acc_latepayment']}."
                    f" Good repayment behavior."
                )
            elif current_data["Acc_latepayment"] == previous_data["Acc_latepayment"] and current_data["Acc_latepayment"] > 0:
                need_improve_recommendations.append(
                    f"⚠️ Late repayments remain unchanged at {current_data['Acc_latepayment']}."
                    f" Focus on reducing overdue payments."
                )
            elif current_data["Acc_latepayment"] == previous_data["Acc_latepayment"] and current_data["Acc_latepayment"] == 0:
                good_recommendations.append(
                    f"✔️ Late repayments remain at 0."
                    f" Maintain this excellent repayment behavior."
                )

        # Analyze Badbank Bucket
        if "Badbank_bucket" in current_data and "Badbank_bucket" in previous_data:
            if current_data["Badbank_bucket"] > previous_data["Badbank_bucket"]:
                need_improve_recommendations.append(
                    f"⚠️ Increase in badbank bucket cases by {current_data['Badbank_bucket'] - previous_data['Badbank_bucket']}."
                    f" Focus on reducing defaults."
                )
            elif current_data["Badbank_bucket"] < previous_data["Badbank_bucket"]:
                good_recommendations.append(
                    f"👍 Decrease in badbank bucket cases by {previous_data['Badbank_bucket'] - current_data['Badbank_bucket']}."
                    f" Well-managed defaults."
                )
            elif current_data["Badbank_bucket"] == previous_data["Badbank_bucket"] and current_data["Badbank_bucket"] > 0:
                need_improve_recommendations.append(
                    f"⚠️ Badbank bucket cases remain unchanged at {current_data['Badbank_bucket']}."
                    f" Continue efforts to minimize defaults."
                )
            elif current_data["Badbank_bucket"] == previous_data["Badbank_bucket"] and current_data["Badbank_bucket"] == 0:
                good_recommendations.append(
                    f"✔️ No badbank bucket cases reported."
                    f" Maintain this excellent credit behavior."
                )

        return good_recommendations, need_improve_recommendations

    # Display raw data
    if not shop_data.empty:
        st.subheader("Overall analyst comment")
        good_recommendations, need_improve_recommendations = generate_recommendations(current_data, last_date_data)
        # Helper function to style numbers in green or red
        def style_numbers_in_text(text, color):
            # Use regex to find numbers and wrap them in a span with the specified color
            styled_text = re.sub(r"(\d+)", rf'<span style="color:{color};">\1</span>', text)
            return styled_text

        # Display Good Recommendations (Green)
        if good_recommendations:
            st.markdown('<h4 style="color:green;">✅ Good</h4>', unsafe_allow_html=True)
            for recommendation in good_recommendations:
                # Style numbers in green
                styled_recommendation = style_numbers_in_text(recommendation, "green")
                st.markdown(f"- {styled_recommendation}", unsafe_allow_html=True)

        # Display Need Improve Recommendations (Red)
        if need_improve_recommendations:
            st.markdown('<h4 style="color:red;">⚠️ Need Improve</h4>', unsafe_allow_html=True)
            for recommendation in need_improve_recommendations:
                # Style numbers in red
                styled_recommendation = style_numbers_in_text(recommendation, "red")
                st.markdown(f"- {styled_recommendation}", unsafe_allow_html=True)
        st.subheader("Customer Data Table")
        # Display the table
        st.dataframe(shop_data, use_container_width=True)
        
        # Function to convert DataFrame to Excel for download
        def to_excel(dataframe):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                dataframe.to_excel(writer, index=False, sheet_name='Customer Data')
            processed_data = output.getvalue()
            return processed_data

        # Convert shop_data to Excel
        excel_data = to_excel(shop_data)
        
        # Download button
        excel_data = to_excel(shop_data)
        st.download_button(
            label="📥 Download Data as Excel",
            data=excel_data,
            file_name=f"seller_data_{selected_shopid}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


with tab2:
    st.subheader("Q&A")
    stoggle(
        "What is this?",
        """Banking customer dashboard""",
    )
    stoggle(
        "Change log",
        """🛠️ Version 1.0: release""",
    )
