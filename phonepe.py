import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import mysql
import mysql.connector
import plotly.express as px
import requests
import json
from PIL import Image
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


chart_counter = 0

def plot_chart(fig):
    global chart_counter
    chart_counter += 1
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{chart_counter}")


# Dataframe Creation

#sql connection

mysql_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database = "phonepe_data"
)

mysql_cursor = mysql_connection.cursor()

# aggregated_insurance
mysql_cursor.execute("SELECT * FROM aggregated_insurance")
aggregated_insurance_records = mysql_cursor.fetchall()

Aggre_insurance = pd.DataFrame(
    aggregated_insurance_records,
    columns=[
        "States",
        "Years",
        "Quarter",
        "Transaction_type",
        "Transaction_count",
        "Transaction_amount"
    ]
)


# aggregated_transaction
mysql_cursor.execute("SELECT * FROM aggregated_transaction")
aggregated_transaction_records = mysql_cursor.fetchall()

Aggre_transaction = pd.DataFrame(
    aggregated_transaction_records,
    columns=[
        "States",
        "Years",
        "Quarter",
        "Transaction_type",
        "Transaction_count",
        "Transaction_amount"
    ]
)


# aggregated_user
mysql_cursor.execute("SELECT * FROM aggregated_user")
aggregated_user_records = mysql_cursor.fetchall()

Aggre_user = pd.DataFrame(
    aggregated_user_records,
    columns=[
        "States",
        "Years",
        "Quarter",
        "Brands",
        "Transaction_count",
        "Percentage"
    ]
)


# map_insurance
mysql_cursor.execute("SELECT * FROM map_insurance")
map_insurance_records = mysql_cursor.fetchall()

map_insurance = pd.DataFrame(
    map_insurance_records,
    columns=[
        "States",
        "Years",
        "Quarter",
        "District",
        "Transaction_count",
        "Transaction_amount"
    ]
)


# map_transaction
mysql_cursor.execute("SELECT * FROM map_transaction")
map_transaction_records = mysql_cursor.fetchall()

map_transaction = pd.DataFrame(
    map_transaction_records,
    columns=[
        "States",
        "Years",
        "Quarter",
        "District",
        "Transaction_count",
        "Transaction_amount"
    ]
)


# map_user
mysql_cursor.execute("SELECT * FROM map_user")
map_user_records = mysql_cursor.fetchall()

map_user = pd.DataFrame(
    map_user_records,
    columns=[
        "States",
        "Years",
        "Quarter",
        "District",
        "RegisteredUser",
        "AppOpens"
    ]
)


# top_insurance
mysql_cursor.execute("SELECT * FROM top_insurance")
top_insurance_records = mysql_cursor.fetchall()

top_insurance = pd.DataFrame(
    top_insurance_records,
    columns=[
        "States",
        "Years",
        "Quarter",
        "Pincodes",
        "Transaction_count",
        "Transaction_amount"
    ]
)


# top_transaction
mysql_cursor.execute("SELECT * FROM top_transaction")
top_transaction_records = mysql_cursor.fetchall()

top_transaction = pd.DataFrame(
    top_transaction_records,
    columns=[
        "States",
        "Years",
        "Quarter",
        "Pincodes",
        "Transaction_count",
        "Transaction_amount"
    ]
)

top_transaction["Location"] = top_transaction["States"] + " - " + top_transaction["Pincodes"].astype(str)


# top_user
mysql_cursor.execute("SELECT * FROM top_user")
top_user_records = mysql_cursor.fetchall()

top_user = pd.DataFrame(
    top_user_records,
    columns=[
        "States",
        "Years",
        "Quarter",
        "Pincodes",
        "RegisteredUsers"
    ]
)

# ------------------------------
# TRANSACTION ANALYSIS BY YEAR
# ------------------------------

def plot_transaction_by_year(df, year):

    # Filter selected year
    year_df = df[df["Years"] == year].reset_index(drop=True)

    # Aggregate data by state
    state_summary = year_df.groupby("States")[["Transaction_count", "Transaction_amount"]].sum().reset_index()

    col1, col2 = st.columns(2)

    # Transaction Amount Bar Chart
    with col1:
        fig_amount = px.bar(
            state_summary,
            x="States",
            y="Transaction_amount",
            title=f"{year} TRANSACTION AMOUNT",
            color_discrete_sequence=px.colors.sequential.Aggrnyl,
            height=650,
            width=600
        )
        fig_amount.update_layout(xaxis_tickangle=-45)
        plot_chart(fig_amount)

    # Transaction Count Bar Chart
    with col2:
        fig_count = px.bar(
            state_summary,
            x="States",
            y="Transaction_count",
            title=f"{year} TRANSACTION COUNT",
            color_discrete_sequence=px.colors.sequential.Bluered_r,
            height=650,
            width=600
        )
        fig_count.update_layout(xaxis_tickangle=-45)
        plot_chart(fig_count)

    # Load India map
    geo_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    india_geojson = json.loads(requests.get(geo_url, verify=False).content)

    col1, col2 = st.columns(2)

    # Map: Transaction Amount
    with col1:
        fig_map_amount = px.choropleth(
            state_summary,
            geojson=india_geojson,
            locations="States",
            featureidkey="properties.ST_NM",
            color="Transaction_amount",
            color_continuous_scale="Rainbow",
            hover_name="States",
            title=f"{year} TRANSACTION AMOUNT",
            fitbounds="locations",
            height=600,
            width=600
        )

        fig_map_amount.update_geos(visible=False)
        plot_chart(fig_map_amount)

    # Map: Transaction Count
    with col2:
        fig_map_count = px.choropleth(
            state_summary,
            geojson=india_geojson,
            locations="States",
            featureidkey="properties.ST_NM",
            color="Transaction_count",
            color_continuous_scale="Rainbow",
            hover_name="States",
            title=f"{year} TRANSACTION COUNT",
            fitbounds="locations",
            height=600,
            width=600
        )

        fig_map_count.update_geos(visible=False)
        plot_chart(fig_map_count)

    return year_df


