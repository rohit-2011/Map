from flask import Flask, request, jsonify , render_template
import requests
import time
import math

from config import RAPIDAPI_KEY, RAPIDAPI_HOST

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/directions", methods=["GET"])
def directions():

    origin = request.args.get("origin")
    destination = request.args.get("destination")
    mode = request.args.get("mode", "driving")

    if not origin or not destination:
        return jsonify({
            "status": "error",
            "message": "Origin and destination are required"
        }), 400

    url = (
        "https://google-map-places.p.rapidapi.com/"
        "maps/api/directions/json"
    )

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }


    # =====================================================
    # NORMAL ROUTES
    # DRIVING / WALKING
    # =====================================================

    if mode != "transit":

        querystring = {
            "region": "en",
            "language": "en",
            "units": "metric",
            "mode": mode,
            "traffic_model": "best_guess",
            "departure_time": str(int(time.time())),
            "alternatives": "true",
            "origin": origin,
            "destination": destination
        }

        response = requests.get(
            url,
            headers=headers,
            params=querystring
        )

        return jsonify(
            response.json()
        )


    # =====================================================
    # TRANSIT
    # =====================================================

    transit_routes = []


    # =====================================================
    # FUNCTION TO REQUEST TRANSIT
    # =====================================================

    def get_transit_routes(transit_mode):

        querystring = {
            "region": "en",
            "language": "en",
            "units": "metric",
            "mode": "transit",
            "transit_mode": transit_mode,
            "transit_routing_preference": "less_walking",
            "departure_time": str(int(time.time())),
            "alternatives": "true",
            "origin": origin,
            "destination": destination
        }

        response = requests.get(
            url,
            headers=headers,
            params=querystring
        )

        data = response.json()

        if data.get("status") != "OK":
            return []

        return data.get(
            "routes",
            []
        )


    # =====================================================
    # BUS ROUTES
    # =====================================================

    bus_routes = get_transit_routes(
        "bus"
    )


    # =====================================================
    # TRAIN / RAIL ROUTES
    # =====================================================

    train_routes = get_transit_routes(
        "rail"
    )


    # =====================================================
    # COMBINE ROUTES
    # =====================================================

    all_routes = []

    all_routes.extend(
        bus_routes
    )

    all_routes.extend(
        train_routes
    )


    # =====================================================
    # NO ROUTE
    # =====================================================

    if not all_routes:

        return jsonify({
            "status": "ZERO_RESULTS",
            "message": "No transit route found."
        })


    # =====================================================
    # REMOVE DUPLICATE ROUTES
    # =====================================================

    seen_routes = set()

    unique_routes = []


    for route in all_routes:

        leg = route.get(
            "legs",
            [{}]
        )[0]


        steps = leg.get(
            "steps",
            []
        )


        route_signature = []


        for step in steps:

            if step.get(
                "travel_mode"
            ) == "TRANSIT":

                transit = step.get(
                                        "transit_details",
                                        {}
                                    )
                

                line = transit.get(
                                        "line",
                                        {}
                                    )
                

                vehicle = line.get(
                                        "vehicle",
                                        {}
                                    )
                

                route_signature.append(
                    (
                        vehicle.get(
                            "type"
                        ),

                        line.get(
                            "short_name"
                        ),

                        transit.get(
                            "departure_stop",
                            {}
                        ).get(
                            "name"
                        ),

                        transit.get(
                            "arrival_stop",
                            {}
                        ).get(
                            "name"
                        )
                    )
                )


        route_signature = str(
            route_signature
        )


        if route_signature in seen_routes:
            continue


        seen_routes.add(
            route_signature
        )

        unique_routes.append(
            route
        )


    # =====================================================
    # CLEAN ROUTES
    # =====================================================

    clean_routes = []


    for route_number, route in enumerate(
        unique_routes,
        1
    ):

        leg = route.get(
            "legs",
            [{}]
        )[0]


        clean_steps = []


        for step in leg.get(
            "steps",
            []
        ):

            travel_mode = step.get(
                                "travel_mode"
                            )
            
            

            # =================================================
            # WALKING
            # =================================================

            if travel_mode == "WALKING":

                clean_steps.append({

                    "travel_mode":
                        "WALKING",

                    "distance":
                        step.get(
                            "distance",
                            {}
                        ).get(
                            "text"
                        ),

                    "duration":
                        step.get(
                            "duration",
                            {}
                        ).get(
                            "text"
                        ),

                    "duration_seconds":
                        step.get(
                            "duration",
                            {}
                        ).get(
                            "value"
                        ),

                    "instruction":
                        step.get(
                            "html_instructions"
                        )
                })


            # =================================================
            # TRANSIT
            # =================================================

            elif travel_mode == "TRANSIT":

                transit = step.get(
                                        "transit_details",
                                        {}
                                    )
               


                line =  transit.get(
                                        "line",
                                        {}
                                    )
                
               

                vehicle = line.get(
                                        "vehicle",
                                        {}
                                    )
                


                departure_stop = transit.get(
                                        "departure_stop",
                                        {}
                                    )
                


                arrival_stop = transit.get(
                                        "arrival_stop",
                                        {}
                                    )
                
                

                departure_time = transit.get(
                                        "departure_time",
                                        {}
                                    )
               


                arrival_time =  transit.get(
                                        "arrival_time",
                                        {}
                                    )
              


                vehicle_type = vehicle.get(
                                        "type"
                                    )
               


                # =============================================
                # CATEGORY
                # =============================================

                if vehicle_type == "BUS":

                    category = "BUS"

                elif vehicle_type in [
                    "TRAIN",
                    "RAIL",
                    "HEAVY_RAIL"
                ]:

                    category = "TRAIN"

                elif vehicle_type in [
                    "SUBWAY"
                ]:

                    category = "SUBWAY"

                elif vehicle_type in [
                    "TRAM",
                    "LIGHT_RAIL"
                ]:

                    category = "TRAM"

                else:

                    category = (
                        vehicle.get(
                            "name"
                        )
                        or "TRANSIT"
                    )


                clean_steps.append({

                    "travel_mode":
                        "TRANSIT",

                    "category":
                        category,

                    "vehicle":
                        vehicle.get(
                            "name"
                        ),

                    "vehicle_type":
                        vehicle_type,

                    "number":
                        line.get(
                            "short_name"
                        ),

                    "headsign":
                        transit.get(
                            "headsign"
                        ),

                    "from":
                        departure_stop.get(
                            "name"
                        ),

                    "to":
                        arrival_stop.get(
                            "name"
                        ),

                    "stops":
                        transit.get(
                            "num_stops"
                        ),

                    "distance":
                        step.get(
                            "distance",
                            {}
                        ).get(
                            "text"
                        ),

                    "duration":
                        step.get(
                            "duration",
                            {}
                        ).get(
                            "text"
                        ),

                    "duration_seconds":
                        step.get(
                            "duration",
                            {}
                        ).get(
                            "value"
                        ),

                    "departure_time":
                        departure_time.get(
                            "text"
                        ),

                    "arrival_time":
                        arrival_time.get(
                            "text"
                        )
                })


        # =====================================================
        # ROUTE TOTAL
        # =====================================================

        total_distance = leg.get(
                        "distance",
                        {}
                    ).get(
                        "text"
                    )
        


        total_duration =leg.get("duration",{}).get("text")


        total_duration_seconds =leg.get(
                        "duration",
                        {}
                    ).get(
                        "value"
                    )
        


        # =====================================================
        # DETERMINE ROUTE TYPE
        # =====================================================

        route_types = []


        for step in clean_steps:

            if step.get(
                "travel_mode"
            ) == "TRANSIT":

                category = step.get(
                                        "category"
                                    )
               

                if category not in route_types:

                    route_types.append(
                        category
                    )


        if "TRAIN" in route_types:

            route_type = "TRAIN"

        elif "BUS" in route_types:

            route_type = "BUS"

        else:

            route_type = "TRANSIT"


        # =====================================================
        # SAVE CLEAN ROUTE
        # =====================================================

        clean_routes.append({

            "route_number":
                route_number,

            "type":
                route_type,

            "distance":
                total_distance,

            "duration":
                total_duration,

            "duration_seconds":
                total_duration_seconds,

            "steps":
                clean_steps
        })


    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return jsonify({

        "status":
            "success",

        "mode":
            "transit",

        "origin":
            origin,

        "destination":
            destination,

        "routes":
            clean_routes
    })

