// =========================
// DOM ELEMENTS
// =========================

const originInput = document.getElementById("origin");
const destinationInput = document.getElementById("destination");

const originSuggestions =
    document.getElementById("originSuggestions");

const destinationSuggestions =
    document.getElementById("destinationSuggestions");

const searchBtn =
    document.getElementById("searchBtn");

const modeButtons =
    document.querySelectorAll(".mode-btn");

const distanceElement =
    document.getElementById("distance");

const durationElement =
    document.getElementById("duration");

const placesList =
    document.getElementById("placesList");


// =========================
// PLACE SEARCH ELEMENTS
// =========================

const placeSearchInput =
    document.getElementById("placeSearchInput");

const placeSearchBtn =
    document.getElementById("placeSearchBtn");

const placeSuggestions =
    document.getElementById("placeSuggestions");

const placeSearchResult =
    document.getElementById("placeSearchResult");


// =========================
// VARIABLES
// =========================

let selectedMode = "driving";

let map = null;

let routeLine = null;

let placeMarker = null;


// =========================
// INITIALIZE MAP
// =========================

function initializeMap() {

    map = L.map("map").setView(
        [26.9124, 75.7873],
        10
    );

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,
            attribution:
                "&copy; OpenStreetMap contributors"
        }
    ).addTo(map);
}


// =========================
// HIDE SUGGESTIONS
// =========================

function hideSuggestions(box) {

    box.innerHTML = "";

    box.style.display = "none";
}


// =========================
// SHOW AUTOCOMPLETE
// =========================

async function loadSuggestions(
    inputElement,
    suggestionsBox
) {

    const value =
        inputElement.value.trim();

    if (value.length < 2) {

        hideSuggestions(
            suggestionsBox
        );

        return;
    }

    try {

        const url =
            `/autocomplete?input=${encodeURIComponent(value)}`;

        const response =
            await fetch(url);

        const data =
            await response.json();

        const predictions =
            data.predictions || [];

        suggestionsBox.innerHTML = "";

        if (predictions.length === 0) {

            hideSuggestions(
                suggestionsBox
            );

            return;
        }

        predictions.forEach(
            function (prediction) {

                const item =
                    document.createElement("div");

                item.className =
                    "suggestion-item";

                item.textContent =
                    prediction.description;

                item.addEventListener(
                    "click",
                    function () {

                        inputElement.value =
                            prediction.description;

                        hideSuggestions(
                            suggestionsBox
                        );
                    }
                );

                suggestionsBox.appendChild(
                    item
                );
            }
        );

        suggestionsBox.style.display =
            "block";

    } catch (error) {

        console.error(
            "Autocomplete error:",
            error
        );

        hideSuggestions(
            suggestionsBox
        );
    }
}


// =========================
// FROM AUTOCOMPLETE
// =========================

originInput.addEventListener(
    "input",
    function () {

        loadSuggestions(
            originInput,
            originSuggestions
        );
    }
);


// =========================
// TO AUTOCOMPLETE
// =========================

destinationInput.addEventListener(
    "input",
    function () {

        loadSuggestions(
            destinationInput,
            destinationSuggestions
        );
    }
);


// =========================
// PLACE AUTOCOMPLETE
// =========================

placeSearchInput.addEventListener(
    "input",
    function () {

        loadSuggestions(
            placeSearchInput,
            placeSuggestions
        );
    }
);


// =========================
// DRAW ROUTE
// =========================

function drawRoute(route) {

    if (!route) {
        return;
    }

    if (
        !route.overview_polyline ||
        !route.overview_polyline.points
    ) {
        return;
    }

    const points =
        decodePolyline(
            route.overview_polyline.points
        );

    if (points.length === 0) {
        return;
    }

    if (routeLine) {

        map.removeLayer(
            routeLine
        );
    }

    routeLine =
        L.polyline(
            points,
            {
                weight: 5
            }
        ).addTo(map);

    map.fitBounds(
        routeLine.getBounds(),
        {
            padding: [30, 30]
        }
    );
}


// =========================
// POLYLINE DECODER
// =========================

function decodePolyline(encoded) {

    let points = [];

    let index = 0;

    let lat = 0;

    let lng = 0;

    while (
        index < encoded.length
    ) {

        let shift = 0;

        let result = 0;

        let byte;

        do {

            byte =
                encoded.charCodeAt(
                    index++
                ) - 63;

            result |=
                (byte & 0x1f) <<
                shift;

            shift += 5;

        } while (
            byte >= 0x20
        );

        let deltaLat =
            (
                result & 1
            )
                ? ~(result >> 1)
                : result >> 1;

        lat += deltaLat;


        shift = 0;

        result = 0;


        do {

            byte =
                encoded.charCodeAt(
                    index++
                ) - 63;

            result |=
                (byte & 0x1f) <<
                shift;

            shift += 5;

        } while (
            byte >= 0x20
        );


        let deltaLng =
            (
                result & 1
            )
                ? ~(result >> 1)
                : result >> 1;

        lng += deltaLng;


        points.push([
            lat / 100000,
            lng / 100000
        ]);
    }

    return points;
}