# --------------------------------
# TRANSACTION ANALYSIS BY QUARTER
# --------------------------------

def plot_transaction_by_quarter(df, quarter):

    # Filter selected quarter
    quarter_df = df[df["Quarter"] == quarter].reset_index(drop=True)

    # Aggregate state data
    state_summary = quarter_df.groupby("States")[["Transaction_count", "Transaction_amount"]].sum().reset_index()

    year = quarter_df["Years"].min()

    col1, col2 = st.columns(2)

    # Transaction Amount Bar
    with col1:
        fig_amount = px.bar(
            state_summary,
            x="States",
            y="Transaction_amount",
            title=f"{year} YEAR {quarter} QUARTER TRANSACTION AMOUNT",
            color_discrete_sequence=px.colors.sequential.Aggrnyl,
            height=650,
            width=600
        )
        plot_chart(fig_amount)

    # Transaction Count Bar
    with col2:
        fig_count = px.bar(
            state_summary,
            x="States",
            y="Transaction_count",
            title=f"{year} YEAR {quarter} QUARTER TRANSACTION COUNT",
            color_discrete_sequence=px.colors.sequential.Bluered_r,
            height=650,
            width=600
        )
        plot_chart(fig_count)

    # Load map
    geo_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    india_geojson = json.loads(requests.get(geo_url, verify=False).content)

    col1, col2 = st.columns(2)

    # Map: Transaction Amount
    with col1:
        fig_map_amount = px.choropleth(
            state_summary,
            geojson=india_geojson,
            locations="States",
            featureidkey="properties.ST_NM",
            color="Transaction_amount",
            color_continuous_scale="Rainbow",
            hover_name="States",
            title=f"{year} YEAR {quarter} QUARTER TRANSACTION AMOUNT",
            fitbounds="locations",
            height=600,
            width=600
        )

        fig_map_amount.update_geos(visible=False)
        plot_chart(fig_map_amount)

    # Map: Transaction Count
    with col2:
        fig_map_count = px.choropleth(
            state_summary,
            geojson=india_geojson,
            locations="States",
            featureidkey="properties.ST_NM",
            color="Transaction_count",
            color_continuous_scale="Rainbow",
            hover_name="States",
            title=f"{year} YEAR {quarter} QUARTER TRANSACTION COUNT",
            fitbounds="locations",
            height=600,
            width=600
        )

        fig_map_count.update_geos(visible=False)
        plot_chart(fig_map_count)

    return quarter_df


# -----------------------------------
# TRANSACTION TYPE ANALYSIS BY STATE
# ------------------------------------

def plot_transaction_type_distribution(df, state):

    # Filter state data
    state_df = df[df["States"] == state].reset_index(drop=True)

    # Aggregate by transaction type
    transaction_summary = state_df.groupby("Transaction_type")[["Transaction_count", "Transaction_amount"]].sum().reset_index()

    col1, col2 = st.columns(2)

    # Pie chart: Amount
    with col1:
        fig_amount = px.pie(
            transaction_summary,
            names="Transaction_type",
            values="Transaction_amount",
            title=f"{state.upper()} TRANSACTION AMOUNT",
            hole=0.5,
            width=600
        )
        plot_chart(fig_amount)

    # Pie chart: Count
    with col2:
        fig_count = px.pie(
            transaction_summary,
            names="Transaction_type",
            values="Transaction_count",
            title=f"{state.upper()} TRANSACTION COUNT",
            hole=0.5,
            width=600
        )
        plot_chart(fig_count)


# ---------------------------------------------------------
# AGGREGATED USER ANALYSIS - YEAR
# ---------------------------------------------------------
def plot_user_brand_transactions_by_year(df, year):

    year_df = df[df["Years"] == year].reset_index(drop=True)

    brand_summary = year_df.groupby("Brands")["Transaction_count"].sum().reset_index()

    fig_bar = px.bar(
        brand_summary,
        x="Brands",
        y="Transaction_count",
        title=f"{year} BRANDS AND TRANSACTION COUNT",
        width=1000,
        color_discrete_sequence=px.colors.sequential.haline_r,
        hover_name="Brands"
    )

    plot_chart(fig_bar)

    return year_df