@app.route("/route-nearby", methods=["GET"])
def route_nearby():

    origin = request.args.get("origin")
    destination = request.args.get("destination")

    if not origin or not destination:
        return jsonify({
            "status": "error",
            "message": "Origin and destination are required"
        }), 400

    # =========================
    # 1. GET ROUTE
    # =========================

    directions_url = (
        "https://google-map-places.p.rapidapi.com/"
        "maps/api/directions/json"
    )

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    directions_params = {
        "region": "en",
        "language": "en",
        "units": "metric",
        "mode": "driving",
        "traffic_model": "best_guess",
        "departure_time": str(int(time.time())),
        "alternatives": "false",
        "origin": origin,
        "destination": destination
    }

    response = requests.get(
        directions_url,
        headers=headers,
        params=directions_params
    )

    data = response.json()

    if data.get("status") != "OK":
        return jsonify(data)

    route = data["routes"][0]
    leg = route["legs"][0]

    # =========================
    # 2. COLLECT ALL ROUTE POINTS
    # =========================

    route_points = []

    route_points.append(
        leg["start_location"]
    )

    for step in leg.get("steps", []):

        route_points.append(
            step["start_location"]
        )

        route_points.append(
            step["end_location"]
        )

    route_points.append(
        leg["end_location"]
    )

    # =========================
    # 3. SELECT ROUTE POINTS
    # =========================

    max_points = 8

    if len(route_points) > max_points:

        step_size = len(route_points) / max_points

        selected_points = []

        for i in range(max_points):

            index = int(i * step_size)

            selected_points.append(
                route_points[index]
            )

    else:

        selected_points = route_points

    # =========================
    # 4. NEARBY SEARCH
    # =========================

    nearby_url = (
        "https://google-map-places.p.rapidapi.com/"
        "maps/api/place/nearbysearch/json"
    )

    found_places = {}

    for search_point in selected_points:

        search_lat = search_point["lat"]
        search_lng = search_point["lng"]

        nearby_params = {
            "language": "en",
            "rankby": "prominence",
            "radius": "3000",
            "location": f"{search_lat},{search_lng}"
        }

        nearby_response = requests.get(
            nearby_url,
            headers=headers,
            params=nearby_params
        )

        nearby_data = nearby_response.json()

        if nearby_data.get("status") not in [
            "OK",
            "ZERO_RESULTS"
        ]:
            continue

        # =========================
        # 5. FILTER HOTELS / PETROL
        # =========================

        for place in nearby_data.get(
            "results",
            []
        ):

            place_id = place.get(
                "place_id"
            )

            if not place_id:
                continue

            types = place.get(
                "types",
                []
            )

            is_hotel = (
                "lodging" in types
            )

            is_petrol = (
                "gas_station" in types
            )

            if not (
                is_hotel
                or is_petrol
            ):
                continue

            # =========================
            # 6. PLACE LOCATION
            # =========================

            place_location = (
                place.get(
                    "geometry",
                    {}
                ).get(
                    "location",
                    {}
                )
            )

            place_lat = place_location.get(
                "lat"
            )

            place_lng = place_location.get(
                "lng"
            )

            if (
                place_lat is None
                or place_lng is None
            ):
                continue

            # =========================
            # 7. FIND NEAREST ROUTE POINT
            # =========================

            nearest_distance_km = None
            nearest_route_point = None

            for route_point_data in route_points:

                route_lat = route_point_data["lat"]
                route_lng = route_point_data["lng"]

                lat1 = math.radians(
                    route_lat
                )

                lon1 = math.radians(
                    route_lng
                )

                lat2 = math.radians(
                    place_lat
                )

                lon2 = math.radians(
                    place_lng
                )

                dlat = lat2 - lat1
                dlon = lon2 - lon1

                a = (
                    math.sin(dlat / 2) ** 2
                    +
                    math.cos(lat1)
                    * math.cos(lat2)
                    * math.sin(dlon / 2) ** 2
                )

                c = 2 * math.atan2(
                    math.sqrt(a),
                    math.sqrt(1 - a)
                )

                earth_radius_km = 6371

                distance_km = (
                    earth_radius_km * c
                )

                if (
                    nearest_distance_km is None
                    or distance_km < nearest_distance_km
                ):
                    nearest_distance_km = (
                        distance_km
                    )

                    nearest_route_point = {
                        "lat": route_lat,
                        "lng": route_lng
                    }

            # =========================
            # 8. ONLY WITHIN 1 KM
            # =========================

            if (
                nearest_distance_km is None
                or nearest_distance_km > 1
            ):
                continue

            # =========================
            # 9. CATEGORY
            # =========================

            if is_petrol:
                category = "PETROL PUMP"
            else:
                category = "HOTEL"

            # =========================
            # 10. SAVE PLACE
            # =========================

            found_places[place_id] = {

                "category": category,

                "name": place.get(
                    "name"
                ),

                "rating": place.get(
                    "rating"
                ),

                "address": place.get(
                    "vicinity"
                ),

                "location": place_location,

                "distance_from_route_km": round(
                    nearest_distance_km,
                    2
                ),

                "route_point": nearest_route_point
            }

    # =========================
    # 11. FINAL RESPONSE
    # =========================

    return jsonify({

        "status": "success",

        "origin": origin,

        "destination": destination,

        "route": {

            "distance":
                leg["distance"]["text"],

            "duration":
                leg["duration"]["text"]
        },

        "places":
            list(
                found_places.values()
            )
    })

