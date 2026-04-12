import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for leaflet marker icon issue in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom icon for campus
const campusIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// To dynamically fly to a marker
const MapController = ({ focusLocation }) => {
    const map = useMap();
    useEffect(() => {
        if (focusLocation) {
            map.flyTo([focusLocation.latitude, focusLocation.longitude], 15, { animate: true });
        }
    }, [focusLocation, map]);
    return null;
};

export const MapView = ({ restaurants, focusRestaurant, onMapClose }) => {
    const defaultCenter = [26.8636, 81.0008]; // IIIT Lucknow
    
    return (
        <div className="relative w-full h-80 rounded-xl overflow-hidden border border-cardsTheme shadow-sm z-0">
            <button 
                onClick={onMapClose}
                className="absolute top-2 right-2 z-[400] bg-white text-gray-800 p-1.5 rounded-md shadow-md text-sm font-bold hover:bg-gray-100"
            >
                Close Map
            </button>
            <MapContainer center={defaultCenter} zoom={12} scrollWheelZoom={false}>
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                />
                
                <Marker position={defaultCenter} icon={campusIcon}>
                    <Popup>
                        <div className="font-bold text-primary">IIIT Lucknow</div>
                        <div className="text-xs">You are here</div>
                    </Popup>
                </Marker>

                {restaurants.map((r, i) => (
                    <Marker key={r.id || i} position={[r.latitude, r.longitude]}>
                        <Popup>
                            <div className="font-semibold">{r.name}</div>
                            <div className="text-xs text-gray-600 mb-1">{r.area} | ⭐ {r.rating}</div>
                            <div className="text-xs">💰 ₹{r.budget_per_person_inr} per person</div>
                            <div className="text-xs">📍 {r.distance_from_campus_km}km from campus</div>
                        </Popup>
                    </Marker>
                ))}
                
                {focusRestaurant && <MapController focusLocation={focusRestaurant} />}
            </MapContainer>
        </div>
    );
};
