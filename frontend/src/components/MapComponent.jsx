/**
 * MapComponent - Offline-friendly campus map visualization with Leaflet
 */
import React, { useEffect, useMemo, useState } from 'react';
import { MapContainer, Marker, Polyline, Popup, TileLayer, Tooltip, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const markerTone = {
  accessible: {
    fill: '#16a34a',
    ring: '#bbf7d0',
  },
  blocked: {
    fill: '#dc2626',
    ring: '#fecaca',
  },
};

const makeMarkerIcon = (isAccessible) => {
  const tone = isAccessible ? markerTone.accessible : markerTone.blocked;
  return (
  L.divIcon({
    className: '',
    html: `<div class="campus-marker" style="--marker-fill:${tone.fill};--marker-ring:${tone.ring}"></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -10],
    tooltipAnchor: [14, 0],
  })
  );
};

const crowdColor = (score = 0) => {
  if (score >= 0.66) return '#dc2626';
  if (score >= 0.33) return '#f59e0b';
  return '#16a34a';
};

const crowdLabel = (level = 'low') => level.replace('_', ' ');

const formatWalkingTime = (seconds = 0) => {
  if (!seconds) return 'ETA unavailable';
  const minutes = Math.max(1, Math.round(seconds / 60));
  return `${minutes} min walk`;
};

const FitRoute = ({ positions }) => {
  const map = useMap();

  useEffect(() => {
    if (positions.length > 1) {
      map.fitBounds(positions, { padding: [36, 36] });
    }
  }, [map, positions]);

  return null;
};

const MapClickHandler = ({ onMapClick }) => {
  useMapEvents({
    click: (event) => onMapClick?.(event.latlng),
  });
  return null;
};

export const MapComponent = ({
  center = [29.8655, 77.8976],
  zoom = 16,
  locations = [],
  route = null,
  onLocationClick = null,
  onMapClick = null,
}) => {
  const [isOnline, setIsOnline] = useState(() => navigator.onLine);

  useEffect(() => {
    const updateOnlineStatus = () => setIsOnline(navigator.onLine);
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    return () => {
      window.removeEventListener('online', updateOnlineStatus);
      window.removeEventListener('offline', updateOnlineStatus);
    };
  }, []);

  const locationById = useMemo(
    () => new Map(locations.map((location) => [location.id, location])),
    [locations]
  );

  const routePositions = useMemo(() => {
    if (!route?.path?.length) return [];
    return route.path
      .map((locationId) => locationById.get(locationId))
      .filter(Boolean)
      .map((location) => [location.latitude, location.longitude]);
  }, [locationById, route]);

  const routeSegments = useMemo(() => {
    if (route?.segments?.length) return route.segments;
    if (routePositions.length < 2) return [];
    return routePositions.slice(0, -1).map((position, index) => ({
      positions: [position, routePositions[index + 1]],
      walking_time: route?.walking_time ? route.walking_time / (routePositions.length - 1) : 0,
      crowdedness_score: route?.crowdedness_score || 0,
      crowdedness_level: route?.crowdedness_level || 'low',
    }));
  }, [route, routePositions]);

  return (
    <div className="relative h-full w-full bg-slate-100">
      <MapContainer center={center} zoom={zoom} className="h-full w-full">
        {isOnline && (
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
        )}

        {onMapClick && <MapClickHandler onMapClick={onMapClick} />}

        {routeSegments.length > 0 && (
          <>
            {routeSegments.map((segment, index) => (
              <Polyline
                key={`${segment.route_id || index}-${segment.source_id || index}`}
                positions={segment.positions}
                pathOptions={{
                  color: crowdColor(segment.crowdedness_score),
                  weight: 7,
                  opacity: 0.9,
                  lineCap: 'round',
                  lineJoin: 'round',
                  className: 'campus-route-segment',
                }}
              >
                <Tooltip direction="top" sticky>
                  <div className="text-sm">
                    <p className="font-bold text-gray-950">
                      {formatWalkingTime(segment.effective_walking_time || segment.walking_time)}
                    </p>
                    <p className="capitalize text-gray-600">
                      {crowdLabel(segment.crowdedness_level)} crowd
                    </p>
                  </div>
                </Tooltip>
              </Polyline>
            ))}
            <FitRoute positions={routePositions} />
          </>
        )}

        {locations.map((location) => (
          <Marker
            key={location.id}
            position={[location.latitude, location.longitude]}
            icon={makeMarkerIcon(location.is_accessible)}
            eventHandlers={{
              click: () => onLocationClick?.(location),
            }}
          >
            <Tooltip direction="right" offset={[12, 0]} opacity={1}>
              <span className="font-semibold">{location.name}</span>
            </Tooltip>
            <Popup>
              <div className="min-w-44 p-1">
                <h3 className="font-bold text-gray-900">{location.name}</h3>
                <p className="text-sm text-gray-600">{location.category}</p>
                {location.description && (
                  <p className="mt-1 text-sm text-gray-700">{location.description}</p>
                )}
                {location.is_accessible && (
                  <p className="mt-2 text-xs font-semibold text-emerald-700">Accessible location</p>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      {!isOnline && (
        <div className="pointer-events-none absolute left-3 top-3 z-[500] rounded bg-white/95 px-3 py-2 text-xs font-semibold text-gray-700 shadow">
          Offline campus layer
        </div>
      )}
    </div>
  );
};

export default MapComponent;