// =========================
// SEARCH ROUTE
// =========================

async function searchRoute() {

    const origin =
        originInput.value.trim();

    const destination =
        destinationInput.value.trim();


    if (
        !origin ||
        !destination
    ) {

        alert(
            "From aur To dono enter karo."
        );

        return;
    }


    try {

        searchBtn.disabled = true;

        searchBtn.textContent =
            "Searching...";


        const url =
            `/directions?origin=${encodeURIComponent(origin)}` +
            `&destination=${encodeURIComponent(destination)}` +
            `&mode=${encodeURIComponent(selectedMode)}`;


        const response =
            await fetch(url);


        const data =
            await response.json();


        if (
            data.status !== "OK" &&
            data.status !== "success"
        ) {

            alert(
                data.error_message ||
                data.message ||
                "Route nahi mila."
            );

            return;
        }


        const routes =
            data.routes || [];


        if (
            routes.length === 0
        ) {

            alert(
                "Koi route nahi mila."
            );

            return;
        }


        // =====================================================
        // TRANSIT
        // =====================================================

        if (
            selectedMode === "transit"
        ) {

            // First route ka total distance/time
            const firstRoute =
                routes[0];


            distanceElement.textContent =
                firstRoute.distance || "—";


            durationElement.textContent =
                firstRoute.duration || "—";


            // Saare transit routes show karo
            showTransitDetails(
                routes
            );


            // Transit backend clean route bhejta hai,
            // isliye normal drawRoute() yahan nahi chalega.

            return;
        }


        // =====================================================
        // DRIVING / WALKING
        // =====================================================

        const route =
            routes[0];


        const leg =
            route.legs &&
            route.legs[0];


        if (!leg) {

            alert(
                "Route information nahi mili."
            );

            return;
        }


        distanceElement.textContent =
            leg.distance?.text || "—";


        durationElement.textContent =
            leg.duration?.text || "—";


        drawRoute(
            route
        );


        // =====================================================
        // DRIVING NEARBY PLACES
        // =====================================================

        if (
            selectedMode === "driving"
        ) {

            await loadNearbyPlaces(
                origin,
                destination
            );

        } else {

            placesList.innerHTML =
                `
                <p class="empty-message">
                    Hotels and petrol pumps are shown along the driving route.
                </p>
                `;
        }


    } catch (error) {

        console.error(
            "Route error:",
            error
        );

        alert(
            "Route search me error aaya."
        );

    } finally {

        searchBtn.disabled =
            false;

        searchBtn.textContent =
            "Search Route";
    }
}


// =========================
// SEARCH BUTTON
// =========================

searchBtn.addEventListener(
    "click",
    searchRoute
);


// =========================
// MODE BUTTONS
// =========================

modeButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                modeButtons.forEach(
                    function (btn) {

                        btn.classList.remove(
                            "active"
                        );
                    }
                );


                button.classList.add(
                    "active"
                );


                selectedMode =
                    button.dataset.mode;


                const origin =
                    originInput.value.trim();

                const destination =
                    destinationInput.value.trim();


                if (
                    origin &&
                    destination
                ) {

                    searchRoute();
                }
            }
        );
    }
);


// =========================
// ROUTE NEARBY
// =========================

async function loadNearbyPlaces(
    origin,
    destination
) {

    try {

        const url =
            `/route-nearby?origin=${encodeURIComponent(origin)}` +
            `&destination=${encodeURIComponent(destination)}`;


        const response =
            await fetch(url);


        const data =
            await response.json();


        if (
            data.status !== "success"
        ) {

            placesList.innerHTML =
                `
                <p class="empty-message">
                    Nearby places nahi mile.
                </p>
                `;

            return;
        }


        renderPlaces(
            data.places || []
        );


    } catch (error) {

        console.error(
            "Nearby places error:",
            error
        );


        placesList.innerHTML =
            `
            <p class="empty-message">
                Nearby places load nahi ho paaye.
            </p>
            `;
    }
}


// =========================
// RENDER PLACES
// =========================