# ---------------------------------------------------------
# AGGREGATED USER ANALYSIS - QUARTER
# ---------------------------------------------------------
def plot_user_brand_transactions_by_quarter(df, quarter):

    quarter_df = df[df["Quarter"] == quarter].reset_index(drop=True)

    brand_summary = quarter_df.groupby("Brands")["Transaction_count"].sum().reset_index()

    fig_bar = px.bar(
        brand_summary,
        x="Brands",
        y="Transaction_count",
        title=f"{quarter} QUARTER BRANDS TRANSACTION COUNT",
        width=1000,
        color_discrete_sequence=px.colors.sequential.Magenta_r,
        hover_name="Brands"
    )

    plot_chart(fig_bar)

    return quarter_df


# ---------------------------------------------------------
# AGGREGATED USER ANALYSIS - STATE
# ---------------------------------------------------------
def plot_user_brand_distribution_by_state(df, state):

    state_df = df[df["States"] == state].reset_index(drop=True)

    fig_line = px.line(
        state_df,
        x="Brands",
        y="Transaction_count",
        hover_data="Percentage",
        title=f"{state.upper()} BRANDS TRANSACTION COUNT AND PERCENTAGE",
        width=1000,
        markers=True
    )

    plot_chart(fig_line)


# ---------------------------------------------------------
# MAP INSURANCE DISTRICT ANALYSIS
# ---------------------------------------------------------
def plot_district_insurance_transactions(df, state):

    state_df = df[df["States"] == state].reset_index(drop=True)

    district_summary = state_df.groupby("District")[["Transaction_count","Transaction_amount"]].sum().reset_index()

    col1, col2 = st.columns(2)

    with col1:

        fig_amount = px.bar(
            district_summary,
            x="Transaction_amount",
            y="District",
            orientation="h",
            height=600,
            title=f"{state.upper()} DISTRICT TRANSACTION AMOUNT",
            color_discrete_sequence=px.colors.sequential.Mint_r
        )

        plot_chart(fig_amount)

    with col2:

        fig_count = px.bar(
            district_summary,
            x="Transaction_count",
            y="District",
            orientation="h",
            height=600,
            title=f"{state.upper()} DISTRICT TRANSACTION COUNT",
            color_discrete_sequence=px.colors.sequential.Bluered_r
        )

        plot_chart(fig_count)


# ---------------------------------------------------------
# MAP USER ANALYSIS - YEAR
# ---------------------------------------------------------

def plot_state_user_activity_by_year(df, year):

    year_df = df[df["Years"] == year].reset_index(drop=True)

    state_summary = year_df.groupby("States")[["RegisteredUser","AppOpens"]].sum().reset_index()

    col1, col2 = st.columns(2)

    # Registered Users chart
    with col1:
        fig_users = px.bar(
            state_summary,
            x="States",
            y="RegisteredUser",
            title=f"{year} REGISTERED USERS",
            color_discrete_sequence=px.colors.sequential.Bluered_r
        )

        fig_users.update_layout(xaxis_tickangle=-45)

        plot_chart(fig_users)

    # App Opens chart
    with col2:
        fig_opens = px.bar(
            state_summary,
            x="States",
            y="AppOpens",
            title=f"{year} APP OPENS",
            color_discrete_sequence=px.colors.sequential.Aggrnyl
        )

        fig_opens.update_layout(xaxis_tickangle=-45)

        plot_chart(fig_opens)

    return year_df

# ---------------------------------------------------------
# MAP USER ANALYSIS - QUARTER
# ---------------------------------------------------------
def plot_state_user_activity_by_quarter(df, quarter):

    quarter_df = df[df["Quarter"] == quarter].reset_index(drop=True)

    state_summary = quarter_df.groupby("States")[["RegisteredUser","AppOpens"]].sum().reset_index()

    year = quarter_df["Years"].min()

    fig_line = px.line(
        state_summary,
        x="States",
        y=["RegisteredUser","AppOpens"],
        title=f"{year} YEAR {quarter} QUARTER USER ACTIVITY",
        width=1000,
        height=800,
        markers=True,
        color_discrete_sequence=px.colors.sequential.Rainbow_r
    )

    plot_chart(fig_line)

    return quarter_df


# ---------------------------------------------------------
# MAP USER DISTRICT ANALYSIS
# ---------------------------------------------------------
def plot_district_user_activity(df, state):

    state_df = df[df["States"].str.contains(state, case=False)].reset_index(drop=True)

    col1, col2 = st.columns(2)

    with col1:

        fig_registered = px.bar(
            state_df,
            x="RegisteredUser",
            y="District",
            orientation="h",
            title=f"{state.upper()} REGISTERED USERS",
            height=800,
            color_discrete_sequence=px.colors.sequential.Rainbow_r
        )

        plot_chart(fig_registered)

    with col2:

        fig_appopens = px.bar(
            state_df,
            x="AppOpens",
            y="District",
            orientation="h",
            title=f"{state.upper()} APP OPENS",
            height=800,
            color_discrete_sequence=px.colors.sequential.Rainbow
        )

        plot_chart(fig_appopens)


# ---------------------------------------------------------
# TOP INSURANCE ANALYSIS
# ---------------------------------------------------------
def plot_top_insurance_transactions(df, state):

    state_df = df[df["States"] == state].reset_index(drop=True)

    col1, col2 = st.columns(2)

    with col1:

        fig_amount = px.bar(
            state_df,
            x="Quarter",
            y="Transaction_amount",
            hover_data="Pincodes",
            title="INSURANCE TRANSACTION AMOUNT",
            height=650,
            width=600,
            color_discrete_sequence=px.colors.sequential.GnBu_r
        )

        plot_chart(fig_amount)

    with col2:

        fig_count = px.bar(
            state_df,
            x="Quarter",
            y="Transaction_count",
            hover_data="Pincodes",
            title="INSURANCE TRANSACTION COUNT",
            height=650,
            width=600,
            color_discrete_sequence=px.colors.sequential.Agsunset_r
        )

        plot_chart(fig_count)


