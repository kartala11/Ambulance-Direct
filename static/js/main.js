// Initialize map
let map, currentLocationMarker, hospitalsLayer;

function initMap() {
    map = new MapmyIndia.Map("map", {
        center: [28.644800, 77.216721], // Default center, will update to current location
        zoom: 14
    });
    
    // Get driver's current location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const currentLatLng = [position.coords.latitude, position.coords.longitude];
            map.setView(currentLatLng, 14);
            
            currentLocationMarker = L.marker(currentLatLng).addTo(map).bindPopup("You are here").openPopup();
            
            // Fetch and display nearby hospitals based on current location
            fetchHospitals(currentLatLng);
        });
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

// Fetch hospitals from the server
function fetchHospitals(currentLatLng) {
    fetch('/api/get_nearby_hospitals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: currentLatLng[0], longitude: currentLatLng[1] })
    })
    .then(response => response.json())
    .then(hospitals => {
        hospitalsLayer = L.layerGroup().addTo(map);
        
        hospitals.forEach(hospital => {
            L.marker([hospital.latitude, hospital.longitude]).addTo(hospitalsLayer)
              .bindPopup(`<b>${hospital.name}</b><br>Beds Available: ${hospital.beds_available}`)
              .on('click', function() {
                  showDirections(currentLatLng, [hospital.latitude, hospital.longitude], hospital.id);
              });
        });
    });
}

// Show directions to the selected hospital
function showDirections(start, end, hospitalId) {
    fetch(`https://apis.mapmyindia.com/advancedmaps/v1/{{ token }}/route_adv/driving/${start[0]},${start[1]};${end[0]},${end[1]}`)
    .then(response => response.json())
    .then(data => {
        const route = data.routes[0].geometry.coordinates.map(coord => [coord[1], coord[0]]);
        const routePolyline = L.polyline(route, { color: 'blue' }).addTo(map);

        // Mark traffic signals along the route and send Discord notifications
        fetch('/api/get_traffic_signals', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ route })
        })
        .then(response => response.json())
        .then(signals => {
            signals.forEach(signal => {
                L.marker([signal.latitude, signal.longitude], { icon: L.icon({ iconUrl: 'signal-icon.png' }) }).addTo(map)
                  .bindPopup("Traffic Signal");
                
                // Send Discord notification
                fetch('/api/notify_traffic_police', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ discord_username: signal.discord_username, hospital_id: hospitalId })
                });
            });
        });
    });
}

// Initialize map on page load
window.onload = initMap;