function renderPlaces(
    places
) {

    if (
        places.length === 0
    ) {

        placesList.innerHTML =
            `
            <p class="empty-message">
                Koi hotel ya petrol pump nahi mila.
            </p>
            `;

        return;
    }


    placesList.innerHTML = "";


    places.forEach(
        function (place) {

            const card =
                document.createElement("div");

            card.className =
                "place-card";


            const category =
                document.createElement("div");

            category.className =
                "place-category";

            category.textContent =
                place.category || "PLACE";


            const name =
                document.createElement("div");

            name.className =
                "place-name";

            name.textContent =
                place.name || "Unknown";


            const address =
                document.createElement("div");

            address.className =
                "place-address";

            address.textContent =
                place.address || "Address unavailable";


            const distance =
                document.createElement("div");

            distance.className =
                "place-distance";

            if (
                place.distance_from_route_km !==
                undefined
            ) {

                distance.textContent =
                    `Distance from route: ${
                        place.distance_from_route_km
                    } km`;

            } else {

                distance.textContent =
                    "";
            }


            card.appendChild(
                category
            );

            card.appendChild(
                name
            );

            card.appendChild(
                address
            );

            card.appendChild(
                distance
            );


            placesList.appendChild(
                card
            );
        }
    );
}


// =========================
// GET TRANSIT DETAILS
// =========================

function getTransitIcon(
    type
) {

    const value =
        String(type || "")
            .toUpperCase();


    if (
        value === "BUS"
    ) {

        return "🚌";
    }


    if (
        value === "TRAIN" ||
        value === "RAIL" ||
        value === "HEAVY_RAIL"
    ) {

        return "🚆";
    }


    if (
        value === "SUBWAY"
    ) {

        return "🚇";
    }


    if (
        value === "TRAM" ||
        value === "LIGHT_RAIL"
    ) {

        return "🚊";
    }


    return "🚍";
}

// =========================
// TRANSIT DETAILS
// =========================

function showTransitDetails(
    routes
) {

    if (
        !routes ||
        routes.length === 0
    ) {

        placesList.innerHTML =
            `
            <p class="empty-message">
                Koi transit route nahi mila.
            </p>
            `;

        return;
    }


    let html =
        `
        <div class="transit-details">

            <h3>Transit Routes</h3>
        `;


    routes.forEach(
        function (route, routeIndex) {

            const routeType =
                route.type || "TRANSIT";

            const routeDistance =
                route.distance || "—";

            const routeDuration =
                route.duration || "—";


            // =================================================
            // ROUTE CARD
            // =================================================

            html +=
                `
                <div class="transit-route-card">

                    <div class="transit-route-header">

                        <strong>
                            Route ${routeIndex + 1}
                        </strong>

                        <span>
                            ${getTransitIcon(routeType)}
                            ${routeType}
                        </span>

                    </div>


                    <div class="transit-route-summary">

                        <span>
                            📍 ${routeDistance}
                        </span>

                        <span>
                            ⏱️ ${routeDuration}
                        </span>

                    </div>
                `;


            // =================================================
            // STEPS
            // =================================================

            const steps =
                route.steps || [];


            if (
                steps.length === 0
            ) {

                html +=
                    `
                    <div class="transit-step">
                        Transit details available nahi hain.
                    </div>
                    `;

            } else {

                steps.forEach(
                    function (step, stepIndex) {


                        // =====================================
                        // WALKING
                        // =====================================

                        if (
                            step.travel_mode ===
                            "WALKING"
                        ) {

                            html +=
                                `
                                <div class="transit-step">

                                    <div>
                                        🚶 <strong>Walking</strong>
                                    </div>

                                    <div>
                                        ${step.distance || "—"}
                                        ·
                                        ${step.duration || "—"}
                                    </div>

                                </div>
                                `;

                            return;
                        }


                        // =====================================
                        // TRANSIT
                        // =====================================

                        if (
                            step.travel_mode ===
                            "TRANSIT"
                        ) {

                            const category =
                                step.category ||
                                "TRANSIT";


                            const vehicle =
                                step.vehicle ||
                                category;


                            const number =
                                step.number;


                            const headsign =
                                step.headsign;


                            const from =
                                step.from ||
                                "Unknown stop";


                            const to =
                                step.to ||
                                "Unknown stop";


                            const stops =
                                step.stops;


                            const distance =
                                step.distance ||
                                "—";


                            const duration =
                                step.duration ||
                                "—";


                            const departureTime =
                                step.departure_time;


                            const arrivalTime =
                                step.arrival_time;


                            html +=
                                `
                                <div class="transit-step">

                                    <div>
                                        ${getTransitIcon(category)}

                                        <strong>
                                            ${category}
                                        </strong>
                                    </div>


                                    <div>
                                        ${vehicle}
                                        ${
                                            number
                                                ? ` · ${number}`
                                                : ""
                                        }
                                    </div>


                                    ${
                                        headsign
                                            ? `
                                            <div>
                                                Direction:
                                                ${headsign}
                                            </div>
                                            `
                                            : ""
                                    }


                                    <div>
                                        ${from}
                                        →
                                        ${to}
                                    </div>


                                    ${
                                        stops !== null &&
                                        stops !== undefined
                                            ? `
                                            <div>
                                                Stops:
                                                ${stops}
                                            </div>
                                            `
                                            : ""
                                    }


                                    <div>
                                        ${distance}
                                        ·
                                        ${duration}
                                    </div>


                                    ${
                                        departureTime ||
                                        arrivalTime
                                            ? `
                                            <div>
                                                ${
                                                    departureTime
                                                        ? `Departure: ${departureTime}`
                                                        : ""
                                                }

                                                ${
                                                    arrivalTime
                                                        ? ` · Arrival: ${arrivalTime}`
                                                        : ""
                                                }
                                            </div>
                                            `
                                            : ""
                                    }

                                </div>
                                `;
                        }

                    }
                );
            }


            html +=
                `
                </div>
                `;
        }
    );


    html +=
        `
        </div>
        `;


    placesList.innerHTML =
        html;
}


