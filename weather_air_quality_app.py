import streamlit as st
import requests
from streamlit_folium import folium_static
import folium

# Your API Key
api_key = "864b4e93-b19e-4ca3-8960-0859cab989c9"

# Title and Header
st.title("Weather and Air Quality Web App")
st.header("Streamlit and AirVisual API")

# Select category
display_options = ["By City, State, and Country", "By Nearest City (IP Address)", "By Latitude and Longitude"]
category = st.selectbox("Choose how you'd like to search:", options=display_options)

# Cache functions
@st.cache_data
def map_creator(latitude, longitude):
    # center on the station
    m = folium.Map(location=[latitude, longitude], zoom_start=10)

    # add marker for the station
    folium.Marker([latitude, longitude], popup="Station", tooltip="Station").add_to(m)

    # call to render Folium map in Streamlit
    folium_static(m)

@st.cache_data
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    countries_dict = requests.get(countries_url).json()
    return countries_dict

@st.cache_data
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={api_key}"
    states_dict = requests.get(states_url).json()
    return states_dict

@st.cache_data
def generate_list_of_cities(state_selected, country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={api_key}"
    cities_dict = requests.get(cities_url).json()
    return cities_dict

# By City, State, and Country
if category == "By City, State, and Country":
    countries_dict = generate_list_of_countries()
    if countries_dict["status"] == "success":
        countries_list = [i["country"] for i in countries_dict["data"]]
        countries_list.insert(0, "")

        country_selected = st.selectbox("Select a country", options=countries_list)
        if country_selected:
            states_dict = generate_list_of_states(country_selected)
            if states_dict["status"] == "success":
                states_list = [i["state"] for i in states_dict["data"]]
                states_list.insert(0, "")

                state_selected = st.selectbox("Select a state", options=states_list)
                if state_selected:
                    cities_dict = generate_list_of_cities(state_selected, country_selected)
                    if cities_dict["status"] == "success":
                        cities_list = [i["city"] for i in cities_dict["data"]]
                        cities_list.insert(0, "")

                        city_selected = st.selectbox("Select a city", options=cities_list)
                        if city_selected:
                            aqi_data_url = f"https://api.airvisual.com/v2/city?city={city_selected}&state={state_selected}&country={country_selected}&key={api_key}"
                            aqi_data_dict = requests.get(aqi_data_url).json()

                            if aqi_data_dict["status"] == "success":
                                # Display weather and air quality data
                                data = aqi_data_dict["data"]
                                st.subheader(f"Weather and Air Quality in {city_selected}, {state_selected}, {country_selected}")
                                st.write(f"**Temperature:** {data['current']['weather']['tp']} °C")
                                st.write(f"**Humidity:** {data['current']['weather']['hu']} %")
                                st.write(f"**Wind Speed:** {data['current']['weather']['ws']} m/s")
                                st.write(f"**Air Quality Index (AQI):** {data['current']['pollution']['aqius']}")

                                # Create a map for the location
                                map_creator(data["location"]["coordinates"][1], data["location"]["coordinates"][0])
                            else:
                                st.warning("No data available for this location.")
                    else:
                        st.warning("No cities available, please select another state.")
            else:
                st.warning("No states available, please select another country.")
    else:
        st.error("Too many requests. Wait for a few minutes before your next API call.")

# By Nearest City (IP Address)
elif category == "By Nearest City (IP Address)":
    url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
    aqi_data_dict = requests.get(url).json()

    if aqi_data_dict["status"] == "success":
        data = aqi_data_dict["data"]
        st.subheader(f"Weather and Air Quality in Your Nearest City: {data['city']}, {data['state']}, {data['country']}")
        st.write(f"**Temperature:** {data['current']['weather']['tp']} °C")
        st.write(f"**Humidity:** {data['current']['weather']['hu']} %")
        st.write(f"**Wind Speed:** {data['current']['weather']['ws']} m/s")
        st.write(f"**Air Quality Index (AQI):** {data['current']['pollution']['aqius']}")

        # Create a map for the location
        map_creator(data["location"]["coordinates"][1], data["location"]["coordinates"][0])
    else:
        st.warning("No data available for this location.")

# By Latitude and Longitude
elif category == "By Latitude and Longitude":
    latitude = st.text_input("Enter Latitude:")
    longitude = st.text_input("Enter Longitude:")

    if latitude and longitude:
        try:
            lat = float(latitude)
            lon = float(longitude)
            url = f"https://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={api_key}"
            aqi_data_dict = requests.get(url).json()

            if aqi_data_dict["status"] == "success":
                data = aqi_data_dict["data"]
                st.subheader(f"Weather and Air Quality for Coordinates: ({lat}, {lon})")
                st.write(f"**Temperature:** {data['current']['weather']['tp']} °C")
                st.write(f"**Humidity:** {data['current']['weather']['hu']} %")
                st.write(f"**Wind Speed:** {data['current']['weather']['ws']} m/s")
                st.write(f"**Air Quality Index (AQI):** {data['current']['pollution']['aqius']}")

                # Create a map for the location
                map_creator(data["location"]["coordinates"][1], data["location"]["coordinates"][0])
            else:
                st.warning("No data available for this location.")
        except ValueError:
            st.error("Please enter valid numeric values for latitude and longitude.")
