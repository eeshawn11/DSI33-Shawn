import pandas as pd
import streamlit as st
import numpy as np
import altair as alt
import plotly.express as px
from decimal import Decimal
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide")
alt.data_transformers.enable("json")

if "df" not in st.session_state:
    st.error("Error: DataFrame not found, redirecting to Home")
    switch_page("Home")

towns = st.session_state.df["town"].unique()
towns = sorted(towns)
towns.insert(0, "All")

years = list(st.session_state.df["month"].dt.year.unique())
years = sorted(years, reverse=True)
years.insert(0, "All")


def magnitude(value: int) -> int:
    if value == 0:
        return 0
    return int(np.floor(np.log10(abs(value))))


def get_buffer(value: int) -> int:
    try:
        buffer = 10 ** magnitude(value) / magnitude(value)
        return buffer
    except:
        return 0


def get_scale(series: pd.Series) -> list[int, int]:
    scale_min = series.min() - get_buffer(series.min())
    if scale_min <= 50:
        scale_min = 0
    scale_max = series.max() + get_buffer(series.max())
    return [scale_min, scale_max]


def resale_transaction_delta() -> str:
    if year_option != "All" and year_option != years[-1]:
        delta = (
            df_filtered["resale_price"].count()
            - df_filtered_previous_year["resale_price"].count()
        )
        return f"{delta:,} vs {year_option-1}"


def transaction_value_delta() -> str:
    if year_option != "All" and year_option != years[-1]:
        delta = (
            df_filtered["resale_price"].sum()
            - df_filtered_previous_year["resale_price"].sum()
        )
        return f"{numerize(delta.item())} vs {year_option-1}"


def min_price_delta() -> str:
    if year_option != "All" and year_option != years[-1]:
        delta = (
            df_filtered["resale_price"].min()
            - df_filtered_previous_year["resale_price"].min()
        )
        return f"{delta:,} vs {year_option-1}"


def max_price_delta() -> str:
    if year_option != "All" and year_option != years[-1]:
        delta = (
            df_filtered["resale_price"].max()
            - df_filtered_previous_year["resale_price"].max()
        )
        return f"{delta:,} vs {year_option-1}"


def median_price_delta() -> str:
    if year_option != "All" and year_option != years[-1]:
        delta = (
            df_filtered["resale_price"].median()
            - df_filtered_previous_year["resale_price"].median()
        )
        return f"{delta:,} vs {year_option-1}"


def round_num(n, decimals):
    return n.to_integral() if n == n.to_integral() else round(n.normalize(), decimals)


def drop_zero(n):
    n = str(n)
    return n.rstrip("0").rstrip(".") if "." in n else n


def numerize(n, decimals=2):
    """
    Adapted from numerize (https://github.com/davidsa03/numerize) to handle numbers over 1 million only
    """
    is_negative_string = ""
    if n < 0:
        is_negative_string = "-"
    try:
        n = abs(Decimal(n))
    except:
        n = abs(Decimal(n.item()))
    if n >= 1000000 and n < 1000000000:
        if n % 1000000 == 0:
            return is_negative_string + str(int(n / 1000000)) + "M"
        else:
            n = n / 1000000
            return is_negative_string + str(drop_zero(round_num(n, decimals))) + "M"
    elif n >= 1000000000 and n < 1000000000000:
        if n % 1000000000 == 0:
            return is_negative_string + str(int(n / 1000000000)) + "B"
        else:
            n = n / 1000000000
            return is_negative_string + str(drop_zero(round_num(n, decimals))) + "B"
    elif n >= 1000000000000 and n < 1000000000000000:
        if n % 1000000000000 == 0:
            return is_negative_string + str(int(n / 1000000000000)) + "T"
        else:
            n = n / 1000000000000
            return is_negative_string + str(drop_zero(round_num(n, decimals))) + "T"
    else:
        return is_negative_string + f"{n:,}"


# create sidebar for filtering dashboard
with st.sidebar:
    st.header("Filter options")
    town_option = st.selectbox(label="District", options=towns)

    year_option = st.selectbox(label="Year", options=years)

    st.markdown(
        """
        ---
        
        Created by Shawn

        - Happy to connect on [LinkedIn](https://www.linkedin.com/in/shawn-sing/)
        - Check out my [GitHub](https://github.com/eeshawn11/) for other projects
        """
    )

