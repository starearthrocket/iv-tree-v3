"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const countrySearch = document.getElementById("country-search");
    const countrySelect = document.getElementById("id_country");

    if (!countrySearch || !countrySelect) {
        return;
    }

    const ukAliases = [
        "uk",
        "u.k.",
        "united kingdom",
        "great britain",
        "britain",
        "england",
        "wales",
        "scotland",
        "northern ireland"
    ];

    const originalOptions = Array.from(countrySelect.options).map(
        (option) => ({
            value: option.value,
            text: option.text,
            disabled: option.disabled
        })
    );

    function restoreCountryOptions() {
        const selectedValue = countrySelect.value;

        countrySelect.innerHTML = "";

        originalOptions.forEach((optionData) => {
            const option = document.createElement("option");

            option.value = optionData.value;
            option.textContent = optionData.text;
            option.disabled = optionData.disabled;

            countrySelect.appendChild(option);
        });

        countrySelect.value = selectedValue;
    }

    function selectCountryCode(code) {
        restoreCountryOptions();

        const optionExists = Array.from(countrySelect.options).some(
            (option) => option.value === code
        );

        if (optionExists) {
            countrySelect.value = code;
        }

        countrySearch.value = "";
    }

    function getSelectedCountryName() {
        const selectedOption =
            countrySelect.options[countrySelect.selectedIndex];

        if (!selectedOption || !selectedOption.value) {
            return "";
        }

        return selectedOption.text;
    }

    window.selectReportCountry = selectCountryCode;
    window.getReportCountryName = getSelectedCountryName;

    function filterCountries() {
        const query = countrySearch.value.trim().toLowerCase();
        const selectedValue = countrySelect.value;

        countrySelect.innerHTML = "";

        originalOptions.forEach((optionData) => {
            const optionText = optionData.text.toLowerCase();

            const isPlaceholder =
                optionData.value === "" &&
                optionText.includes("select country");

            const isDivider =
                optionData.value === "" &&
                optionData.text.includes("---");

            const isUnitedKingdom = optionData.value === "GB";

            const matchesCountry = optionText.includes(query);

            const matchesUkAlias =
                isUnitedKingdom &&
                ukAliases.some((alias) => alias.includes(query));

            if (
                !query ||
                isPlaceholder ||
                isDivider ||
                matchesCountry ||
                matchesUkAlias
            ) {
                const option = document.createElement("option");

                option.value = optionData.value;
                option.textContent = optionData.text;
                option.disabled = optionData.disabled;

                countrySelect.appendChild(option);
            }
        });

        if (!query) {
            const previousSelectionExists =
                Array.from(countrySelect.options).some(
                    (option) => option.value === selectedValue
                );

            if (previousSelectionExists) {
                countrySelect.value = selectedValue;
            }

            return;
        }

        if (ukAliases.includes(query)) {
            countrySelect.value = "GB";
            return;
        }

        const exactCountry = originalOptions.find(
            (option) =>
                option.value &&
                option.text.toLowerCase() === query
        );

        if (exactCountry) {
            countrySelect.value = exactCountry.value;
            return;
        }

        const availableCountries = Array.from(
            countrySelect.options
        ).filter(
            (option) => option.value && !option.disabled
        );

        if (availableCountries.length === 1) {
            countrySelect.value = availableCountries[0].value;
        }
    }

    countrySearch.addEventListener("input", filterCountries);
});