@app.route("/autocomplete", methods=["GET"])
def autocomplete():

    user_input = request.args.get("input")

    if not user_input:
        return jsonify({
            "status": "error",
            "message": "Input is required"
        }), 400

    url = "https://google-map-places.p.rapidapi.com/maps/api/place/autocomplete/json"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    querystring = {
        "input": user_input,
        "language": "en"
    }

    response = requests.get(
        url,
        headers=headers,
        params=querystring
    )

    return jsonify(response.json())

@app.route("/geocoding", methods=["GET"])
def geocoding():

    address = request.args.get("address")

    if not address:
        return jsonify({
            "status": "error",
            "message": "Address is required"
        }), 400

    url = "https://google-map-places.p.rapidapi.com/maps/api/geocode/json"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    querystring = {
        "language": "en",
        "location_type": "APPROXIMATE",
        "address": address,
        "region": "en"
    }

    response = requests.get(
        url,
        headers=headers,
        params=querystring
    )

    return jsonify(response.json())

@app.route("/nearby", methods=["GET"])
def nearby():

    place = request.args.get("place")

    if not place:
        return jsonify({
            "status": "error",
            "message": "Place is required"
        }), 400

    # Step 1: Place ko coordinates me convert karna
    geocode_url = "https://google-map-places.p.rapidapi.com/maps/api/geocode/json"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    geocode_params = {
        "language": "en",
        "location_type": "APPROXIMATE",
        "address": place,
        "region": "en"
    }

    geocode_response = requests.get(
        geocode_url,
        headers=headers,
        params=geocode_params
    )

    geocode_data = geocode_response.json()

    if geocode_data.get("status") != "OK":
        return jsonify(geocode_data)

    location = geocode_data["results"][0]["geometry"]["location"]

    lat = location["lat"]
    lng = location["lng"]

    # Step 2: Nearby Search
    nearby_url = "https://google-map-places.p.rapidapi.com/maps/api/place/nearbysearch/json"

    nearby_params = {
        "opennow": "true",
        "language": "en",
        "rankby": "prominence",
        "radius": "1000",
        "location": f"{lat},{lng}"
    }

    nearby_response = requests.get(
        nearby_url,
        headers=headers,
        params=nearby_params
    )

    return jsonify(nearby_response.json())

