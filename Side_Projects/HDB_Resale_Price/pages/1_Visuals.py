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
    switch_page("Home")

towns = st.session_state.df["town"].unique()
towns = sorted(towns)
towns.insert(0, "All Towns")

years = list(st.session_state.df["year"].unique())
years = sorted(years, reverse=True)
years.insert(0, "All Years")


def get_scale(series: pd.Series) -> list[int, int]:
    scale_min = int(series.min() * 0.9)
    scale_max = int(series.max() * 1.1)
    return [scale_min, scale_max]


def get_delta(var:str, type:str) -> str:
    if year_option != "All Years" and year_option != years[-1]:
        if type == "count":
            delta = (df_filtered[var].count() - df_filtered_previous_year[var].count())
        elif type == "sum":
            delta = (df_filtered[var].sum() - df_filtered_previous_year[var].sum())
        elif type == "min":
            delta = (df_filtered[var].min() - df_filtered_previous_year[var].min())
        elif type == "max":
            delta = (df_filtered[var].max() - df_filtered_previous_year[var].max())
        elif type == "median":
            delta = (df_filtered[var].median() - df_filtered_previous_year[var].median())
        return f"{numerize(delta)} vs {year_option-1}" 

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


def add_marker(base_chart, nearest, tooltip_y_val:str, tooltip_y_title:str, tooltip_y_format:str):
    '''
    Adds a selector indiator and rule to altair chart
    '''
    # selectors that tell us the x-value of the cursor
    selector = (
        base_chart.mark_point(color="red")
        .encode(
            x="date",
            opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
            tooltip=[
                alt.Tooltip("date", title="Transaction Period", format="%b-%y"),
                alt.Tooltip(
                    tooltip_y_val, title=tooltip_y_title, format=tooltip_y_format
                ),
            ]
        )
        .add_selection(nearest)
    )

    # draw a rule at location of selection
    rule = (
        base_chart.mark_rule(color="gray")
        .encode(x="date")
        .transform_filter(nearest)
    )

    return selector, rule


# sidebar for filtering dashboard
with st.sidebar:
    st.header("Filter options")
    town_option = st.selectbox(label="Town", options=towns)

    year_option = st.selectbox(label="Year", options=years)

    st.markdown(
        """
        ---
        
        Created by Shawn

        - Happy to connect on [LinkedIn](https://www.linkedin.com/in/shawn-sing/)
        - Check out my other projects on [GitHub](https://github.com/eeshawn11/)
        """
    )

# filter df based on selected parameters
if town_option == "All Towns":
    if year_option == "All Years":
        df_filtered = st.session_state.df
    else:
        df_filtered = st.session_state.df.query("date.dt.year == @year_option")
        df_filtered_previous_year = st.session_state.df.query(
            "date.dt.year == @year_option-1"
        )
else:
    if year_option == "All Years":
        df_filtered = st.session_state.df.query("town.str.contains(@town_option)")
    else:
        df_filtered = st.session_state.df.query(
            "date.dt.year == @year_option & town.str.contains(@town_option)"
        )
        df_filtered_previous_year = st.session_state.df.query(
            "date.dt.year == @year_option-1 & town.str.contains(@town_option)"
        )

# median price choropleth
median_map_df = df_filtered.groupby("town").resale_price.agg(["count", "median"]).reset_index()
# choropleth scatter overlay
million_dollar_flats_df = df_filtered[df_filtered["resale_price"] >= 1_000_000][["resale_price", "town", "latitude", "longitude", "address", "flat_type"]]
million_dollar_flats_df["text"] = million_dollar_flats_df["flat_type"].str.title() +  " flat at " +  million_dollar_flats_df["address"].astype(str).str.title() + ", sold for $" + million_dollar_flats_df["resale_price"].apply(lambda x: f"{x:,}")
# scatter plot
scatter_df = df_filtered[["year", "town", "floor_area_sqm", "price_per_sqm"]]
scatter_df = scatter_df.sort_values(by="year", ascending=True)
# resale transactions line chart
resale_transactions_df = df_filtered.groupby("date").agg({"town": "count", "resale_price": "median"}).reset_index()
index_benchmark = 400000 # price as of Jan 2020
resale_transactions_df["price_index"] = resale_transactions_df["resale_price"] / index_benchmark * 100
resale_transactions_df[["resale_price", "price_index"]] = resale_transactions_df[["resale_price", "price_index"]].round(0).astype("int32")
# flat type distribution
flat_type_df = df_filtered[["flat_type", "floor_area_sqm"]]
flat_type_df["flat_type"] = flat_type_df["flat_type"].str.replace("MULTI-GENERATION", "EXECUTIVE")
flat_type_df["flat_type"] = flat_type_df["flat_type"].str.replace("EXECUTIVE", "EXECUTIVE*")

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
        delta=get_delta("resale_price", "count")
    )
    met2.metric(
        label="Total Transaction Value",
        value=f'S${numerize(df_filtered["resale_price"].sum().item())}',
        help="Total value of all transactions during this period",
        delta=get_delta("resale_price", "sum")
    )
    # row 2
    met4, met5, met6 = st.columns(3)
    met4.metric(
        label="Lowest Price",
        value=f'S${df_filtered["resale_price"].min():,}',
        help="Lowest resale transaction price during this period",
        delta=get_delta("resale_price", "min"),        
        delta_color="inverse",
    )
    met5.metric(
        label="Highest Price",
        value=f'S${numerize(df_filtered["resale_price"].max())}',
        help="Highest resale transaction price during this period",
        delta=get_delta("resale_price", "max"),
        delta_color="inverse",
    )
    met6.metric(
        label="Median Price",
        value=f'S${int(df_filtered["resale_price"].median()):,}',
        help="Median price of all transactions during this period",
        delta=get_delta("resale_price", "median"),
        delta_color="inverse",
    )

