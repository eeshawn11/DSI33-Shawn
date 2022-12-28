import pandas as pd
import streamlit as st
import requests
import numpy as np
import altair as alt
from numerize.numerize import numerize
import plotly.express as px
import json

st.set_page_config(layout="wide")
alt.data_transformers.enable("json")

def magnitude(value: int) -> int:
    if (value == 0): return 0
    return int(np.floor(np.log10(abs(value))))


def get_buffer(value: int) -> int:
    return 10 ** magnitude(value) / magnitude(value)


def get_scale(series:pd.Series) -> list[int, int]:
        scale_min = series.min() - get_buffer(series.min())
        if scale_min <= 50:
            scale_min = 0
        scale_max = series.max() + get_buffer(series.max())
        return [scale_min, scale_max]


def resale_transaction_delta() -> str:
    if year != 'All' and year != st.session_state.years[-1]:
        delta = df_filtered['resale_price'].count() - df_filtered_previous_year['resale_price'].count()
        return f"{delta:,} vs {year-1}"


def transaction_value_delta() -> str:
    if year != 'All' and year != st.session_state.years[-1]:
        delta = df_filtered['resale_price'].sum() - df_filtered_previous_year['resale_price'].sum()
        return f"{numerize(delta.item())} vs {year-1}"


def min_price_delta() -> str:
    if year != 'All' and year != st.session_state.years[-1]:
        delta = df_filtered['resale_price'].min() - df_filtered_previous_year["resale_price"].min()
        return f"{delta:,} vs {year-1}"


def max_price_delta() -> str:
    if year != 'All' and year != st.session_state.years[-1]:
        delta = df_filtered['resale_price'].max() - df_filtered_previous_year["resale_price"].max()
        return f"{delta:,} vs {year-1}"


def median_price_delta() -> str:
    if year != 'All' and year != st.session_state.years[-1]:
        delta = df_filtered['resale_price'].median() - df_filtered_previous_year["resale_price"].median()
        return f"{delta:,} vs {year-1}"


# def retrieve(n: int):
#     """
#     Retrieve data through Data.gov.sg API.
#     """
#     resource_id = "f1765b54-a209-4718-8d38-a39237f502b3"
#     url_string = f"https://data.gov.sg/api/action/datastore_search?resource_id={resource_id}&limit={n}"
#     try:
#         response = requests.get(
#             url_string, headers={"User-Agent": "Mozilla/5.0"}
#         ).json()
#         return response
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         print(e)
#         print(url_string)


# @st.experimental_memo(ttl=2_630_000)  # dataset is updated monthly
# def get_data():
#     body = retrieve(1)
#     limit = body["result"]["total"]
#     body = retrieve(limit)
#     content = pd.DataFrame(body["result"]["records"])
#     return content


# df = get_data()
# df["address"] = df["block"] + " " + df["street_name"]


# @st.experimental_memo(max_entries=1)
# def get_coords_df():
#     # return pd.read_csv('/app/dsi33-shawn/Side_Projects/HDB_Resale_Price/assets/hdb_coords.csv')
#     return pd.read_csv(
#         "C:/Users/brkit/Documents/DSI33-Shawn/Side_Projects/HDB_Resale_Price/assets/hdb_coords.csv"
#     )


# hdb_coordinates = get_coords_df()
# df_merged = df.merge(hdb_coordinates, how="left", on="address")
# df_merged.drop(columns="_id", inplace=True)
# df_merged["month"] = pd.to_datetime(df_merged["month"], format="%Y-%m", errors="raise")
# df_merged["town"] = df_merged["town"].str.title()
# df_merged["resale_price"] = df_merged["resale_price"].astype(float).astype(int)

# @st.experimental_singleton
# def get_chloropeth():
#     # with open('/app/dsi33-shawn/Side_Projects/HDB_Resale_Price/assets/master-plan-2014-planning-area-boundary-no-sea.json') as f:
#     with open(
#         "C:/Users/brkit/Documents/DSI33-Shawn/Side_Projects/HDB_Resale_Price/assets/master-plan-2014-planning-area-boundary-no-sea.json"
#     ) as f:
#         return json.load(f)


# geo_df = get_chloropeth()

# towns = st.session_state.df["town"].unique()
# towns = sorted(towns)
# towns.insert(0, "All")

# years = list(
#     range(st.session_state.df["month"].max().year, st.session_state.df["month"].min().year - 1, -1)
# )
# years.insert(0, "All")

# create sidebar for filtering dashboard
with st.sidebar:
    st.header("Filter options")
    town_option = st.selectbox(label="District", options=st.session_state.towns)

    year = st.selectbox(label="Year", options=st.session_state.years)