// =========================
// DIRECT PLACE SEARCH
// =========================

async function searchPlace() {

    const place =
        placeSearchInput.value.trim();


    if (!place) {

        alert(
            "Place ka naam enter karo."
        );

        return;
    }


    try {

        placeSearchBtn.disabled =
            true;

        placeSearchBtn.textContent =
            "Searching...";


        const url =
            `/place-search?place=${encodeURIComponent(place)}`;


        const response =
            await fetch(url);


        const data =
            await response.json();


        if (
            data.status !== "success"
        ) {

            placeSearchResult.innerHTML =
                `
                <p class="empty-message">
                    ${
                        data.message ||
                        "Place nahi mila."
                    }
                </p>
                `;

            return;
        }


        const result =
            data.place;


        const location =
            result.location || {};


        // Map par place show karo

        if (
            location.lat !== undefined &&
            location.lng !== undefined
        ) {

            if (placeMarker) {

                map.removeLayer(
                    placeMarker
                );
            }


            placeMarker =
                L.marker([
                    location.lat,
                    location.lng
                ])
                .addTo(map);


            placeMarker.bindPopup(
                `<b>${escapeHtml(
                    result.name || place
                )}</b>`
            ).openPopup();


            map.setView(
                [
                    location.lat,
                    location.lng
                ],
                15
            );
        }


        // Place details

        placeSearchResult.innerHTML =
            `
            <div class="place-result-card">

                <h3>
                    ${escapeHtml(
                        result.name || "Place"
                    )}
                </h3>

                <p>
                    <strong>Address:</strong>
                    ${escapeHtml(
                        result.address || "Not available"
                    )}
                </p>

                ${
                    result.rating
                    ? `
                    <p>
                        <strong>Rating:</strong>
                        ⭐ ${result.rating}
                    </p>
                    `
                    : ""
                }

                ${
                    location.lat !== undefined
                    ? `
                    <p>
                        <strong>Location:</strong>
                        ${location.lat},
                        ${location.lng}
                    </p>
                    `
                    : ""
                }

                ${
                    result.place_id
                    ? `
                    <p>
                        <strong>Place ID:</strong>
                        ${escapeHtml(
                            result.place_id
                        )}
                    </p>
                    `
                    : ""
                }

            </div>
            `;


    } catch (error) {

        console.error(
            "Place search error:",
            error
        );


        placeSearchResult.innerHTML =
            `
            <p class="empty-message">
                Place search me error aaya.
            </p>
            `;

    } finally {

        placeSearchBtn.disabled =
            false;

        placeSearchBtn.textContent =
            "Search";
    }
}


// =========================
// PLACE SEARCH BUTTON
// =========================

placeSearchBtn.addEventListener(
    "click",
    searchPlace
);


// =========================
// PLACE SEARCH ENTER KEY
// =========================

placeSearchInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter"
        ) {

            searchPlace();
        }
    }
);


// =========================
// ESCAPE HTML
// =========================

function escapeHtml(
    value
) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


// =========================
// CLICK OUTSIDE
// =========================

document.addEventListener(
    "click",
    function (event) {

        if (
            !originInput.contains(event.target) &&
            !originSuggestions.contains(event.target)
        ) {

            hideSuggestions(
                originSuggestions
            );
        }


        if (
            !destinationInput.contains(event.target) &&
            !destinationSuggestions.contains(event.target)
        ) {

            hideSuggestions(
                destinationSuggestions
            );
        }


        if (
            !placeSearchInput.contains(event.target) &&
            !placeSuggestions.contains(event.target)
        ) {

            hideSuggestions(
                placeSuggestions
            );
        }
    }
);


// =========================
// ENTER KEY - ROUTE
// =========================

originInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter"
        ) {

            searchRoute();
        }
    }
);


destinationInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter"
        ) {

            searchRoute();
        }
    }
);


// =========================
// START MAP
// =========================

initializeMap();