# ---------------------------------------------------------
# TOP USER ANALYSIS - YEAR
# ---------------------------------------------------------
def plot_top_registered_users_by_year(df, year):

    year_df = df[df["Years"] == year].reset_index(drop=True)

    summary = year_df.groupby(["States","Quarter"])["RegisteredUsers"].sum().reset_index()

    fig = px.bar(
        summary,
        x="States",
        y="RegisteredUsers",
        color="Quarter",
        width=1000,
        height=800,
        color_discrete_sequence=px.colors.sequential.Burgyl,
        hover_name="States",
        title=f"{year} REGISTERED USERS"
    )

    plot_chart(fig)

    return year_df


# ---------------------------------------------------------
# TOP USER ANALYSIS - STATE
# ---------------------------------------------------------
def plot_top_registered_users_by_state(df, state):

    state_df = df[df["States"] == state].reset_index(drop=True)

    fig = px.bar(
        state_df,
        x="Quarter",
        y="RegisteredUsers",
        title="REGISTERED USERS BY PINCODE AND QUARTER",
        width=1000,
        height=800,
        color="RegisteredUsers",
        hover_data="Pincodes",
        color_continuous_scale=px.colors.sequential.Magenta
    )

    plot_chart(fig)


# -------------------------------------
# TOP CHARTS
# -------------------------------------

# Aggregated Insurance Transactions Charts
# --------------------------------------------

def top_chart_aggregated_insurance():

    # Insurance Amount by State
    state_amount = Aggre_insurance.groupby("States")["Transaction_amount"].sum().reset_index()

    fig = px.bar(
        state_amount,
        x="States",
        y="Transaction_amount",
        title="Insurance Amount by State"
    )
    plot_chart(fig)


    # Insurance Count by State
    state_count = Aggre_insurance.groupby("States")["Transaction_count"].sum().reset_index()

    fig = px.bar(
        state_count,
        x="States",
        y="Transaction_count",
        title="Insurance Count by State"
    )
    plot_chart(fig)


    # Insurance Growth by Year
    trend = Aggre_insurance.groupby("Years")["Transaction_amount"].sum().reset_index()

    fig = px.line(
        trend,
        x="Years",
        y="Transaction_amount",
        markers=True,
        title="Insurance Growth by Year"
    )
    plot_chart(fig)


    # Insurance Growth by Quarter
    quarter_trend = Aggre_insurance.groupby("Quarter")["Transaction_amount"].sum().reset_index()

    fig = px.line(
        quarter_trend,
        x="Quarter",
        y="Transaction_amount",
        markers=True,
        title="Insurance Growth by Quarter"
    )
    plot_chart(fig)

# -----------------------------------------
# Map Insurance Transactions Charts
# -----------------------------------------


def top_chart_map_transactions():

    # Amount by State
    state_amount = map_transaction.groupby("States")["Transaction_amount"].sum().reset_index()

    geo_url="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    india_geojson=json.loads(requests.get(geo_url, verify=False).content)

    fig = px.choropleth(
        state_amount,
        geojson=india_geojson,
        locations="States",
        featureidkey="properties.ST_NM",
        color="Transaction_amount",
        title="Insurance Amount by State Map",
    )

    fig.update_geos(visible=False, fitbounds = "locations")
    plot_chart(fig)

    # Count Map
    state_count = map_transaction.groupby("States")["Transaction_count"].sum().reset_index()

    fig = px.choropleth(
        state_count,
        geojson=india_geojson,
        locations="States",
        featureidkey="properties.ST_NM",
        color="Transaction_count",
        title="Insurance Count by State Map"
    )

    fig.update_geos(visible=False, fitbounds = "locations")
    plot_chart(fig)

    # District wise transactions (Top 10)
    district_data = map_transaction.groupby("District")["Transaction_amount"].sum().reset_index()

    district_data = district_data.sort_values(
        by="Transaction_amount",
        ascending=False
    ).head(10)

    fig = px.bar(
        district_data,
        x="Transaction_amount",
        y="District",
        orientation="h",
        title="Top 10 Districts by Insurance Amount"
    )
    plot_chart(fig)

    district_count = map_transaction.groupby("District")["Transaction_count"].sum().reset_index()

    district_count = district_count.sort_values(
    by="Transaction_count",
    ascending=False
).head(10)

    fig = px.bar(
        district_count,
        x="Transaction_count",
        y="District",
        orientation="h",
        title="Top 10 Districts by Insurance Count"
    )
    plot_chart(fig) 