async function initLocationPickerMap() {
    try {
        const [
            { Map },
            { AdvancedMarkerElement },
            { Geocoder }
        ] = await Promise.all([
            google.maps.importLibrary("maps"),
            google.maps.importLibrary("marker"),
            google.maps.importLibrary("geocoding")
        ]);

        const mapElement =
            document.getElementById("location-picker-map");

        if (!mapElement) {
            return;
        }

        const latitudeInput =
            document.getElementById("id_latitude");

        const longitudeInput =
            document.getElementById("id_longitude");

        const what3wordsInput =
            document.getElementById("id_what3words");

        const countrySelect =
            document.getElementById("id_country");

        const regionInput =
            document.getElementById("id_region");

        const townCityInput =
            document.getElementById("id_town_city");

        const statusElement =
            document.getElementById("map-location-status");

        const locationSummary =
            document.getElementById("location-summary");

        const locationDetails =
            document.getElementById("location-details");

        const currentLocationButton =
            document.getElementById("use-current-location");

        const manualWhat3wordsInput =
            document.getElementById("manual-what3words");

        const what3wordsButton =
            document.getElementById("use-what3words");

        const what3wordsStatus =
            document.getElementById("what3words-status");

        const csrfTokenElement =
            document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );

        if (
            !latitudeInput ||
            !longitudeInput ||
            !what3wordsInput ||
            !countrySelect ||
            !regionInput ||
            !townCityInput ||
            !statusElement ||
            !locationSummary ||
            !currentLocationButton ||
            !manualWhat3wordsInput ||
            !what3wordsButton ||
            !what3wordsStatus ||
            !csrfTokenElement
        ) {
            return;
        }

        const csrfToken = csrfTokenElement.value;

        const mapId = mapElement.dataset.mapId;

        const what3wordsUrl =
            mapElement.dataset.what3wordsUrl;

        const geocoder = new Geocoder();

        const existingLatitude =
            parseFloat(latitudeInput.value);

        const existingLongitude =
            parseFloat(longitudeInput.value);

        const hasExistingLocation =
            !Number.isNaN(existingLatitude) &&
            !Number.isNaN(existingLongitude);

        const initialPosition = hasExistingLocation
            ? {
                lat: existingLatitude,
                lng: existingLongitude
            }
            : {
                lat: 54.5,
                lng: -3.0
            };

        const map = new Map(
            mapElement,
            {
                center: initialPosition,
                zoom: hasExistingLocation ? 15 : 5,
                mapId: mapId,
                mapTypeControl: false,
                streetViewControl: false,
                clickableIcons: false
            }
        );

        let locationMarker = null;

        function getAddressComponent(result, type) {
            const component =
                result.address_components.find(
                    (item) => item.types.includes(type)
                );

            return component || null;
        }

        function getLocationSummaryText() {
            const parts = [];

            if (
                townCityInput &&
                townCityInput.value.trim()
            ) {
                parts.push(townCityInput.value.trim());
            }

            if (
                regionInput &&
                regionInput.value.trim()
            ) {
                parts.push(regionInput.value.trim());
            }

            if (window.getReportCountryName) {
                const countryName =
                    window.getReportCountryName();

                if (countryName) {
                    parts.push(countryName);
                }
            }

            return parts.join(", ");
        }

        function refreshLocationSummary() {
            const summary = getLocationSummaryText();

            if (summary) {
                locationSummary.textContent =
                    `✓ Location found: ${summary}`;
            } else {
                locationSummary.textContent = "";
            }
        }

        function setTreeLocation(
            position,
            statusMessage,
            zoomLevel = null
        ) {
            latitudeInput.value =
                Number(position.lat).toFixed(6);

            longitudeInput.value =
                Number(position.lng).toFixed(6);

            if (locationMarker) {
                locationMarker.position = position;
            } else {
                locationMarker =
                    new AdvancedMarkerElement({
                        map: map,
                        position: position,
                        title: "Selected tree location"
                    });
            }

            map.setCenter(position);

            if (zoomLevel) {
                map.setZoom(zoomLevel);
            }

            statusElement.textContent = statusMessage;
        }

        async function reverseGeocodeLocation(position) {
            try {
                const response = await geocoder.geocode({
                    location: position
                });

                if (
                    !response.results ||
                    !response.results.length
                ) {
                    throw new Error(
                        "No location details found."
                    );
                }

                const result = response.results[0];

                const country =
                    getAddressComponent(
                        result,
                        "country"
                    );

                const regionLevelTwo =
                    getAddressComponent(
                        result,
                        "administrative_area_level_2"
                    );

                const regionLevelOne =
                    getAddressComponent(
                        result,
                        "administrative_area_level_1"
                    );

                const postalTown =
                    getAddressComponent(
                        result,
                        "postal_town"
                    );

                const locality =
                    getAddressComponent(
                        result,
                        "locality"
                    );

                const sublocality =
                    getAddressComponent(
                        result,
                        "sublocality"
                    );

                const town =
                    postalTown ||
                    locality ||
                    sublocality;

                const region =
                    regionLevelTwo ||
                    regionLevelOne;

                if (
                    country &&
                    window.selectReportCountry
                ) {
                    window.selectReportCountry(
                        country.short_name
                    );
                }

                if (regionInput && region) {
                    regionInput.value =
                        region.long_name;
                }

                if (townCityInput && town) {
                    townCityInput.value =
                        town.long_name;
                }

                refreshLocationSummary();

                return true;

            } catch (error) {
                console.error(
                    "Reverse geocoding failed:",
                    error
                );

                locationSummary.textContent =
                    "The precise location was selected, " +
                    "but the place name could not be " +
                    "filled automatically.";

                if (locationDetails) {
                    locationDetails.open = true;
                }

                return false;
            }
        }

        async function selectLocation(
            position,
            statusMessage,
            zoomLevel
        ) {
            setTreeLocation(
                position,
                statusMessage,
                zoomLevel
            );

            await reverseGeocodeLocation(position);
        }

        if (hasExistingLocation) {
            setTreeLocation(
                initialPosition,
                "✓ Tree location selected. " +
                    "Click the map to adjust it if needed.",
                15
            );

            if (what3wordsInput.value) {
                manualWhat3wordsInput.value =
                    what3wordsInput.value;
            }

            refreshLocationSummary();
        }

        map.addListener(
            "click",
            async (event) => {
                const position = {
                    lat: event.latLng.lat(),
                    lng: event.latLng.lng()
                };

                what3wordsInput.value = "";
                manualWhat3wordsInput.value = "";
                what3wordsStatus.textContent = "";

                await selectLocation(
                    position,
                    "✓ Tree location selected. " +
                        "A what3words address will be " +
                        "generated when you save the report.",
                    null
                );
            }
        );

        currentLocationButton.addEventListener(
            "click",
            () => {
                if (!navigator.geolocation) {
                    statusElement.textContent =
                        "Your browser does not support " +
                        "location services. Please use " +
                        "the map instead.";

                    return;
                }

                currentLocationButton.disabled = true;

                currentLocationButton.textContent =
                    "Finding your location...";

                statusElement.textContent =
                    "Requesting your current location...";

                navigator.geolocation.getCurrentPosition(
                    async (position) => {
                        const currentPosition = {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude
                        };

                        what3wordsInput.value = "";
                        manualWhat3wordsInput.value = "";
                        what3wordsStatus.textContent = "";

                        await selectLocation(
                            currentPosition,
                            "✓ Current location selected. " +
                                "Adjust the marker if the " +
                                "tree is nearby.",
                            17
                        );

                        currentLocationButton.disabled =
                            false;

                        currentLocationButton.textContent =
                            "Use my current location";
                    },

                    (error) => {
                        let message =
                            "Your current location could " +
                            "not be used. Please use the " +
                            "map instead.";

                        if (
                            error.code ===
                            error.PERMISSION_DENIED
                        ) {
                            message =
                                "Location permission was " +
                                "denied. Please use the map.";
                        }

                        if (
                            error.code ===
                            error.POSITION_UNAVAILABLE
                        ) {
                            message =
                                "Your current location is " +
                                "unavailable. Please use " +
                                "the map.";
                        }

                        if (
                            error.code === error.TIMEOUT
                        ) {
                            message =
                                "Finding your location took " +
                                "too long. Please try again " +
                                "or use the map.";
                        }

                        statusElement.textContent = message;

                        currentLocationButton.disabled =
                            false;

                        currentLocationButton.textContent =
                            "Use my current location";
                    },

                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            }
        );

        what3wordsButton.addEventListener(
            "click",
            async () => {
                const address =
                    manualWhat3wordsInput.value.trim();

                if (!address) {
                    what3wordsStatus.textContent =
                        "Enter a what3words address first.";

                    return;
                }

                what3wordsButton.disabled = true;

                what3wordsButton.textContent =
                    "Finding address...";

                what3wordsStatus.textContent =
                    "Checking the what3words address...";

                const formData = new FormData();

                formData.append(
                    "what3words",
                    address
                );

                try {
                    const response = await fetch(
                        what3wordsUrl,
                        {
                            method: "POST",
                            headers: {
                                "X-CSRFToken": csrfToken
                            },
                            body: formData
                        }
                    );

                    const data = await response.json();

                    if (
                        !response.ok ||
                        !data.success
                    ) {
                        what3wordsStatus.textContent =
                            data.message ||
                            "That address could not be found.";

                        return;
                    }

                    const position = {
                        lat: Number(data.latitude),
                        lng: Number(data.longitude)
                    };

                    what3wordsInput.value =
                        data.what3words;

                    manualWhat3wordsInput.value =
                        data.what3words;

                    setTreeLocation(
                        position,
                        "✓ what3words location selected.",
                        18
                    );

                    const geocoded =
                        await reverseGeocodeLocation(
                            position
                        );

                    if (
                        !geocoded &&
                        data.country &&
                        window.selectReportCountry
                    ) {
                        window.selectReportCountry(
                            data.country
                        );
                    }

                    if (
                        !geocoded &&
                        data.nearest_place &&
                        townCityInput &&
                        !townCityInput.value.trim()
                    ) {
                        townCityInput.value =
                            data.nearest_place;
                    }

                    refreshLocationSummary();

                    what3wordsStatus.textContent =
                        `✓ ${data.what3words} ` +
                        "found successfully.";

                } catch (error) {
                    console.error(
                        "what3words lookup failed:",
                        error
                    );

                    what3wordsStatus.textContent =
                        "The what3words service could not " +
                        "be reached. Please try again or " +
                        "use the map.";

                } finally {
                    what3wordsButton.disabled = false;

                    what3wordsButton.textContent =
                        "Use this address";
                }
            }
        );

        countrySelect.addEventListener(
            "change",
            refreshLocationSummary
        );

        regionInput.addEventListener(
            "input",
            refreshLocationSummary
        );

        townCityInput.addEventListener(
            "input",
            refreshLocationSummary
        );

    } catch (error) {
        console.error(
            "I-V Tree location map failed to load:",
            error
        );

        const statusElement =
            document.getElementById(
                "map-location-status"
            );

        if (statusElement) {
            statusElement.textContent =
                "The map could not be loaded. " +
                "Please try again later.";
        }
    }
}

window.initLocationPickerMap = initLocationPickerMap;