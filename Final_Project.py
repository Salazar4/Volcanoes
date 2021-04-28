"""
Name: Rigoberto Salazar
CS230: Section 5
Data: Volcanoes
URL: Link to your web application online (see extra credit)

Description: This program gives data about volcanoes in three ways.
The first way is a map where you can choose a country and it will
show the volcanoes for that country. The first chart that i made is a bar chart
that counts the frequency of three pieces of data. The user can decide which data
type they want to chart and how many they want to see in the chart. They could look at
the top 10 of the data or top 50 using a slider. The final chart will allow the
user to choose between 2-5 countries and the user will receive a grouped bar
chart of the mean, max and min of the volcano elevations for those countries.
"""
import pandas as pd
import streamlit as st
import numpy as np
import pydeck as pdk
import plotly.express as px
import itertools

@st.cache(suppress_st_warning=True)
def location_map(locations, country_choice):
    ICON = "https://image.flaticon.com/icons/png/512/2206/2206599.png"
    tool_tip = {"html": "<b>Volcano Name:<br/> <b>{Volcano Name}</br> Last Known Eruption:<br/> <b>{Last Known Eruption}</b> ",
                "style": {"backgroundColor": "steelblue", "color": "white"}}

    st.header(f" Map of {country_choice} Volcanos")

    view_state = pdk.ViewState(
        latitude=locations["lat"].mean(),
        longitude=locations["lon"].mean(),
        zoom=4,
        pitch=0)

    #Create an icon layer
    icon_data = {
            "url": ICON,
            "width": 242,
            "height": 242,
            "anchorY": 242,
        }

    locations["icon_data"] = None
    for i in locations.index:
        locations["icon_data"][i] = icon_data

    icon_layer = pdk.Layer(
            type="IconLayer",
            data=locations,
            get_icon="icon_data",
            get_size=4,
            size_scale=15,
            get_position=["lon", "lat"],
            pickable=True,
            auto_highlight=True
        )

    r = pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=view_state,
                layers=[icon_layer],
                tooltip=tool_tip
    )

    st.pydeck_chart(r)




def bar_graph(Bar_Graph, df):
    # Count frequency of data using dictionary
    df.reset_index()
    freq_dict = {}
    list_of_item = list(df[Bar_Graph])
    for i in list_of_item:
        if i in freq_dict:
            freq_dict[i] += 1
        else:
            freq_dict[i] = 1

    # Sort dictionary by the most to least
    sorted_items = {}
    sorted_keys = sorted(freq_dict, key=freq_dict.get, reverse=True)
    for i in sorted_keys:
        sorted_items[i] = freq_dict[i]


    rank = st.slider(f"How many items to graph:",1,len(sorted_items),5)

    # Create a new dictionary, only including the amount chosen by the slider
    ranked_items = dict(itertools.islice(sorted_items.items(), rank))

    x = ranked_items.keys()
    y = ranked_items.values()

    fig = px.bar(x=x, y=y, color=y, title=f"Top {rank} Volcano Counts for {Bar_Graph}",
                 labels={'x':f'{Bar_Graph}', 'y':'Count'})
    st.plotly_chart(fig)


# Multiple Bars
# Compare data of countries: years(eruptions), highest elevation, average elevation
def elevation_graph(volcanoes, country_choices):

    multiple_bar = pd.DataFrame(volcanoes, columns=["Country", "Elevation (m)"])
    multiple_bar = multiple_bar.rename(columns={'Elevation (m)': 'Elevation'})
    multiple_bar = multiple_bar[multiple_bar.groupby('Country').Country.transform('count')>9].copy()

    selected_countries = multiple_bar.loc[multiple_bar['Country'].isin(country_choices)]

    # Find the aggregate information for the data
    avg_elevation = selected_countries.groupby("Country")["Elevation"].mean().astype(int).reset_index(name="Average Elevation")

    max_elevation = selected_countries.groupby("Country")["Elevation"].max().astype(int).reset_index(name="Max Elevation")
    max_elevation.pop("Country")

    min_elevation = selected_countries.groupby("Country")["Elevation"].min().astype(int).reset_index(name="Min Elevation")
    min_elevation.pop("Country")

    #Put the data together in one dataframe
    full_elevation = pd.concat([avg_elevation, max_elevation, min_elevation], ignore_index=False, sort=False, axis=1)

    st.write(full_elevation)

    #Create the grouped bar chart
    fig = px.bar(full_elevation, x=["Average Elevation", "Max Elevation", "Min Elevation"], y="Country", barmode='group',
                 title="Aggregate Information for Selected Countries' Elevation", labels={'variable':f'Elevation Calculation', 'value':'Elevation'})

    st.plotly_chart(fig)


def main():
    volcanoes = pd.read_csv("volcanoes.csv")

    df = pd.DataFrame(volcanoes, columns=['Volcano Number', 'Volcano Name',
                                          'Country', 'Primary Volcano Type', 'Activity Evidence', 'Last Known Eruption',
                                          'Region',
                                          'Subregion', 'Latitude', 'Longitude',
                                          'Elevation (m)', 'Dominant Rock Type', 'Tectonic Setting'])

    df = df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})
    # Select map or chart
    options = ['Home', 'Map', 'Counting Bar Chart', 'Elevation Bar Chart']

    options_choice = st.sidebar.radio("Select a Streamlit Option:", options)


    if options_choice == 'Home':
        #Home Menu
        st.title("Volcanoes!")
        st.image("Volcano_Image.jpeg")
        st.write("View all the data")
        st.dataframe(df)


    elif options_choice == 'Map':
        # User chooses a country to map
        country_order = df.sort_values('Country')
        countries = country_order["Country"].drop_duplicates().reset_index()
        country_choice = st.selectbox("Select a Country:", countries["Country"])

        locations = df[df["Country"] == country_choice][["Volcano Name", "Last Known Eruption", "Country", "lon", "lat"]]

        if st.button("Create Map"):
            location_map(locations, country_choice)

    elif options_choice == 'Counting Bar Chart':
        # User can decide the data and how many to put on the chart
        df = df.rename(columns={'Country': 'Countries'})
        Bar_Graph_Options = ["Countries", "Dominant Rock Type", "Primary Volcano Type"]
        Bar_Graph = st.selectbox('Select Bar Graph', Bar_Graph_Options)

        bar_graph(Bar_Graph, df)

    else:
        # User chooses the countries to compare
        st.write("Compare the elevation of volcanoes between countries.")
        country_order = df.sort_values('Country')
        country_order = country_order[country_order.groupby('Country').Country.transform('count')>9].copy()
        countries = country_order["Country"].drop_duplicates().reset_index()
        country_choices = st.multiselect("Select 2-5 Countries To Compare:", countries["Country"])

        if len(country_choices) == 0:
            st.write("Please select countries at least 2 countries")
        elif len(country_choices) == 1:
            st.write("Please select countries at least 1 more country")
        elif len(country_choices) >= 6:
            st.write("Please remove countries to have 5 maximum")
        else:
            if st.button("Create Graph"):
                elevation_graph(volcanoes, country_choices)



main()
