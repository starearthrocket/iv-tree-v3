/* jshint esversion: 8, esnext: false */
/* global google */

async function initHomeMap() {
    const mapElement =
        document.getElementById("home-report-map");

    if (!mapElement) {
        return;
    }

    try {
        const { Map: GoogleMap } =
            await google.maps.importLibrary("maps");

        const { AdvancedMarkerElement } =
            await google.maps.importLibrary("marker");

        const cards =
            document.querySelectorAll(".home-report-card");

        const markerUrls = {
            ACTIVE: mapElement.dataset.markerActive,
            IN_PROGRESS: mapElement.dataset.markerProgress,
            PROTECTED: mapElement.dataset.markerProtected,
            RESOLVED: mapElement.dataset.markerResolved,
            NEEDS_ATTENTION: mapElement.dataset.markerAttention
        };

        const map = new GoogleMap(
            mapElement,
            {
                center: {
                    lat: 54.5,
                    lng: -3.0
                },
                zoom: 5,
                mapId: mapElement.dataset.mapId,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: false,
                clickableIcons: false
            }
        );

        const bounds =
            new google.maps.LatLngBounds();

        const markers = [];

        let openInfoWindow = null;

        const getLocation = (card) => {
            const locationParts = [
                card.dataset.townCity,
                card.dataset.region,
                card.dataset.country
            ].filter(
                (part) => part && part.trim()
            );

            if (locationParts.length) {
                return locationParts.join(", ");
            }

            if (
                card.dataset.legacyLocation &&
                card.dataset.legacyLocation.trim()
            ) {
                return card.dataset.legacyLocation;
            }

            return "Location recorded";
        };

        const createMarkerContent = (card) => {
            const image =
                document.createElement("img");

            image.src =
                markerUrls[card.dataset.status] ||
                markerUrls.ACTIVE;

            image.alt = "";
            image.className =
                "home-map-marker-content";

            return image;
        };

        const createInfoWindowContent = (card) => {
            const container =
                document.createElement("div");

            container.className =
                "map-info-window";

            const title =
                document.createElement("strong");

            title.textContent =
                card.dataset.title;

            const location =
                document.createElement("p");

            location.textContent =
                getLocation(card);

            const link =
                document.createElement("a");

            link.href =
                card.dataset.url;

            link.textContent =
                "View report";

            container.appendChild(title);
            container.appendChild(location);
            container.appendChild(link);

            return container;
        };

        cards.forEach((card) => {
            const latitude =
                parseFloat(
                    card.dataset.latitude
                );

            const longitude =
                parseFloat(
                    card.dataset.longitude
                );

            if (
                Number.isNaN(latitude) ||
                Number.isNaN(longitude)
            ) {
                return;
            }

            const position = {
                lat: latitude,
                lng: longitude
            };

            const markerContent =
                createMarkerContent(card);

            const marker =
                new AdvancedMarkerElement({
                    map: map,
                    position: position,
                    title: card.dataset.title,
                    content: markerContent,
                    gmpClickable: true
                });

            const infoWindow =
                new google.maps.InfoWindow({
                    content:
                        createInfoWindowContent(
                            card
                        )
                });

            marker.addEventListener(
                "gmp-click",
                () => {
                    if (openInfoWindow) {
                        openInfoWindow.close();
                    }

                    infoWindow.open({
                        map: map,
                        anchor: marker
                    });

                    openInfoWindow =
                        infoWindow;
                }
            );

            card.addEventListener(
                "mouseenter",
                () => {
                    markerContent.classList.add(
                        "home-map-marker-active"
                    );
                }
            );

            card.addEventListener(
                "mouseleave",
                () => {
                    markerContent.classList.remove(
                        "home-map-marker-active"
                    );
                }
            );

            bounds.extend(position);
            markers.push(marker);
        });

        if (markers.length === 1) {
            map.setCenter(
                bounds.getCenter()
            );

            map.setZoom(13);
        } else if (markers.length > 1) {
            map.fitBounds(bounds);

            google.maps.event.addListenerOnce(
                map,
                "idle",
                () => {
                    if (map.getZoom() > 12) {
                        map.setZoom(12);
                    }
                }
            );
        }
    } catch (error) {
        console.error(
            "I-V Tree homepage map failed to load:",
            error
        );

        mapElement.innerHTML = `
            <div class="home-map-error">
                <p class="section-eyebrow">
                    Map unavailable
                </p>

                <h3>
                    The map could not be loaded
                </h3>

                <p>
                    You can still explore all public
                    tree reports using the full map page.
                </p>
            </div>
        `;
    }
}

window.initHomeMap = initHomeMap;