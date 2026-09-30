import os

# RAPIDAPI CONFIGURATION

try:
    from api_config import RAPIDAPI_KEY
except ModuleNotFoundError:
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

RAPIDAPI_HOST = "google-map-places.p.rapidapi.com"


# API URLS

AUTOCOMPLETE_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/place/autocomplete/json"
)

QUERY_AUTOCOMPLETE_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/place/queryautocomplete/json"
)

ADDRESS_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/geocode/json"
)

DIRECTIONS_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/directions/json"
)

NEARBY_SEARCH_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/place/nearbysearch/json"
)

TEXT_SEARCH_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/place/textsearch/json"
)

PLACE_DETAILS_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/place/details/json"
)

FIND_PLACE_FROM_TEXT_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/place/findplacefromtext/json"
)

GET_PLACE_PHOTO_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/place/photo"
)

STREETVIEW_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/streetview"
)

TIMEZONE_URL = (
    "https://google-map-places.p.rapidapi.com/maps/api/timezone/json"
)
