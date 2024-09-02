import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime
import streamlit_extras
from streamlit_extras.stoggle import stoggle
from streamlit_extras.mandatory_date_range import date_range_picker
from streamlit_extras.colored_header import colored_header
from streamlit_extras.chart_container import chart_container
from streamlit_echarts import st_echarts
from streamlit_extras.switch_page_button import switch_page
#from st_pages import Page, add_page_title, show_pages
import gspread
from google.oauth2.service_account import Credentials
from shillelagh.backends.apsw.db import connect

st.set_page_config(layout="wide", page_title="Seller Capabilities", page_icon="🇲🇱", menu_items={
        'Get Help': 'mailto:anhhung.trinh@shopee.com',
        'Report a bug': "https://docs.google.com/spreadsheets/d/1L1O4PALajoRq2nUdWz1_7TTQjVevBZ3jBlLAR40oRpo/edit#gid=0",
        'About': "# Seller Capabilities. This is an :red[internal] used only app!"})
col1, col2 = st.columns([6, 1])
col1.title('[Template] Seller Capabilities Dashboard')
col1.caption('update _:green[26/5/2023]_')
col2.image(image="https://www.freepnglogos.com/uploads/shopee-logo/logo-shopee-png-images-download-shopee-1.png",width=200)

# with st.sidebar:
#     st.image(image="https://www.freepnglogos.com/uploads/shopee-logo/logo-shopee-png-images-download-shopee-1.png",width=200)
#     st.header("Seller Dashboard")
#     st.header("Help!")
tab1, tab2, tab3 = st.tabs(["Seller Dashboard","Seller Overall", "Help!"])

#loại bỏ mũi tên trên báo cáo
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

with tab1:
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            option = st.selectbox('🆔 Select a Shopid',("381825931","266616640"))
        with col2:
            date_range_picker("📅 Select a date range")

    st.text("") #tao khoang cach giua cac mang du lieu
    # st.write(option)
    # SQL = """SELECT * FROM "https://docs.google.com/spreadsheets/d/1QUHFiRcxKMVIuA8N29btvCi-_V5Vetv210SzYR7xx38/edit#gid=0" WHERE SHOP_ID = a"""
    # st.text(SQL)

    # connection = connect(":memory:")
    # cursor = connection.cursor()
    #
    # query = """
    #     SELECT ado
    #     FROM "https://docs.google.com/spreadsheets/d/1QUHFiRcxKMVIuA8N29btvCi-_V5Vetv210SzYR7xx38/edit#gid=0"
    #     where shop_id = "381825931" and grass_month = "2023-02-01"
    #     """



    colored_header(':bookmark_tabs: Seller information',description="📌:blue[ilita.vn] | Shoe | C2C | BD PIC: thuhuyen.trinh@shopee.com",color_name="blue-green-70")
    with st.container():
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

        col1.metric(label="Overall Tier", value="Tier 2", delta="Tier 3 LM")
        col2.metric(label="%FSS ADG", value="30%", delta="6% MOM | Tier 2")
        col3.metric(label="%FSS+ ADG", value="30%", delta="6% MOM | Tier 2")
        col4.metric(label="%VCX ADG", value="Not join", delta="Tier 5", delta_color="inverse")
        col5.metric(label="NFR", value="0.54%", delta="0.3% LM | Tier 2")
        col6.metric(label="NSR", value="1.07%", delta="2% LM | Tier 4", delta_color="inverse")
        # col2.metric(label="Paid AD Spending", value="87", delta="Over | 3% MOM")
        col7.metric(label="Live SKU", value="497", delta="3% MOM | Tier 2")
        col8.metric(label="New SKU", value="2", delta="5 LM | Tier 4", delta_color="inverse")