# filter df based on selected parameters
if town_option == "All":
    if year == "All":
        df_filtered = st.session_state.df
    else:
        df_filtered = st.session_state.df.query("month.dt.year == @year")
        df_filtered_previous_year = st.session_state.df.query("month.dt.year == @year-1")
else:
    if year == "All":
        df_filtered = st.session_state.df.query("town.str.contains(@town_option)")
    else:
        df_filtered = st.session_state.df.query(
            "month.dt.year == @year & town.str.contains(@town_option)"
        )
        df_filtered_previous_year = st.session_state.df.query("month.dt.year == @year-1 & town.str.contains(@town_option)")

# create dataframes for individual plot displays
map_df = df_filtered.groupby("town").resale_price.median().reset_index()
resale_price = df_filtered.groupby("month").resale_price.median().reset_index()
resale_transactions = df_filtered.groupby("month").town.count().reset_index()


with st.container():
    st.markdown(f"## {town_option} transactions in {year}")
    st.markdown("### Key Metrics")
    # row 1
    met1, met2, met3 = st.columns(3)
    met1.metric(
        label="Total Resale Transactions",
        value=f"{df_filtered['resale_price'].count():,}",
        help="Total resale transactions during this period",
        delta=resale_transaction_delta()
    )
    met2.metric(
        label="Total Transaction Value",
        value=f'S${numerize(df_filtered["resale_price"].sum().item())}',
        help="Total value of all transactions during this period",
        delta=transaction_value_delta()
    )
    # met3.metric(
    #     label = 'Percentage',
    #     value = f"{(df_filtered['resale_price'].count() / len(df_merged.query('month >= @min_date & month <= @max_date')) * 100):.2f}%",
    #     help = f'Proportion of total transactions for this period'
    # )
    # row 2
    met4, met5, met6 = st.columns(3)
    met4.metric(
        label="Lowest Price",
        value=f'S${df_filtered["resale_price"].min():,}',
        help="Lowest resale transaction price during this period",
        delta=min_price_delta(),
        delta_color="inverse"
    )
    met5.metric(
        label="Highest Price",
        value=f'S${numerize(df_filtered["resale_price"].max())}',
        help="Highest resale transaction price during this period",
        delta=max_price_delta(),
        delta_color="inverse"
    )
    met6.metric(
        label="Median Price",
        value=f'S${int(df_filtered["resale_price"].median()):,}',
        help="Median price of all transactions during this period",
        delta=median_price_delta(),
        delta_color="inverse"
    )

st.markdown("---")

# @st.experimental_memo(max_entries=5)
# def create_choropeth(source):
#     fig = px.choropleth_mapbox(
#         source,
#         geojson=st.session_state.geo_df,
#         locations="town",
#         color="resale_price",
#         featureidkey="properties.PLN_AREA_N",
#         color_continuous_scale="Sunsetdark",
#         center={"lat": 1.35, "lon": 103.80},
#         mapbox_style="carto-positron",
#         opacity=0.7,
#         labels={"town": "Town", "resale_price": "Median Resale Price"},
#         zoom=10,
#     )

#     fig.update_layout(
#         title={"text": f"Median Resale Price by Town in {year}"},
#         height=550,
#         width=700,
#     )

#     # if town_option != "All":
#     #     fig.update_coloraxes(showscale=False)
#     return fig

with st.container():
    fig = px.choropleth_mapbox(
        map_df,
        geojson=st.session_state.geo_df,
        locations="town",
        color="resale_price",
        featureidkey="properties.PLN_AREA_N",
        color_continuous_scale="Sunsetdark",
        center={"lat": 1.35, "lon": 103.80},
        mapbox_style="carto-positron",
        opacity=0.7,
        labels={"town": "Town", "resale_price": "Median Resale Price"},
        zoom=10,
    )

    fig.update_layout(
        title={"text": f"Median Resale Price by Town in {year}"},
        height=550,
        width=700,
    )

    # fig = create_choropeth(map_df)

    if town_option != "All":
        fig.update_coloraxes(showscale=False)

    st.plotly_chart(fig, use_container_width=True)