# filter df based on selected parameters
if town_option == "All":
    if year_option == "All":
        df_filtered = st.session_state.df
    else:
        df_filtered = st.session_state.df.query("month.dt.year == @year_option")
        df_filtered_previous_year = st.session_state.df.query(
            "month.dt.year == @year_option-1"
        )
else:
    if year_option == "All":
        df_filtered = st.session_state.df.query("town.str.contains(@town_option)")
    else:
        df_filtered = st.session_state.df.query(
            "month.dt.year == @year_option & town.str.contains(@town_option)"
        )
        df_filtered_previous_year = st.session_state.df.query(
            "month.dt.year == @year_option-1 & town.str.contains(@town_option)"
        )

# create dataframes for individual plot displays
map_df = df_filtered.groupby("town").resale_price.agg(["count", "median"]).reset_index()
resale_price = df_filtered.groupby("month").resale_price.median().reset_index()
resale_transactions = df_filtered.groupby("month").town.count().reset_index()
million_dollar_flats = df_filtered[df_filtered["resale_price"] >= 1_000_000][["resale_price", "town", "latitude", "longitude", "address", "flat_type"]]
million_dollar_flats["text"] = million_dollar_flats["flat_type"].str.title() +  " flat at " +  million_dollar_flats["address"].astype(str).str.title() + ", sold for $" + million_dollar_flats["resale_price"].apply(lambda x: f"{x:,}")

with st.container():
    st.title("Singapore HDB Resale Price from 2012")

with st.container():
    st.markdown(f"## {year_option} transactions in {town_option}")
    st.markdown("### Key Metrics")
    # row 1
    met1, met2, met3 = st.columns(3)
    met1.metric(
        label="Total Resale Transactions",
        value=f"{df_filtered['resale_price'].count():,}",
        help="Total resale transactions during this period",
        delta=resale_transaction_delta(),
    )
    met2.metric(
        label="Total Transaction Value",
        value=f'S${numerize(df_filtered["resale_price"].sum().item())}',
        help="Total value of all transactions during this period",
        delta=transaction_value_delta(),
    )
    # row 2
    met4, met5, met6 = st.columns(3)
    met4.metric(
        label="Lowest Price",
        value=f'S${df_filtered["resale_price"].min():,}',
        help="Lowest resale transaction price during this period",
        delta=min_price_delta(),
        delta_color="inverse",
    )
    met5.metric(
        label="Highest Price",
        value=f'S${numerize(df_filtered["resale_price"].max())}',
        help="Highest resale transaction price during this period",
        delta=max_price_delta(),
        delta_color="inverse",
    )
    met6.metric(
        label="Median Price",
        value=f'S${int(df_filtered["resale_price"].median()):,}',
        help="Median price of all transactions during this period",
        delta=median_price_delta(),
        delta_color="inverse",
    )

st.markdown("---")


###
# WIP - create individual trace layers for $m flats by year
# WIP - include average PSF comparisons
###
with st.container():
    st.markdown(
        """
        A choropleth map based on the boundary lines provided by the URA 2014 Master Plan Planning Areas. 
        
        - The planning areas are coloured based on the median resale price in each area during the selected time period.
        - Stars on the map represent transactions that have crossed the coveted S$1 million threshold.
        """
    )

    map_plot = px.choropleth_mapbox(
        map_df,
        geojson=st.session_state.geo_df,
        locations="town",
        color="median",
        featureidkey="properties.PLN_AREA_N",
        color_continuous_scale="Sunsetdark",
        center={"lat": 1.35, "lon": 103.80},
        opacity=0.5,
        hover_name="town",
        hover_data={
            "town": False,
            "count": ":,",
            "median": ":,"
        },
        labels={"town": "Town", "count": "Transactions", "median": "Median Resale Price"},
    )

    map_plot.update_layout(
        title={
            "text": f"{year_option} Median Resale Price by Town",
            "x": 0.5,
            "xanchor": "center",
        },
        height=700,
        mapbox={
            "accesstoken": st.secrets["mapbox_token"],
            "style": "dark",
            "zoom": 10,
            "bounds": {"west": 103.5, "east": 104.2, "north": 1.55, "south": 1.15}
        },
    )

    map_plot.add_scattermapbox(
        below="",
        lat=million_dollar_flats["latitude"],
        lon=million_dollar_flats["longitude"],
        text=million_dollar_flats["text"],
        mode="markers",
        marker={"symbol": "star", "size": 5, "opacity": 0.9, "allowoverlap": True},
        hovertemplate="<b>Million-Dollar Flat</b><br><br>"
        + "%{text}"
        + "<extra></extra>",
        hoverlabel={
            "bgcolor": "snow",
            "font_color" : "black"
        },
    )

    st.plotly_chart(map_plot, use_container_width=True)