# ----------------------------------------
# Top Insurance Analysis Charts
# -----------------------------------------
def top_chart_top_insurance():

    # Top 10 States by Insurance Amount

    state_amount = top_insurance.groupby("States")["Transaction_amount"].sum().reset_index()

    state_amount = state_amount.sort_values(
        by="Transaction_amount",
        ascending=False
    ).head(10)

    fig = px.bar(
        state_amount,
        x="States",
        y="Transaction_amount",
        title="Top 10 States by Insurance Amount"
    )

    plot_chart(fig)


    # Top 10 States by Insurance Count

    state_count = top_insurance.groupby("States")["Transaction_count"].sum().reset_index()

    state_count = state_count.sort_values(
        by="Transaction_count",
        ascending=False
    ).head(10)

    fig = px.bar(
        state_count,
        x="States",
        y="Transaction_count",
        title="Top 10 States by Insurance Count"
    )

    plot_chart(fig)


    # Top 10 Pincodes by Insurance Amount

    pin_amount = top_insurance.groupby("Pincodes")["Transaction_amount"].sum().reset_index()

    pin_amount = pin_amount.sort_values(
        by="Transaction_amount",
        ascending=False
    ).head(10)

    # convert to string so Plotly treats it as category
    pin_amount["Pincodes"] = pin_amount["Pincodes"].astype(str)

    fig = px.bar(
        pin_amount,
        x="Transaction_amount",
        y="Pincodes",
        orientation="h",
        title="Top 10 Pincodes by Insurance Amount",
        height=600
    )

    fig.update_yaxes(type="category")   # force categorical axis

    fig.update_layout(
        yaxis_title="Pincode",
        xaxis_title="Insurance Amount"
    )

    plot_chart(fig)

    # Insurance Growth By Quarter

    st.subheader("Insurance Growth by Quarter")

    quarter_growth = Aggre_insurance.groupby("Quarter")["Transaction_amount"].sum().reset_index()

    fig = px.line(
        quarter_growth,
        x="Quarter",
        y="Transaction_amount",
        markers=True,
    )
    plot_chart(fig)

# -----------------------------------------
# Aggregated Transactions Charts
# -----------------------------------------

def top_chart_aggregated_transactions():

    # Transaction Amount by State
    state_amount = Aggre_transaction.groupby("States")["Transaction_amount"].sum().reset_index()

    fig = px.bar(
        state_amount,
        x="States",
        y="Transaction_amount",
        title="Transaction Amount by State",
        height=600
    )

    fig.update_layout(xaxis_tickangle=-45)
    plot_chart(fig)


    # Transaction Count by State
    state_count = Aggre_transaction.groupby("States")["Transaction_count"].sum().reset_index()

    fig = px.bar(
        state_count,
        x="States",
        y="Transaction_count",
        title="Transaction Count by State",
        height=600
    )

    fig.update_layout(xaxis_tickangle=-45)
    plot_chart(fig)


    # Transaction Type Distribution
    type_data = Aggre_transaction.groupby("Transaction_type")["Transaction_amount"].sum().reset_index()

    fig = px.pie(
        type_data,
        names="Transaction_type",
        values="Transaction_amount",
        title="Transaction Type Distribution"
    )

    plot_chart(fig)


    # Transaction Growth by Year
    trend = Aggre_transaction.groupby("Years")["Transaction_amount"].sum().reset_index()

    fig = px.line(
        trend,
        x="Years",
        y="Transaction_amount",
        markers=True,
        title="Transaction Growth by Year",
        height=500
    )

    plot_chart(fig)

    # Top 10 States by Transaction Amount

    top_states = Aggre_transaction.groupby("States")["Transaction_amount"].sum().reset_index()

    top_states = top_states.sort_values(
        by="Transaction_amount",
        ascending=False
    ).head(10)

    fig = px.bar(
        top_states,
        x="Transaction_amount",
        y="States",
        orientation="h",
        title="Top 10 States by Transaction Amount",
        height=600
    )

    fig.update_yaxes(categoryorder="total ascending")

    plot_chart(fig)

# -----------------------------------------
# Map Transactions Charts
# -----------------------------------------

def top_chart_map_transactions():

    geo_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    india_geojson = json.loads(requests.get(geo_url, verify=False).content)

    col1, col2 = st.columns(2)

    # Transaction Amount Map
    with col1:

        state_amount = map_transaction.groupby("States")["Transaction_amount"].sum().reset_index()

        fig = px.choropleth(
            state_amount,
            geojson=india_geojson,
            locations="States",
            featureidkey="properties.ST_NM",
            color="Transaction_amount",
            title="Transaction Amount by State Map"
        )

        fig.update_geos(visible=False, fitbounds="locations")

        plot_chart(fig)


    # Transaction Count Map
    with col2:

        state_count = map_transaction.groupby("States")["Transaction_count"].sum().reset_index()

        fig = px.choropleth(
            state_count,
            geojson=india_geojson,
            locations="States",
            featureidkey="properties.ST_NM",
            color="Transaction_count",
            title="Transaction Count by State Map"
        )

        fig.update_geos(visible=False, fitbounds="locations")

        plot_chart(fig)


    # Top Districts by Amount
    district_amount = map_transaction.groupby("District")["Transaction_amount"].sum().reset_index()

    district_amount = district_amount.sort_values(
        by="Transaction_amount",
        ascending=False
    ).head(10)

    fig = px.bar(
        district_amount,
        x="Transaction_amount",
        y="District",
        orientation="h",
        title="Top 10 Districts by Transaction Amount"
    )

    plot_chart(fig)


    # Top Districts by Count
    district_count = map_transaction.groupby("District")["Transaction_count"].sum().reset_index()

    district_count = district_count.sort_values(
        by="Transaction_count",
        ascending=False
    ).head(10)

    fig = px.bar(
        district_count,
        x="Transaction_count",
        y="District",
        orientation="h",
        title="Top 10 Districts by Transaction Count"
    )

    plot_chart(fig)