with st.container():
    median_price = (
        alt.Chart(resale_price, title="Median Resale Price by Month")
        .mark_line(point=True)
        .encode(
            alt.X(
                "month:T",
                axis=alt.Axis(
                    formatType="time",
                    format="%b-%y",
                    title="Transaction Period",
                    grid=False,
                    tickCount="month",
                ),
            ),
            alt.Y(
                "resale_price:Q",
                axis=alt.Axis(
                    title="Resale Price (S$)", formatType="number", format="~s"
                ),
                scale=alt.Scale(
                    domain=get_scale(resale_price["resale_price"])
                ),
            ),
        )
        .properties(
            height=300,
        )
    )

    # creates selection that chooses the nearest point
    median_price_nearest = alt.selection_single(
        nearest=True, on="mouseover", fields=["month"], empty="none"
    )

    # selectors that tell us the x-value of the cursor
    median_price_selector = (
        median_price.mark_point(color="red")
        .encode(
            x="month",
            opacity=alt.condition(median_price_nearest, alt.value(1), alt.value(0)),
            tooltip=[
                alt.Tooltip("month", title="Transaction Period", format="%b-%y"),
                alt.Tooltip("resale_price", title="Median Resale Price", format="$,"),
            ],
        )
        .add_selection(median_price_nearest)
    )

    # draw a rule at location of selection
    median_price_rule = (
        median_price.mark_rule(color="gray")
        .encode(
            x="month",
        )
        .transform_filter(median_price_nearest)
    )

    # visualise number of transactions by month
    transactions_by_month = (
        alt.Chart(resale_transactions, title="Monthly Transactions by Month")
        .mark_line(
            point=alt.OverlayMarkDef(filled=True, fill='green'),
            color='green')
        .encode(
            alt.X(
                "month:T",
                axis=alt.Axis(
                    formatType="time",
                    format="%b-%y",
                    title="Transaction Period",
                    grid=False,
                    tickCount="month",
                ),
            ),
            alt.Y(
                "town:Q",
                axis=alt.Axis(
                    title="Transactions",
                    formatType="number",
                ),
                scale=alt.Scale(
                    domain=get_scale(resale_transactions["town"])
                ),
            ),
        )
        .properties(
            height=300,
        )
    )

    # creates selection that chooses the nearest point
    transactions_nearest = alt.selection_single(
        nearest=True, on="mouseover", fields=["month"], empty="none"
    )

    # selectors that tell us the x-value of the cursor
    transactions_selector = (
        transactions_by_month.mark_point(color="red")
        .encode(
            x="month",
            opacity=alt.condition(transactions_nearest, alt.value(1), alt.value(0)),
            tooltip=[
                alt.Tooltip("month", title="Transaction Period", format="%b-%y"),
                alt.Tooltip("town", title="Resale Transactions"),
            ],
        )
        .add_selection(transactions_nearest)
    )

    # draw a rule at location of selection
    transactions_rule = (
        transactions_by_month.mark_rule(color="gray")
        .encode(
            x="month",
        )
        .transform_filter(transactions_nearest)
    )

    st.altair_chart(
        median_price + median_price_selector + median_price_rule  | transactions_by_month + transactions_selector + transactions_rule,
        use_container_width=True,
    )

with st.container():
    st.markdown("Click to filter by flat types, hold shift to select multiple options.")
    selector = alt.selection_multi(empty="all", fields=["flat_type"])

    flat_base = alt.Chart(
        df_filtered,
    ).add_selection(selector)

    flat_type = (
        flat_base.mark_bar()
        .encode(
            alt.X("count()", axis=alt.Axis(title="Transactions")),
            alt.Y("flat_type:N", axis=alt.Axis(title="Flat Type")),
            color=alt.condition(
                selector, "flat_type:N", alt.value("lightgray"), legend=None
            ),
            tooltip=[
                alt.Tooltip("flat_type", title="Flat Type"),
                alt.Tooltip("count()", title="Transactions", format=","),
            ],
        )
        .properties(
            height=300,
            title="Transactions by Flat Type"
        )
    )

    floor_area = (
        flat_base.mark_bar(opacity=0.8, binSpacing=0)
        .encode(
            alt.X(
                "floor_area_sqm:Q",
                bin=alt.Bin(step=5),
                axis=alt.Axis(title="Floor Area (sqm)"),
            ),
            alt.Y("count()", stack=None, axis=alt.Axis(title="Count")),
            alt.Color("flat_type:N", legend=None),
        )
        .transform_filter(selector)
        .properties(
            height=300,
            title="Distribution of Floor Area by Flat Type"
        )
    )

    st.altair_chart(flat_type | floor_area, use_container_width=True)

# with st.container():
#     scatter_plot = alt.Chart(
#         df_filtered
#     ).mark_point().encode(
#         x="floor_area_sqm:Q",
#         y="resale_price:Q",
#         color='town:N'
#     )

#     st.altair_chart(scatter_plot, use_container_width=True)