@app.route("/place-details", methods=["GET"])
def place_details():

    place_id = request.args.get("place_id")

    print("PLACE DETAILS REQUEST RECEIVED")
    print("Place ID:", place_id)
    print("Calling RapidAPI...")

    if not place_id:
        return jsonify({
            "status": "error",
            "message": "Place ID is required"
        }), 400

    url = "https://google-map-places.p.rapidapi.com/maps/api/place/details/json"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    querystring = {
        "fields": "all",
        "region": "en",
        "language": "en",
        "reviews_no_translations": "true",
        "place_id": place_id
    }

    

    try:
        response = requests.get(
            url,
            headers=headers,
            params=querystring,
            timeout=15
        )

        print("RapidAPI Status:", response.status_code)
        print("RapidAPI Response received")

        return jsonify(response.json())

    except requests.exceptions.Timeout:
        print("RapidAPI request timed out")

        return jsonify({
            "status": "error",
            "message": "RapidAPI request timed out"
        }), 504

    except Exception as e:
        print("ERROR:", str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route("/photo", methods=["GET"])
def photo():

    place = request.args.get("place")

    if not place:
        return jsonify({
            "status": "error",
            "message": "Place is required"
        }), 400

    # -----------------------------
    # STEP 1: Find Place
    # -----------------------------

    place_url = "https://google-map-places.p.rapidapi.com/maps/api/place/findplacefromtext/json"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    place_params = {
        "fields": "all",
        "language": "en",
        "inputtype": "textquery",
        "input": place
    }

    place_response = requests.get(
        place_url,
        headers=headers,
        params=place_params
    )

    place_data = place_response.json()

    if place_data.get("status") != "OK":
        return jsonify(place_data)

    candidates = place_data.get("candidates", [])

    if not candidates:
        return jsonify({
            "status": "error",
            "message": "No place found"
        }), 404

    candidate = candidates[0]

    place_name = candidate.get("name")
    address = candidate.get("formatted_address")

    photos = candidate.get("photos", [])

    if not photos:
        return jsonify({
            "status": "error",
            "message": "No photos found",
            "place": place_name,
            "address": address
        }), 404

    photo_reference = photos[0].get("photo_reference")

    # -----------------------------
    # STEP 2: Photo API
    # -----------------------------

    photo_url = "https://google-map-places.p.rapidapi.com/maps/api/place/photo"

    photo_params = {
        "photo_reference": photo_reference
    }

    photo_response = requests.get(
        photo_url,
        headers=headers,
        params=photo_params
    )

    return jsonify({
        "status": "debug",
        "place": place_name,
        "address": address,
        "photo_reference_found": bool(photo_reference),
        "photo_api_status": photo_response.status_code,
        "photo_content_type": photo_response.headers.get("Content-Type"),
        "photo_size": len(photo_response.content)
    })

@app.route("/timezone", methods=["GET"])
def timezone():

    place = request.args.get("place")

    if not place:
        return jsonify({
            "status": "error",
            "message": "Place is required"
        }), 400

    # -----------------------------
    # STEP 1: Geocoding
    # -----------------------------

    geocode_url = "https://google-map-places.p.rapidapi.com/maps/api/geocode/json"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    geocode_params = {
        "language": "en",
        "location_type": "APPROXIMATE",
        "address": place,
        "region": "en"
    }

    geocode_response = requests.get(
        geocode_url,
        headers=headers,
        params=geocode_params
    )

    geocode_data = geocode_response.json()

    if geocode_data.get("status") != "OK":
        return jsonify({
            "status": "error",
            "message": "Place nahi mila",
            "details": geocode_data
        }), 404

    location = geocode_data["results"][0]["geometry"]["location"]

    lat = location["lat"]
    lng = location["lng"]

    # -----------------------------
    # STEP 2: Time Zone
    # -----------------------------

    timezone_url = "https://google-map-places.p.rapidapi.com/maps/api/timezone/json"

    timezone_params = {
        "language": "en",
        "location": f"{lat},{lng}",
        "timestamp": str(int(time.time()))
    }

    timezone_response = requests.get(
        timezone_url,
        headers=headers,
        params=timezone_params
    )

    return jsonify(timezone_response.json())

@app.route("/streetview", methods=["GET"])
def streetview():

    place = request.args.get("place")

    if not place:
        return jsonify({
            "status": "error",
            "message": "Place is required"
        }), 400

    url = "https://google-map-places.p.rapidapi.com/maps/api/streetview/metadata"

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    querystring = {
        "source": "default",
        "location": place,
        "return_error_code": "true"
    }

    response = requests.get(
        url,
        headers=headers,
        params=querystring
    )

    return jsonify(response.json())

@app.route("/place-search", methods=["GET"])
def place_search():

    place = request.args.get("place")

    if not place:
        return jsonify({
            "status": "error",
            "message": "Place is required"
        }), 400

    url = (
        "https://google-map-places.p.rapidapi.com/"
        "maps/api/place/findplacefromtext/json"
    )

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    querystring = {
        "fields": "all",
        "language": "en",
        "inputtype": "textquery",
        "input": place
    }

    response = requests.get(
        url,
        headers=headers,
        params=querystring
    )

    data = response.json()

    if data.get("status") != "OK":

        return jsonify({
            "status": "error",
            "message": "Place not found",
            "details": data
        }), 404

    candidates = data.get("candidates", [])

    if not candidates:

        return jsonify({
            "status": "error",
            "message": "No place found"
        }), 404

    candidate = candidates[0]

    location = (
        candidate
        .get("geometry", {})
        .get("location", {})
    )

    return jsonify({
        "status": "success",

        "place": {
            "name": candidate.get("name"),

            "address": candidate.get(
                "formatted_address"
            ),

            "rating": candidate.get(
                "rating"
            ),

            "place_id": candidate.get(
                "place_id"
            ),

            "location": location,

            "phone": candidate.get(
                "formatted_phone_number"
            ),

            "website": candidate.get(
                "website"
            ),

            "types": candidate.get(
                "types",
                []
            )
        }
    })

if __name__ == "__main__":
    app.run(debug=True)

    