#bổ sung các dữ liệu về dat

    st.text("") #tao khoang cach giua cac mang du lieu
    colored_header(':one: Commercial', description="MOM: compare to last, LM: uplift from last month", color_name="blue-green-70")
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
        col1.metric("ADO", "550", "10% MOM | Tier 1")
        col2.metric("ADGMV", "3897", "2% MOM | Tier 3", delta_color="inverse")
        col3.metric("ABS", "2.9", "3% MOM | Tier 1")
        col4.metric("CR", "0.1%", "0.2% LM | Tier 4", delta_color="inverse")
        col5.metric("View", "7.2K", "0.6% LM | Tier 3", delta_color="inverse")
        col6.metric("Impression", "23K", "0.4% LM | Tier 2")

    with st.container():
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            d = {'Month': [1, 2, 3, 4, 5],
                 'ADO': [477, 387, 444, 462, 384]}
            DATA_ADO = pd.DataFrame(data=d)
            with chart_container(DATA_ADO):
                st.area_chart(DATA_ADO, x="Month", y="ADO", width=50, height=200, use_container_width=True)
            stoggle(
                "[Commercial Insight]",
                """Seller performance...""",
            )
        with col2:
            d = {'Month': [1, 2, 3, 4, 5],
                 'ADGmv': [4775, 3837, 4444, 4622, 3544]}
            DATA_ADO = pd.DataFrame(data=d)
            with chart_container(DATA_ADO):
                st.area_chart(DATA_ADO, x="Month", y="ADGmv", width=50, height=200, use_container_width=True)

        with col3:
            d = {'Month': [1, 2, 3, 4, 5],
                 'ABS': [4.7, 3.8, 4.4, 4.6, 3.5]}
            DATA_ADO = pd.DataFrame(data=d)
            with chart_container(DATA_ADO):
                st.area_chart(DATA_ADO, x="Month", y="ABS", width=50, height=200, use_container_width=True)
        with col4:
            d = {'Month': [1, 2, 3, 4, 5],
                 'CR': [0.4, 0.5, 0.3, 0.4, 0.3]}
            DATA_ADO = pd.DataFrame(data=d)
            with chart_container(DATA_ADO):
                st.area_chart(DATA_ADO, x="Month", y="CR", width=50, height=200, use_container_width=True)

    st.text("")  # tao khoang cach giua cac mang du lieu

    colored_header(':two: Marketing', description="Seller marketing information", color_name="blue-green-70")
    st.subheader("Paid Ad")

    with st.container():
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        col1.metric("Expense", "497", "Tier 2")
        col2.metric("PA Ado", "320", "3% MOM | Tier 1")
        col3.metric("PA Adgmv", "3210", "2% MOM | Tier 3", delta_color="inverse")
        col4.metric("PA Top SKU ADO", "150", "5% MOM | Tier 2")
        col5.metric("PA Live SKU", "32", "2% MOM | Tier 1")

    with st.container():

        # colored_header(':two: Marketing', description="Seller marketing information", color_name="blue-green-70")
        # st.subheader("Paid Ad")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
         d = {'Month': [1, 2, 3, 4, 5],
             'Paid Ads': [577, 487, 444, 362, 484]}
         DATA_ADO = pd.DataFrame(data=d)
         with chart_container(DATA_ADO):
            st.area_chart(DATA_ADO, x="Month", y="Paid Ads", width=50, height=200, use_container_width=True)

        with col2:
         # st.text(" ")
         # st.text(" ")
         # st.text(" ")
         # st.text(" ")
         st.markdown(":chart_with_upwards_trend: Detail")
         d = {'ROI': [2, "Tier 4"],
              'Tỷ suất đầu tư': ["33%", "Tier 3"],
              'CIR': ["5%", "Tier 4"]
              }
         col2.table(d)
        with col3:
            # st.text("")
            # st.text("")
            # st.text(" ")
            # st.text(" ")
            # st.markdown(":red[Insight] : Marketing performance...")
            # stoggle(
            #     "[Insight]",
            #     """Paid ad insight""",
            # )
            st.markdown(":heavy_check_mark: :blue[Recommendation]:")
            st.markdown('- Package A')
            st.markdown('- Initiative B')
            st.markdown('- Project C')
        options = {
            "title": {"text": "📊 PA Trending"},
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
            },
            "legend": {"data": ["Spending GR", "Cir", "Roi", "Ado GR", "ADgmv GR"]},
            "toolbox": {"feature": {"saveAsImage": {}}},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": [
                {
                    "type": "category",
                    "boundaryGap": False,
                    "data": ["Jan", "Feb", "March", "April", "May", "June", "Jul"],
                }
            ],
            "yAxis": [{"type": "value"}],
            "series": [
                {
                    "name": "Spending GR",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [1.20, 1.32, 1.01, 1.34, 1.90, 2.30, 2.10],
                },
                {
                    "name": "Cir",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [0.20, 0.182, 0.191, 0.234, 0.290, 0.330, 0.310],
                },
                {
                    "name": "Roi",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [1.0, 2.2, 2.1, 3.4, 1.0, 3.0, 4.0],
                },
                {
                    "name": "Ado GR",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [0.320, 0.332, 0.301, 0.334, 0.390, 0.330, 0.320],
                },
                {
                    "name": "ADgmv GR",
                    "type": "line",
                    "stack": "总量",
                    "label": {"show": True, "position": "top"},
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [0.820, 0.932, 0.901, 0.934, 0.1290, 0.1330, 0.1320],
                },
            ],
        }
        st_echarts(options=options, height="400px")
        st.subheader("Seller voucher")

        with st.container():
            col1, col2, col3, col4= st.columns([1, 1, 1, 1])
            col1.metric("Expense", "497", "Tier 2")
            col2.metric("SV Ado", "100", "1% MOM | Tier 4", delta_color="inverse")
            col3.metric("SV Adgmv", "1510", "2% MOM | Tier 3", delta_color="inverse")
            col4.metric("20% Off - MBS 1 VND - Cap 2000 VND", "2792 ADO", "17% UR | 2% CIR")

        with st.container():
            col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
             d = {'Month': [1, 2, 3, 4, 5],
                 'Seller voucher': [577, 487, 444, 362, 484]}
             DATA_ADO = pd.DataFrame(data=d)
             with chart_container(DATA_ADO):
                 st.area_chart(DATA_ADO, x="Month", y="Seller voucher", width=50, height=200, use_container_width=True)

        with col2:
            # st.text("")
            # st.text("")
            # st.text(" ")
            # st.text(" ")
            st.markdown(":chart_with_upwards_trend: Detail")
        d = {'ROI': [16, "Tier 4"],
             'Tỷ suất đầu tư': ["9%", "Tier 3"],
             'CIR': ["6%", "Tier 4"]
             }
        col2.table(d)
        with col3:
            # st.markdown(":red[Insight] : Marketing performance...")
            # st.text("")
            # st.text("")
            # st.text(" ")
            # st.text(" ")
            st.markdown(":heavy_check_mark: :blue[Recommendation]:")
            st.markdown('- Package A')
            st.markdown('- Initiative B')
            st.markdown('- Project C')
        options = {
            "title": {"text": "📊 SV Trending"},
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
            },
            "legend": {"data": ["Spending GR", "Cir", "Roi", "Ado GR", "ADgmv GR"]},
            "toolbox": {"feature": {"saveAsImage": {}}},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": [
                {
                    "type": "category",
                    "boundaryGap": False,
                    "data": ["Jan", "Feb", "March", "April", "May", "June", "Jul"],
                }
            ],
            "yAxis": [{"type": "value"}],
            "series": [
                {
                    "name": "Spending GR",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [1.20, 1.32, 1.01, 1.34, 1.90, 2.30, 2.10],
                },
                {
                    "name": "Cir",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [0.20, 0.182, 0.191, 0.234, 0.290, 0.330, 0.310],
                },
                {
                    "name": "Roi",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [5.0, 3.2, 2.1, 5.4, 1.0, 3.0, 4.0],
                },
                {
                    "name": "Ado GR",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [0.320, 0.332, 0.301, 0.334, 0.390, 0.330, 0.320],
                },
                {
                    "name": "ADgmv GR",
                    "type": "line",
                    "stack": "总量",
                    "label": {"show": True, "position": "top"},
                    "areaStyle": {},
                    "emphasis": {"focus": "series"},
                    "data": [0.820, 0.932, 0.901, 0.934, 0.1290, 0.1330, 0.1320],
                },
            ],
        }
        st_echarts(options=options, height="400px")

    st.subheader("Affiliate (or other initiative to track)")
    st.caption("template same with PA, SV")
    stoggle(
        "[Marketing Insight]",
        """Marketing insight""",
    )
    colored_header(':three: Raw data', description="Seller detail data table for download and check data", color_name="blue-green-70")


with tab3:
    st.subheader("Q&A")
    stoggle(
        "What is this?",
        """Seller capability tool""",
    )
    stoggle(
        "Change log",
        """26.5 : 🛠️ Version 1.0""",
    )