with st.container():
    chart1, chart2 = st.columns(2)

    with chart1:
        # visualise median monthly resale price
        median_price_plot = (
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
                    scale=alt.Scale(domain=get_scale(resale_price["resale_price"])),
                ),
            )
            .properties(
                height=350,
            )
        )

        # creates selection that chooses the nearest point
        median_price_nearest = alt.selection_single(
            nearest=True, on="mouseover", fields=["month"], empty="none"
        )

        # selectors that tell us the x-value of the cursor
        median_price_selector = (
            median_price_plot.mark_point(color="red")
            .encode(
                x="month",
                opacity=alt.condition(median_price_nearest, alt.value(1), alt.value(0)),
                tooltip=[
                    alt.Tooltip("month", title="Transaction Period", format="%b-%y"),
                    alt.Tooltip(
                        "resale_price", title="Median Resale Price", format="$,"
                    ),
                ],
            )
            .add_selection(median_price_nearest)
        )

        # draw a rule at location of selection
        median_price_rule = (
            median_price_plot.mark_rule(color="gray")
            .encode(
                x="month",
            )
            .transform_filter(median_price_nearest)
        )

        st.altair_chart(
            median_price_plot + median_price_selector + median_price_rule,
            use_container_width=True,
        )

    with chart2:
        # visualise number of transactions by month
        transactions_by_month_plot = (
            alt.Chart(resale_transactions, title="Monthly Transactions by Month")
            .mark_line(
                point=alt.OverlayMarkDef(filled=True, fill="green"), color="green"
            )
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
                    scale=alt.Scale(domain=get_scale(resale_transactions["town"])),
                ),
            )
            .properties(
                height=350,
            )
        )

        # creates selection that chooses the nearest point
        transactions_nearest = alt.selection_single(
            nearest=True, on="mouseover", fields=["month"], empty="none"
        )

        # selectors that tell us the x-value of the cursor
        transactions_selector = (
            transactions_by_month_plot.mark_point(color="red")
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
            transactions_by_month_plot.mark_rule(color="gray")
            .encode(
                x="month",
            )
            .transform_filter(transactions_nearest)
        )

        st.altair_chart(
            transactions_by_month_plot + transactions_selector + transactions_rule,
            use_container_width=True,
        )

with st.container():
    st.markdown("Click to filter by flat types, hold shift to select multiple options.")
    selector = alt.selection_multi(empty="all", fields=["flat_type"])

    flat_base = alt.Chart(
        df_filtered,
    ).add_selection(selector)

    flat_type_plot = (
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
        .properties(height=350, title="Transactions by Flat Type")
    )

    floor_area_plot = (
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
        .properties(height=350, title="Distribution of Floor Area by Flat Type")
    )

    st.altair_chart(flat_type_plot | floor_area_plot, use_container_width=True)

###
# WIP - create chart showing relationship between property age, size and price?
###
# with st.container():
#     property_age = (
#         alt.Chart(df_filtered)
#         .mark_circle()
#         .encode(
#             x="age:Q",
#             y="resale_price:Q",
#             color="flat_type:N"
#             # alt.X(
#             #     "age:Q",
#                 # axis=alt.Axis(
#                 #     formatType="time",
#                 #     format="%b-%y",
#                 #     title="Transaction Period",
#                 #     grid=False,
#                 #     tickCount="month",
#                 # ),
#             # ),
#             # alt.Y(
#             #     "resale_price:Q",
#                 # axis=alt.Axis(
#                 #     title="Transactions",
#                 #     formatType="number",
#                 # ),
#                 # scale=alt.Scale(domain=get_scale(df_filtered["town"])),
#             # ),
#         )
#         # .properties(
#         #     height=300,
#         # )
#     )

#     st.altair_chart(property_age, use_container_width=True)
