/* jshint esversion: 8, esnext: false */
/* global google */

async function initDetailReportMap() {
    const mapElement = document.getElementById("detail-report-map");

    if (!mapElement) {
        return;
    }

    try {
        const latitude = parseFloat(mapElement.dataset.latitude);
        const longitude = parseFloat(mapElement.dataset.longitude);
        const mapId = mapElement.dataset.mapId;

        if (Number.isNaN(latitude) || Number.isNaN(longitude)) {
            throw new Error("Report coordinates are unavailable.");
        }

        const { Map: GoogleMap } =
            await google.maps.importLibrary("maps");

        const { AdvancedMarkerElement } =
            await google.maps.importLibrary("marker");

        const position = {
            lat: latitude,
            lng: longitude
        };

        const map = new GoogleMap(mapElement, {
            center: position,
            zoom: 16,
            mapId: mapId,
            mapTypeControl: false,
            streetViewControl: false,
            clickableIcons: false
        });

        const markerUrlElement =
            document.getElementById("detail-marker-url");

        const markerImage = document.createElement("img");
        let markerUrl = "";

        if (markerUrlElement) {
            markerUrl = markerUrlElement.dataset.markerUrl;
        }

        markerImage.src = markerUrl;
        markerImage.alt = "";
        markerImage.style.width = "42px";
        markerImage.style.height = "52px";
        markerImage.style.objectFit = "contain";
        markerImage.style.display = "block";

        const reportMarker = new AdvancedMarkerElement({
            map: map,
            position: position,
            title: mapElement.dataset.title,
            content: markerImage
        });

        return reportMarker;
    } catch (error) {
        console.error(
            "I-V Tree detail map failed to load:",
            error
        );

        mapElement.innerHTML = "";

        const message = document.createElement("div");
        message.className = "map-placeholder-content";

        const heading = document.createElement("p");
        heading.className = "section-eyebrow";
        heading.textContent = "Map unavailable";

        const description = document.createElement("p");
        description.textContent =
            "The report is still available, " +
            "but its map could not be loaded.";

        message.appendChild(heading);
        message.appendChild(description);
        mapElement.appendChild(message);
    }

    return null;
}

window.initDetailReportMap = initDetailReportMap;