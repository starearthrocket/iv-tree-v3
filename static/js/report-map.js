/* jshint esversion: 8, esnext: false */
/* global google */

async function initReportMap() {
    try {
        const { Map: GoogleMap } =
            await google.maps.importLibrary("maps");

        const { AdvancedMarkerElement } =
            await google.maps.importLibrary("marker");

        const mapElement =
            document.getElementById("report-map");

        if (!mapElement) {
            return;
        }

        const markerUrls = {
            ACTIVE: mapElement.dataset.markerActive,
            IN_PROGRESS: mapElement.dataset.markerProgress,
            PROTECTED: mapElement.dataset.markerProtected,
            RESOLVED: mapElement.dataset.markerResolved,
            NEEDS_ATTENTION: mapElement.dataset.markerAttention
        };

        const reportList =
            document.querySelector(".map-report-list");

        const cards =
            document.querySelectorAll(".map-report-card");

        const searchInput =
            document.getElementById("map-report-search");

        const statusFilter =
            document.getElementById("map-status-filter");

        const filterCount =
            document.getElementById("map-filter-count");

        const clearFiltersButton =
            document.getElementById("clear-map-filters");

        const noResults =
            document.getElementById("map-no-filter-results");

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
                clickableIcons: false
            }
        );

        const reportMapItems = new Map();
        const mapMarkers = [];

        let markerCluster = null;
        let clusteringAvailable = false;
        let openInfoWindow = null;
        let selectedCard = null;

        const getReportLocation = (card) => {
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

            return "Location not specified";
        };

        const createMarkerContent = (card) => {
            const markerImage =
                document.createElement("img");

            markerImage.src =
                markerUrls[card.dataset.status] ||
                markerUrls.ACTIVE;

            markerImage.alt = "";
            markerImage.style.width = "38px";
            markerImage.style.height = "48px";
            markerImage.style.objectFit = "contain";
            markerImage.style.display = "block";
            markerImage.style.transition =
                "transform 0.2s ease";
            markerImage.style.transformOrigin =
                "bottom center";

            return markerImage;
        };

        const createInfoWindowContent = (card) => {
            const container =
                document.createElement("div");

            container.className = "map-info-window";

            const title =
                document.createElement("strong");

            title.textContent = card.dataset.title;

            const location =
                document.createElement("p");

            location.textContent =
                getReportLocation(card);

            const link =
                document.createElement("a");

            link.href = card.dataset.url;
            link.textContent = "View report";

            container.appendChild(title);
            container.appendChild(location);
            container.appendChild(link);

            return container;
        };

        const clearSelectedCard = () => {
            if (!selectedCard) {
                return;
            }

            selectedCard.classList.remove(
                "map-report-card-selected"
            );

            selectedCard = null;
        };

        const selectCard = (card) => {
            clearSelectedCard();

            card.classList.add(
                "map-report-card-selected"
            );

            selectedCard = card;
        };

        const enlargeMarker = (markerContent) => {
            markerContent.style.transform =
                "scale(1.3)";
        };

        const resetMarker = (markerContent) => {
            markerContent.style.transform =
                "scale(1)";
        };

        const resetOtherMarkers = (reportId) => {
            reportMapItems.forEach(
                (item, itemId) => {
                    if (itemId !== reportId) {
                        resetMarker(
                            item.markerContent
                        );
                    }
                }
            );
        };

        const scrollReportToTop = (card) => {
            if (!reportList) {
                return;
            }

            if (
                !window.matchMedia(
                    "(min-width: 901px)"
                ).matches
            ) {
                return;
            }

            const listRectangle =
                reportList.getBoundingClientRect();

            const cardRectangle =
                card.getBoundingClientRect();

            const targetPosition =
                reportList.scrollTop +
                cardRectangle.top -
                listRectangle.top;

            reportList.scrollTo({
                top: targetPosition,
                behavior: "smooth"
            });
        };

        const closePreviousInfoWindow = (
            nextInfoWindow
        ) => {
            if (
                openInfoWindow &&
                openInfoWindow !== nextInfoWindow
            ) {
                openInfoWindow.close();
            }

            openInfoWindow = nextInfoWindow;
        };

        const showReportOnMap = (
            reportId,
            options = {}
        ) => {
            const item =
                reportMapItems.get(reportId);

            if (!item || item.card.hidden) {
                return;
            }

            closePreviousInfoWindow(
                item.infoWindow
            );

            selectCard(item.card);

            enlargeMarker(
                item.markerContent
            );

            resetOtherMarkers(reportId);

            map.panTo(item.position);

            const currentZoom = map.getZoom();

            if (!currentZoom || currentZoom < 16) {
                map.setZoom(16);
            }

            item.infoWindow.setPosition(
                item.position
            );

            item.infoWindow.open({
                map: map
            });

            if (options.scrollReport) {
                scrollReportToTop(item.card);
            }
        };

        const moveToMapOnSmallScreen = () => {
            if (
                window.matchMedia(
                    "(max-width: 900px)"
                ).matches
            ) {
                mapElement.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        };

        const getCardSearchText = (card) => {
            return [
                card.dataset.title,
                card.dataset.treeSpecies,
                card.dataset.townCity,
                card.dataset.region,
                card.dataset.country,
                card.dataset.legacyLocation,
                card.dataset.what3words
            ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase();
        };

        const cardMatchesFilters = (card) => {
            let searchTerm = "";

            if (searchInput) {
                searchTerm = searchInput.value
                    .trim()
                    .toLowerCase();
            }

            let selectedStatus = "";

            if (statusFilter) {
                selectedStatus = statusFilter.value;
            }

            const searchMatches =
                !searchTerm ||
                getCardSearchText(card).includes(
                    searchTerm
                );

            const statusMatches =
                !selectedStatus ||
                card.dataset.status ===
                    selectedStatus;

            return (
                searchMatches &&
                statusMatches
            );
        };

        const fitVisibleMarkers = (
            visibleItems
        ) => {
            if (!visibleItems.length) {
                map.setCenter({
                    lat: 54.5,
                    lng: -3.0
                });

                map.setZoom(5);
                return;
            }

            const visibleBounds =
                new google.maps.LatLngBounds();

            visibleItems.forEach((item) => {
                visibleBounds.extend(
                    item.position
                );
            });

            if (visibleItems.length === 1) {
                map.setCenter(
                    visibleItems[0].position
                );

                map.setZoom(13);
                return;
            }

            map.fitBounds(visibleBounds);
        };

        const updateFilterCount = (
            visibleCount
        ) => {
            if (!filterCount) {
                return;
            }

            const totalCount = cards.length;
            let treeWord = "trees";

            if (totalCount === 1) {
                treeWord = "tree";
            }

            filterCount.textContent =
                `Showing ${visibleCount} of ` +
                `${totalCount} ${treeWord}`;
        };

        const updateFilters = () => {
            const visibleItems = [];

            if (openInfoWindow) {
                openInfoWindow.close();
                openInfoWindow = null;
            }

            clearSelectedCard();

            reportMapItems.forEach((item) => {
                resetMarker(
                    item.markerContent
                );
            });

            cards.forEach((card) => {
                const isVisible =
                    cardMatchesFilters(card);

                card.hidden = !isVisible;

                if (isVisible) {
                    const item =
                        reportMapItems.get(
                            card.dataset.reportId
                        );

                    if (item) {
                        visibleItems.push(item);
                    }
                }
            });

            const visibleMarkers =
                visibleItems.map(
                    (item) => item.marker
                );

            if (
                clusteringAvailable &&
                markerCluster
            ) {
                markerCluster.clearMarkers();

                if (visibleMarkers.length) {
                    markerCluster.addMarkers(
                        visibleMarkers
                    );
                }
            } else {
                reportMapItems.forEach(
                    (item) => {
                        if (
                            visibleMarkers.includes(
                                item.marker
                            )
                        ) {
                            item.marker.map = map;
                        } else {
                            item.marker.map = null;
                        }
                    }
                );
            }

            updateFilterCount(
                visibleItems.length
            );

            if (noResults) {
                noResults.hidden =
                    visibleItems.length !== 0;
            }

            const filtersActive =
                (
                    searchInput &&
                    searchInput.value.trim()
                ) ||
                (
                    statusFilter &&
                    statusFilter.value
                );

            if (clearFiltersButton) {
                clearFiltersButton.hidden =
                    !filtersActive;
            }

            if (
                reportList &&
                visibleItems.length
            ) {
                reportList.scrollTop = 0;
            }

            fitVisibleMarkers(
                visibleItems
            );
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

            const reportId =
                card.dataset.reportId;

            const position = {
                lat: latitude,
                lng: longitude
            };

            const markerContent =
                createMarkerContent(card);

            const marker =
                new AdvancedMarkerElement({
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

            reportMapItems.set(
                reportId,
                {
                    marker: marker,
                    markerContent: markerContent,
                    infoWindow: infoWindow,
                    card: card,
                    position: position
                }
            );

            mapMarkers.push(marker);

            marker.addEventListener(
                "gmp-click",
                () => {
                    showReportOnMap(
                        reportId,
                        {
                            scrollReport: true
                        }
                    );
                }
            );

            card.addEventListener(
                "mouseenter",
                () => {
                    enlargeMarker(
                        markerContent
                    );
                }
            );

            card.addEventListener(
                "mouseleave",
                () => {
                    if (selectedCard !== card) {
                        resetMarker(
                            markerContent
                        );
                    }
                }
            );

            card.addEventListener(
                "click",
                (event) => {
                    if (
                        event.target.closest("a")
                    ) {
                        return;
                    }

                    showReportOnMap(reportId);
                }
            );
        });

        const clusterRenderer = {
            render: ({
                count,
                position
            }) => {
                const clusterElement =
                    document.createElement("div");

                clusterElement.textContent =
                    String(count);

                clusterElement.setAttribute(
                    "aria-label",
                    `${count} public tree reports in this area`
                );

                clusterElement.style.width =
                    "46px";

                clusterElement.style.height =
                    "46px";

                clusterElement.style.borderRadius =
                    "50%";

                clusterElement.style.background =
                    "#166B3A";

                clusterElement.style.border =
                    "3px solid #F7F5EC";

                clusterElement.style.color =
                    "#FFFFFF";

                clusterElement.style.fontSize =
                    "16px";

                clusterElement.style.fontWeight =
                    "700";

                clusterElement.style.display =
                    "flex";

                clusterElement.style.alignItems =
                    "center";

                clusterElement.style.justifyContent =
                    "center";

                clusterElement.style.boxShadow =
                    "0 3px 10px rgba(15, 61, 46, 0.35)";

                clusterElement.style.cursor =
                    "pointer";

                return new AdvancedMarkerElement({
                    position: position,
                    content: clusterElement,
                    title:
                        `${count} public tree reports in this area`,
                    gmpClickable: true,
                    zIndex: 1000 + count
                });
            }
        };

        if (
            window.markerClusterer &&
            window.markerClusterer.MarkerClusterer
        ) {
            clusteringAvailable = true;

            markerCluster =
                new window.markerClusterer
                    .MarkerClusterer({
                        map: map,
                        markers: mapMarkers,
                        algorithmOptions: {
                            maxZoom: 15
                        },
                        renderer: clusterRenderer
                    });

        } else {
            console.warn(
                "Marker clustering unavailable. " +
                "Displaying individual markers."
            );

            mapMarkers.forEach((marker) => {
                marker.map = map;
            });
        }

        const showMapLinks =
            document.querySelectorAll(
                ".map-show-link"
            );

        showMapLinks.forEach((link) => {
            link.addEventListener(
                "click",
                (event) => {
                    event.preventDefault();

                    showReportOnMap(
                        link.dataset.reportId
                    );

                    moveToMapOnSmallScreen();
                }
            );
        });

        if (searchInput) {
            searchInput.addEventListener(
                "input",
                updateFilters
            );
        }

        if (statusFilter) {
            statusFilter.addEventListener(
                "change",
                updateFilters
            );
        }

        if (clearFiltersButton) {
            clearFiltersButton.addEventListener(
                "click",
                () => {
                    if (searchInput) {
                        searchInput.value = "";
                    }

                    if (statusFilter) {
                        statusFilter.value = "";
                    }

                    updateFilters();

                    if (searchInput) {
                        searchInput.focus();
                    }
                }
            );
        }

        if (mapMarkers.length === 1) {
            const firstItem =
                reportMapItems
                    .values()
                    .next()
                    .value;

            if (firstItem) {
                map.setCenter(
                    firstItem.position
                );

                map.setZoom(13);
            }

        } else if (mapMarkers.length > 1) {
            const initialBounds =
                new google.maps.LatLngBounds();

            reportMapItems.forEach(
                (item) => {
                    initialBounds.extend(
                        item.position
                    );
                }
            );

            map.fitBounds(initialBounds);
        }

    } catch (error) {
        console.error(
            "I-V Tree report map failed to load:",
            error
        );

        const mapElement =
            document.getElementById(
                "report-map"
            );

        if (mapElement) {
            mapElement.innerHTML = `
                <div class="map-placeholder-content">
                    <p class="section-eyebrow">
                        Map unavailable
                    </p>

                    <h2>
                        The map could not be loaded
                    </h2>

                    <p>
                        You can still browse the public
                        reports alongside the map.
                    </p>
                </div>
            `;
        }
    }
}

window.initReportMap = initReportMap;