st.markdown("---")


###
# WIP - create individual trace layers for $m flats by year?
# WIP - include average PSF comparisons]
# WIP - include transaction count comparison?   
# show / hide choropeth layer?
# include buttons to change mapbox style?
###
with st.container():
    row1_tab1, row1_tab2 = st.tabs(["Median Resale Price", "Price per sqm"])
    st.markdown("---")

with row1_tab1:
    st.markdown(
        """
        A choropleth map based on the boundary lines provided by the URA 2014 Master Plan Planning Areas. 
        
        - The planning areas are coloured based on the median resale price in each area during the selected time period.
        - Stars on the map represent transactions that have crossed the coveted S$1 million threshold.
        """
    )

    median_map_plot = px.choropleth_mapbox(
        median_map_df,
        geojson=st.session_state.geo_df,
        locations="town",
        color="median",
        featureidkey="properties.PLN_AREA_N",
        color_continuous_scale="Sunsetdark",
        center={"lat": 1.35, "lon": 103.80},
        opacity=0.75,
        hover_name="town",
        hover_data={
            "town": False,
            "count": ":,",
            "median": ":,"
        },
        labels={"town": "Town", "count": "Transactions", "median": "Median Resale Price"},
    )

    median_map_plot.update_layout(
        title={
            "text": f"{year_option} Median Resale Price by Town",
            "x": 0.5,
            "xanchor": "center",
        },
        height=700,
        mapbox={
            "accesstoken": st.secrets["mapbox_token"],
            "style": "streets",
            "zoom": 10,
            "bounds": {"west": 103.5, "east": 104.2, "north": 1.55, "south": 1.15} # not working locally
        },
        coloraxis_colorbar={
            "title": None,
            "y": 0.5,
            "yanchor": "middle",
            "len": 1,
            "ypad": 0,
            "xpad": 0
        }
    )

    median_map_plot.add_annotation(
            text="Stars representing Million Dollar Flats",
            xref="paper", yref="paper",
            xanchor="left",
            yanchor="top",
            x=0,
            y=1.045,
            showarrow=False
        )

    median_map_plot.add_scattermapbox(
        below="",
        lat=million_dollar_flats_df["latitude"],
        lon=million_dollar_flats_df["longitude"],
        text=million_dollar_flats_df["text"],
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

    st.plotly_chart(median_map_plot, use_container_width=True)

with row1_tab2:
    st.markdown("WIP, check back soon. :)")
#     st.markdown(
#         """
#         A choropleth map based on the boundary lines provided by the URA 2014 Master Plan Planning Areas. 
        
#         - The planning areas are coloured based on the average price per sqm in each area during the selected time period.
#         """
#     )

#     map_plot = px.choropleth_mapbox(
#         psqm_map_df,
#         geojson=st.session_state.geo_df,
#         locations="town",
#         color="price_per_sqm",
#         featureidkey="properties.PLN_AREA_N",
#         color_continuous_scale="Sunsetdark",
#         center={"lat": 1.35, "lon": 103.80},
#         opacity=0.75,
#         hover_name="town",
#         hover_data={
#             "town": False,
#             "price_per_sqm": ":,"
#         },
#         labels={"town": "Town", "price_per_sqm": "Average Price per SQM"},
#     )

#     map_plot.update_layout(
#         title={
#             "text": f"{year_option} Average Price per SQM by Town",
#             "x": 0.5,
#             "xanchor": "center",
#         },
#         height=700,
#         mapbox={
#             "accesstoken": st.secrets["mapbox_token"],
#             "style": "dark",
#             "zoom": 10,
#             # "bounds": {"west": 103.5, "east": 104.2, "north": 1.55, "south": 1.15} # not working locally
#         },
#         coloraxis_colorbar_y=0.64,
#     )

#     st.plotly_chart(map_plot, use_container_width=True)

with st.container():
    row2_tab1, row2_tab2 = st.tabs(["Resale Price Index", "Median Resale Price"])
    st.markdown("---")

transactions_base = (
    alt.Chart(resale_transactions_df, title="Total Transactions per Month")
    .mark_line(
        color="green"
    )
    .encode(
        alt.X(
            "date:T",
            axis=alt.Axis(
                formatType="time",
                format="%b-%y",
                title=None,
                grid=False,
                tickCount="month",
            ),
        ),
        alt.Y(
            "town:Q",
            axis=alt.Axis(
                title="Transactions",
                formatType="number",
            )
        ),
    )
    .properties(
        height=300,
    )
)

# creates selection that chooses the nearest point
alt_nearest = alt.selection_single(
    nearest=True, on="mouseover", fields=["date"], empty="none"
)

transactions_selector, transactions_rule = add_marker(transactions_base, alt_nearest, "town", "Resale Transactions", ",")
transactions_plot = transactions_base + transactions_selector + transactions_rule

price_index_base = (
    alt.Chart(resale_transactions_df, title="Resale Price Index^")
    .mark_line(
        color="orange"
    )
    .encode(
        alt.X(
            "date:T",
            axis=alt.Axis(
                formatType="time",
                format="%b-%y",
                title="Transaction Period",
                grid=False,
                tickCount="month",
            )
        ),
        alt.Y(
            "price_index:Q", 
            axis=alt.Axis(
                title="Price Index",
                grid=False
            ),
            scale=alt.Scale(domain=get_scale(resale_transactions_df["price_index"]))
        )
    )
    .properties(
        height=300,
    )
)

price_index_selector, price_index_rule = add_marker(price_index_base, alt_nearest, "price_index", "Price Index", ",")
price_index_plot = price_index_base + price_index_selector + price_index_rule

median_price_base = (
    alt.Chart(resale_transactions_df, title="Median Resale Price^ by Month")
    .mark_line()
    .encode(
        alt.X(
            "date:T",
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
        ),
    )
    .properties(
        height=300,
    )
)

median_price_selector, median_price_rule = add_marker(median_price_base, alt_nearest, "resale_price", "Median Resale Price", "$,")
median_price_plot = median_price_base + median_price_selector + median_price_rule

with row2_tab1:
    # show line at price index = 100
    if resale_transactions_df.price_index.min() <= 100 and resale_transactions_df.price_index.max() >= 100:
        resale_price_index_line = alt.Chart(
            resale_transactions_df).mark_rule(color="gray", strokeDash=[4, 4], strokeOpacity=0.1).encode(y=alt.datum(100)
            )
        st.altair_chart(transactions_plot,use_container_width=True)
        st.altair_chart(price_index_plot + resale_price_index_line,use_container_width=True)
    else:
        st.altair_chart(transactions_plot, use_container_width=True)
        st.altair_chart(price_index_plot,use_container_width=True)
    st.markdown("^ Base period is taken at Jan 2020 ($400k) across all towns and flat types, with index at 100")

with row2_tab2:
    st.altair_chart(transactions_plot,use_container_width=True)
    st.altair_chart(median_price_plot,use_container_width=True)
    st.markdown("^ Median price across all flat types and models.")

# with st.container():
#     scatter_range_x = get_scale(scatter_df["floor_area_sqm"])
#     scatter_range_y = get_scale(scatter_df["price_per_sqm"])

#     scatter_plot = px.scatter(
#         scatter_df,
#         x="floor_area_sqm",
#         y="price_per_sqm",
#         color="town",
#         hover_name="town",
#         animation_frame="year",
#         animation_group="town",
#         # size="address",
#         range_x=scatter_range_x,
#         range_y=scatter_range_y
#     )

#     scatter_plot.update_layout(
#         title={
#             "text": f"Price",
#             "x": 0.5,
#             "xanchor": "center",
#         },
#         height=500,
#         legend={
#             "title": None,
#             # "y": 0.5,
#             # "yanchor": "middle",
#         }
#     )

#     st.plotly_chart(scatter_plot, use_container_width=True)
#     st.markdown("---")

with st.container():
    st.markdown("Click to filter by flat types, hold shift to select multiple options.")
    selector = alt.selection_multi(empty="all", fields=["flat_type"])

    flat_base = alt.Chart(
        flat_type_df,
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
        .properties(height=300, width=400, title="Transactions by Flat Type")
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
        .properties(height=300, width=400, title="Distribution of Floor Area by Flat Type")
    )

    st.altair_chart(flat_type_plot | floor_area_plot, use_container_width=True)
    st.markdown("\* Includes Multi-Generation flats")