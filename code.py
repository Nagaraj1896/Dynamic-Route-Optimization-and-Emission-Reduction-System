import requests
from flask import Flask, request, jsonify, render_template
import folium
import math

# Initialize Flask app
app = Flask(__name__)
def get_traffic_data(source, destination):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{source}:{destination}/json"
    params = {"key": "YOUR_TOMTOM_API_KEY"}
    response = requests.get(url, params=params)
    return response.json()

def get_weather_data(location):
    url = f"https://api.waqi.info/feed/{location}/"
    params = {"token": "YOUR_AQICN_API_KEY"}
    response = requests.get(url, params=params)
    return response.json()

def get_route_data(source, destination):
    url = f"http://router.project-osrm.org/route/v1/driving/{source};{destination}"
    params = {"overview": "full", "geometries": "geojson"}
    response = requests.get(url, params=params)
    return response.json()
def calculate_emissions(distance, fuel_efficiency, emission_factor):
    return (distance / fuel_efficiency) * emission_factor

def score_route(travel_time, distance, emissions, safety_weight):
    alpha, beta, gamma, delta = 1.0, 1.0, 1.0, safety_weight
    return alpha * travel_time + beta * distance + gamma * emissions + delta * 0
def monitor_driver_fatigue(hours_driven, break_time):
    fatigue_flag = hours_driven > 8 and break_time < 30
    return "Fatigue Risk" if fatigue_flag else "Safe"

def assess_vehicle_health(fuel_level, tire_pressure, engine_status):
    if fuel_level < 25 or tire_pressure < 30 or not engine_status:
        return "Check Vehicle"
    return "Good Condition"
def generate_map(route_data, traffic_data, weather_data):
    map_center = [route_data['routes'][0]['legs'][0]['steps'][0]['maneuver']['location'][1], 
                  route_data['routes'][0]['legs'][0]['steps'][0]['maneuver']['location'][0]]
    route_map = folium.Map(location=map_center, zoom_start=13)

    coords = route_data['routes'][0]['geometry']['coordinates']
    folium.PolyLine([(lat, lng) for lng, lat in coords], color="blue", weight=2.5).add_to(route_map)

    folium.Marker(location=map_center, popup=f"Weather: {weather_data['data']['aqi']}").add_to(route_map)

    return route_map
@app.route('/')
def home():
    return render_template('index.html')  # Create an HTML form for inputs

@app.route('/optimize_route', methods=['POST'])
def optimize_route():
    source = request.form['source']
    destination = request.form['destination']
    fuel_efficiency = float(request.form['fuel_efficiency'])
    emission_factor = float(request.form['emission_factor'])

    traffic_data = get_traffic_data(source, destination)
    weather_data = get_weather_data(source)
    route_data = get_route_data(source, destination)

    distance = route_data['routes'][0]['distance'] / 1000  # Convert to km
    travel_time = route_data['routes'][0]['duration'] / 60  # Convert to minutes
    emissions = calculate_emissions(distance, fuel_efficiency, emission_factor)

    score = score_route(travel_time, distance, emissions, safety_weight=1.0)

    fatigue_status = monitor_driver_fatigue(hours_driven=5, break_time=20)
    vehicle_health = assess_vehicle_health(fuel_level=50, tire_pressure=35, engine_status=True)

    route_map = generate_map(route_data, traffic_data, weather_data)

    return jsonify({
        "travel_time": travel_time,
        "distance": distance,
        "emissions": emissions,
        "score": score,
        "fatigue_status": fatigue_status,
        "vehicle_health": vehicle_health,
        "map": route_map._repr_html_()
    })
if __name__ == '__main__':
    app.run(debug=True)