# -----------------------------------------
# Top Transactions Charts
# -----------------------------------------

def top_chart_top_transactions():

    # ---------- Top 10 Pincodes by Amount ----------

    pin_amount = top_insurance.groupby(["States","Pincodes"])["Transaction_amount"].sum().reset_index()

    pin_amount = pin_amount.sort_values(
        by="Transaction_amount",
        ascending=False
    ).head(10)

    # create label
    pin_amount["Location"] = pin_amount["States"] + " - " + pin_amount["Pincodes"].astype(str)

    fig = px.bar(
        pin_amount,
        x="Transaction_amount",
        y="Location",
        orientation="h",
        title="Top 10 Locations by Insurance Amount",
        height=600
    )

    fig.update_yaxes(categoryorder="total ascending")

    plot_chart(fig)

    # ---------- Top 10 Pincodes by Transaction Count ----------

    pin_count = top_transaction.groupby(["States","Pincodes"])["Transaction_count"].sum().reset_index()

    pin_count = pin_count.sort_values(
        by="Transaction_count",
        ascending=False
    ).head(10)

    # create label
    pin_count["Location"] = pin_count["States"] + " - " + pin_count["Pincodes"].astype(str)

    fig = px.bar(
        pin_count,
        x="Transaction_count",
        y="Location",
        orientation="h",
        title="Top 10 Locations by Transaction Count",
        height=600
    )

    fig.update_yaxes(categoryorder="total ascending")
    plot_chart(fig)


    # ---------- Transaction Amount by State ----------
    state_amount = top_transaction.groupby("States")["Transaction_amount"].sum().reset_index()

    fig = px.bar(
        state_amount,
        x="States",
        y="Transaction_amount",
        title="Transaction Amount by State",
        height=600
    )

    fig.update_layout(xaxis_tickangle=-45)

    plot_chart(fig)


    # ---------- Transaction Count by State ----------
    state_count = top_transaction.groupby("States")["Transaction_count"].sum().reset_index()

    fig = px.bar(
        state_count,
        x="States",
        y="Transaction_count",
        title="Transaction Count by State",
        height=600
    )

    fig.update_layout(xaxis_tickangle=-45)

    plot_chart(fig)


    # ---------- Transaction Trend by Year ----------
    year_trend = top_transaction.groupby("Years")["Transaction_amount"].sum().reset_index()

    fig = px.line(
        year_trend,
        x="Years",
        y="Transaction_amount",
        markers=True,
        title="Transaction Growth by Year",
        height=500
    )

    plot_chart(fig)


    # ---------- Transaction Trend by Quarter ----------
    quarter_trend = top_transaction.groupby("Quarter")["Transaction_amount"].sum().reset_index()

    fig = px.line(
        quarter_trend,
        x="Quarter",
        y="Transaction_amount",
        markers=True,
        title="Transaction Growth by Quarter",
        height=500
    )

    plot_chart(fig)

# -----------------------------------------
# Aggregated User Analysis Charts 
# -----------------------------------------
def top_chart_user_analysis():

    # Registered users by state
    state_users = map_user.groupby("States")["RegisteredUser"].sum().reset_index()

    fig = px.bar(
        state_users,
        x="States",
        y="RegisteredUser",
        title="Registered Users by State"
    )
    plot_chart(fig)

    # App opens by state
    state_opens = map_user.groupby("States")["AppOpens"].sum().reset_index()

    fig = px.bar(
        state_opens,
        x="States",
        y="AppOpens",
        title="App Opens by State"
    )
    plot_chart(fig)

    # Mobile brand usage
    brand_usage = Aggre_user.groupby("Brands")["Transaction_count"].sum().reset_index()

    fig = px.pie(
        brand_usage,
        names="Brands",
        values="Transaction_count",
        title="Mobile Brand Usage Distribution"
    )

    plot_chart(fig)


# ----------------------------------------
# REGISTERED USERS BY DISTRICT
# ---------------------------------------

def top_chart_registered_user(table_name, state_name):

    query = f"""
        SELECT district, SUM(registered_user)
        FROM {table_name}
        WHERE state_name = '{state_name}'
        GROUP BY district
        ORDER BY SUM(registered_user) DESC
        LIMIT 10
    """

    mysql_cursor.execute(query)
    top_districts = mysql_cursor.fetchall()

    df = pd.DataFrame(top_districts, columns=["District","Registered_Users"])

    fig = px.bar(
        df,
        x="District",
        y="Registered_Users",
        title="TOP DISTRICTS BY REGISTERED USERS",
        color_discrete_sequence=px.colors.sequential.Aggrnyl
    )

    plot_chart(fig)

# ------------------------------------
# APP OPENS BY DISTRICT
# ------------------------------------

