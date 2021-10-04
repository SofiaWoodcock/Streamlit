%%writefile streamlit_app.py
# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An example of showing geographic data."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns(2)

with row1_1:
    st.title("Number of Travelling Started Data in January 2019 (Date 1-5)")
    date_selected = st.selectbox("Date of January,2019",("1", "2","3","4","5"))
    hour_selected = st.slider("Select hour", 0, 23)

with row1_2:
    st.write(
    """
    ##
    Examining the number of travelling started for near Bangkok area .
    By sliding the slider on the left and selecting date you can view different slices of date and time and explore different transportation trends.
    by Audcharapan Woodcock 6130834821
    """)

# LOADING DATA
DATE_TIME = "date/time"

D1 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190101.csv")
D2 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190102.csv")
D3 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190103.csv")
D4 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190104.csv")
D5 = ("https://raw.githubusercontent.com/Maplub/odsample/master/20190105.csv")

if date_selected == "1" :
  DATA_URL = D1
elif date_selected == "2" :
  DATA_URL = D2
elif date_selected == "3" :
  DATA_URL = D3
elif date_selected == "4" :
  DATA_URL = D4
elif date_selected == "5" :
  DATA_URL = D5

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data = data[['timestart','latstartl','lonstartl']].copy()
    data = data.rename(columns = {'timestart': 'Date/Time'}, inplace = False)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
    return data

data1 = load_data(100000)

# CREATING FUNCTION FOR MAPS

def map(data, latstartl, lonstartl, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": latstartl,
            "longitude": lonstartl,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lonstartl", "latstartl"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))

# FILTERING DATA BY HOUR SELECTED
data1 = data1[(data1[DATE_TIME].dt.hour == hour_selected)]

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2 = st.columns(2)

# SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS
zoom_level = 12
midpoint = [13.7563, 100.5018]

with row2_1:
    st.write("**All started from %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))
    map(data1, midpoint[0], midpoint[1], 12)

with row2_2:
    st.write("**All started from %i:00 and %i:00**" % (hour_selected, (hour_selected + 3) % 24))
    map(data1, midpoint[0], midpoint[1], 12)

# FILTERING DATA FOR THE HISTOGRAM
filtered1 = data1[
    (data1[DATE_TIME].dt.hour >= hour_selected) & (data1[DATE_TIME].dt.hour < (hour_selected + 1))
    ]

hist = np.histogram(filtered1[DATE_TIME].dt.minute, bins=24, range=(0, 23))[0]

chart_data = pd.DataFrame({"minute": range(24), "Number of travelling (start)": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("** travelling (start) per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("Number of travelling (start):Q"),
        tooltip=['minute', 'Number of travelling (start)']
    ).configure_mark(
        opacity=0.4,
        color='blue'
    ), use_container_width=True)