def top_chart_appopens(table_name, state):

    query = f"""
        SELECT district, SUM(app_opens)
        FROM {table_name}
        WHERE state_name = '{state}'
        GROUP BY district
        ORDER BY SUM(app_opens) DESC
        LIMIT 10
    """

    mysql_cursor.execute(query)
    top_districts = mysql_cursor.fetchall()

    df = pd.DataFrame(top_districts, columns=["District","App_Opens"])

    fig = px.bar(
        df,
        x="District",
        y="App_Opens",
        title="TOP DISTRICTS BY APP OPENS",
        color_discrete_sequence=px.colors.sequential.Aggrnyl
    )

    plot_chart(fig)

# ---------------------------------------
# REGISTERED USERS BY STATE
# ---------------------------------------

def top_chart_registered_users(table_name):

    query = f"""
        SELECT state_name, SUM(registered_user)
        FROM {table_name}
        GROUP BY state_name
        ORDER BY SUM(registered_user) DESC
        LIMIT 10
    """

    mysql_cursor.execute(query)
    top_states = mysql_cursor.fetchall()

    df = pd.DataFrame(top_states, columns=["States","Registered_Users"])

    fig = px.bar(
        df,
        x="States",
        y="Registered_Users",
        title="TOP STATES BY REGISTERED USERS",
        color_discrete_sequence=px.colors.sequential.Aggrnyl
    )

    plot_chart(fig)

# ---------------------------------------------------------
# STREAMLIT DASHBOARD
# ---------------------------------------------------------

# Sidebar menu
with st.sidebar:
    menu = option_menu(
        "Main Menu",
        ["Home", "Data Exploration", "Top Charts"],
        icons=["house", "bar-chart", "trophy"],
        default_index=0
    )

# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

if menu == "Home":
    st.set_page_config(layout="wide")
    st.title("📊 PhonePe Transaction Insights")
    st.subheader("Analyzing Digital Payment Trends Across India")

    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/71/PhonePe_Logo.svg",
        width=220
    )

    st.markdown("""
    This dashboard analyzes **PhonePe Pulse data** to understand how digital
    payments are growing across India.

    The project focuses on analyzing transaction patterns, user engagement,
    and insurance-related data to better understand the growth of digital
    payments and regional usage trends.
    """)

    st.markdown("---")

    st.markdown("### 🎯 Project Objective")

    st.write(
        "To analyze PhonePe transaction, user, and insurance data and present "
        "insights through interactive visualizations that help understand "
        "digital payment adoption across different states and districts."
    )

    st.markdown("---")

    st.markdown("### 📊 Key Features of the Dashboard")

    st.write("• Analysis of transaction trends across states and districts")
    st.write("• Visualization of insurance transaction data")
    st.write("• Identification of top performing states and regions")
    st.write("• User engagement and activity insights")
    st.write("• Interactive data exploration by year and quarter")

    st.markdown("---")

    st.markdown("### ⚙️ Technologies Used")

    st.write("• Python")
    st.write("• SQL (MySQL)")
    st.write("• Streamlit")
    st.write("• Pandas")
    st.write("• Plotly for Data Visualization")

    st.markdown("---")

    st.markdown("### Skills Demonstrated")

    st.write("• Data Extraction and ETL")
    st.write("• SQL Data Analysis")
    st.write("• Data Visualization")
    st.write("• Analytical Thinking")
    st.write("• Dashboard Development using Streamlit")

    st.markdown("---")

    st.markdown(
        "[Learn more about PhonePe](https://www.phonepe.com/)"
    )


# ---------------------------------------------------------
# DATA EXPLORATION
# ---------------------------------------------------------

elif menu == "Data Exploration":

    tab1, tab2, tab3 = st.tabs(
        ["Aggregated Analysis", "Map Analysis", "Top Analysis"]
    )

# ---------------- Aggregated Analysis ---------------- #

    with tab1:

        analysis_type = st.radio(
            "Select Analysis",
            ["Insurance", "Transactions", "Users"]
        )

        if analysis_type == "Insurance":

            year = st.slider(
                "Select Year",
                int(Aggre_insurance["Years"].min()),
                int(Aggre_insurance["Years"].max()),
                key="year_slider1"
            )

            year_df = plot_transaction_by_year(Aggre_insurance, year)

            quarter = st.slider(
                "Select Quarter",
                int(year_df["Quarter"].min()),
                int(year_df["Quarter"].max()),
                key="year_slider2"
            )

            plot_transaction_by_quarter(year_df, quarter)


        elif analysis_type == "Transactions":

            year = st.slider(
                "Select Year",
                int(Aggre_transaction["Years"].min()),
                int(Aggre_transaction["Years"].max()),
                key="year_slider3"
            )

            year_df = plot_transaction_by_year(Aggre_transaction, year)

            state = st.selectbox(
                "Select State",
                year_df["States"].unique(),
                key=("state_select_1")
            )

            plot_transaction_type_distribution(year_df, state)

            quarter = st.slider(
                "Select Quarter",
                int(year_df["Quarter"].min()),
                int(year_df["Quarter"].max()),
                key="year_slider4"
            )

            quarter_df = plot_transaction_by_quarter(year_df, quarter)

            state = st.selectbox(
                "Select State (Quarter)",
                quarter_df["States"].unique(),
                key="state_select_2"
            )

            plot_transaction_type_distribution(quarter_df, state)


        elif analysis_type == "Users":

            year = st.slider(
                "Select Year",
                int(Aggre_user["Years"].min()),
                int(Aggre_user["Years"].max()),
                key="year_slider5"
            )

            year_df = plot_user_brand_transactions_by_year(Aggre_user, year)

            quarter = st.slider(
                "Select Quarter",
                int(year_df["Quarter"].min()),
                int(year_df["Quarter"].max()),
                key="year_slider6"
            )

            quarter_df = plot_user_brand_transactions_by_quarter(year_df, quarter)

            state = st.selectbox(
                "Select State",
                quarter_df["States"].unique(),
                key=str("state_select_3")
            )

            plot_user_brand_distribution_by_state(quarter_df, state)

# ---------------- Map Analysis ---------------- #

    with tab2:

        map_analysis = st.radio(
            "Select Map Analysis",
            ["Insurance", "Transactions", "Users"]
        )

        if map_analysis == "Insurance":

            year = st.slider(
                "Select Year",
                int(map_insurance["Years"].min()),
                int(map_insurance["Years"].max()),
                key="year_slider7"
            )

            year_df = plot_transaction_by_year(map_insurance, year)

            state = st.selectbox(
                "Select State",
                year_df["States"].unique(),
                key="state_select_4"
            )

            plot_district_insurance_transactions(year_df, state)


        elif map_analysis == "Transactions":

            year = st.slider(
                "Select Year",
                int(map_transaction["Years"].min()),
                int(map_transaction["Years"].max()),
                key="year_slider8"
            )

            year_df = plot_transaction_by_year(map_transaction, year)

            state = st.selectbox(
                "Select State",
                year_df["States"].unique(),
                key="state_select_5"
            )

            plot_district_insurance_transactions(year_df, state)


        elif map_analysis == "Users":

            year = st.slider(
                "Select Year",
                int(map_user["Years"].min()),
                int(map_user["Years"].max()),
                key="year_slider9"
            )

            year_df = plot_state_user_activity_by_year(map_user, year)

            quarter = st.slider(
                "Select Quarter",
                int(year_df["Quarter"].min()),
                int(year_df["Quarter"].max()),
                key="year_slider10"
            )

            quarter_df = plot_state_user_activity_by_quarter(year_df, quarter)

            state = st.selectbox(
                "Select State",
                quarter_df["States"].unique(),
                key="state_select_6"
            )

            plot_district_user_activity(quarter_df, state)

# ---------------- Top Analysis ---------------- #

    with tab3:

        top_analysis = st.radio(
            "Select Top Analysis",
            ["Insurance", "Transactions", "Users"]
        )

        if top_analysis == "Insurance":

            year = st.slider(
                "Select Year",
                int(top_insurance["Years"].min()),
                int(top_insurance["Years"].max()),
                key="year_slider11"
            )

            year_df = plot_transaction_by_year(top_insurance, year)

            state = st.selectbox(
                "Select State",
                year_df["States"].unique(),
                key="state_select_7"
            )

            plot_top_insurance_transactions(year_df, state)


        elif top_analysis == "Transactions":

            year = st.slider(
                "Select Year",
                int(top_transaction["Years"].min()),
                int(top_transaction["Years"].max()),
                key="year_slider12"
            )

            year_df = plot_transaction_by_year(top_transaction, year)

            state = st.selectbox(
                "Select State",
                year_df["States"].unique(),
                key="state_select_8"
            )

            plot_top_insurance_transactions(year_df, state)


        elif top_analysis == "Users":

            year = st.slider(
                "Select Year",
                int(top_user["Years"].min()),
                int(top_user["Years"].max()),
                key="year_slider13"
            )

            year_df = plot_top_registered_users_by_year(top_user, year)

            state = st.selectbox(
                "Select State",
                year_df["States"].unique(),
                key="state_select_9"
            )

            plot_top_registered_users_by_state(year_df, state)


# ---------------------------------------------------------
# TOP CHARTS
# ---------------------------------------------------------

elif menu == "Top Charts":

    question = st.selectbox(
        "Select Analysis",
        [
            "Aggregated Insurance Transactions",
            "Map Insurance Transactions",
            "Top Insurance Transactions",
            "Aggregated Transactions",
            "Map Transactions",
            "Top Transactions",
            "Aggregated User Transactions",
            "Registered Users by District",
            "App Opens by District",
            "Registered Users by State"
        ],
        key="analaysis_select"
    )

    if question == "Aggregated Insurance Transactions":
        top_chart_aggregated_insurance()

    elif question == "Map Insurance Transactions":
        top_chart_map_transactions()

    elif question == "Top Insurance Transactions":
        top_chart_top_insurance()

    elif question == "Aggregated Transactions":
        top_chart_aggregated_transactions()

    elif question == "Map Transactions":
        top_chart_map_transactions()

    elif question == "Top Transactions":
        top_chart_top_transactions()

    elif question == "Aggregated User Transactions":
        top_chart_user_analysis()

    elif question == "Registered Users by District":

        state = st.selectbox("Select State", map_user["States"].unique(), key="top_chart_select1" )
        top_chart_registered_user("map_user", state)

    elif question == "App Opens by District":

        state = st.selectbox("Select State", map_user["States"].unique(), key="top_chart_sleect_2")
        top_chart_appopens("map_user", state)

    elif question == "Registered Users by State":

        top_chart_registered_users("top_user")