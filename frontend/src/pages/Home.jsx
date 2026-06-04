/**
 * Home Page
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import NavBar from '../components/NavBar';
import SearchBar from '../components/SearchBar';
import MapComponent from '../components/MapComponent';
import { mapService } from '../services/mapService';

const Home = () => {
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [currentLocationId, setCurrentLocationId] = useState('');
  const [signals, setSignals] = useState(null);
  const [weather, setWeather] = useState(null);
  const [presenceMessage, setPresenceMessage] = useState('');
  const accessibleCount = locations.filter((location) => location.is_accessible).length;
  const displayedAccessibleCount = locations.length ? accessibleCount : metrics?.accessible_locations ?? 0;

  useEffect(() => {
    const loadHomeData = async () => {
      try {
        const [locationResponse, metricResponse, signalResponse] = await Promise.all([
          mapService.getAllLocations(),
          mapService.getAccessibilityMetrics(),
          mapService.getSignals(),
        ]);
        setLocations(locationResponse.items || []);
        setMetrics(metricResponse);
        setSignals(signalResponse);
      } catch (error) {
        console.error('Home data load failed:', error);
      }
    };

    loadHomeData();
  }, []);

  const handleLocationSelect = (location) => {
    setSelectedLocation(location);
    navigate('/navigation', { state: { destination: location.name } });
  };

  const handleCurrentLocationChange = async (locationId) => {
    setCurrentLocationId(locationId);
    setPresenceMessage('');
    if (!locationId) {
      setWeather(null);
      return;
    }

    try {
      const response = await mapService.setCurrentLocation(getSessionId(), Number(locationId));
      const [signalResponse, weatherResponse] = await Promise.all([
        mapService.getSignals(),
        mapService.getWeather({ locationId: Number(locationId) }),
      ]);
      setSignals(signalResponse);
      setWeather(weatherResponse);
      setPresenceMessage(
        `${response.location.name} saved. ${response.active_here} active app user(s) here.`
      );
    } catch (error) {
      setPresenceMessage(error.response?.data?.detail || 'Unable to update current location.');
    }
  };

  const handleDetectLocation = () => {
    setPresenceMessage('');
    if (!navigator.geolocation) {
      setPresenceMessage('Location detection is not supported in this browser.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const nearest = findNearestLocation(
          position.coords.latitude,
          position.coords.longitude,
          locations
        );
        if (nearest) {
          handleCurrentLocationChange(String(nearest.id));
        }
      },
      () => setPresenceMessage('Unable to detect location. Please allow browser location access.'),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />

      <main className="mx-auto max-w-7xl px-4 py-6">
        <section className="grid gap-5 lg:grid-cols-[420px_minmax(0,1fr)]">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <p className="mb-2 text-sm font-bold uppercase text-emerald-700">Offline-first campus routing</p>
            <h1 className="text-4xl font-bold leading-tight text-slate-950">Find useful campus routes, not just roads.</h1>
            <p className="mt-3 text-slate-600">
              Search buildings, hostels, mess points, accessible paths, and crowded route status from local campus data.
            </p>

            {/* <div className="mt-5">
              <SearchBar onLocationSelect={handleLocationSelect} placeholder="Where do you want to go?" />
            </div> */}

            <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3">
              <label className="mb-2 block text-sm font-bold text-emerald-900">I am currently at</label>
              <div className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_auto]">
                <select
                  value={currentLocationId}
                  onChange={(event) => handleCurrentLocationChange(event.target.value)}
                  className="w-full rounded border border-emerald-200 bg-white px-3 py-2 text-sm font-semibold text-gray-800"
                >
                  <option value="">Select current campus point</option>
                  {locations.map((location) => (
                    <option key={location.id} value={location.id}>
                      {location.name}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleDetectLocation}
                  className="rounded-md bg-emerald-700 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-emerald-800"
                >
                  Get location
                </button>
              </div>
              {presenceMessage && <p className="mt-2 text-xs font-semibold text-emerald-800">{presenceMessage}</p>}
            </div>

            <div className="mt-5 grid grid-cols-2 gap-3">
              <button
                onClick={() => navigate('/navigation')}
                className="rounded-md bg-slate-950 px-4 py-3 font-semibold text-white shadow-sm hover:bg-slate-800"
              >
                Plan route
              </button>
              <button
                onClick={() => navigate('/admin')}
                className="rounded-md border border-slate-300 bg-white px-4 py-3 font-semibold text-slate-800 hover:bg-slate-50"
              >
                Admin tools
              </button>
            </div>

            <div className="mt-5 grid grid-cols-2 gap-2">
              <Signal label="Locations" value={locations.length} />
              <Signal label="Accessible" value={displayedAccessibleCount} tone="green" />
              {/* <Signal label="Live users" value={signals?.active_presence ?? 0} /> */}
              {currentLocationId && weather && (
                <Signal
                  label="Weather"
                  value={`${weather.condition}${weather.temperature_c ? ` ${Math.round(weather.temperature_c)}C` : ''}`}
                />
              )}
            </div>
          </div>

          <div className="relative min-h-[460px] overflow-hidden rounded-lg border border-slate-200 bg-white shadow-md">
            <MapComponent
              locations={locations}
              onLocationClick={(location) => setSelectedLocation(location)}
            />
            <MapLegend />
          </div>
        </section>

        <section className="mt-6 grid gap-4 md:grid-cols-4">
          <Feature title="Detailed micro-maps" text="Hostel, mess, department, and gate nodes can be maintained separately from public maps." />
          <Feature title="Live route status" text="Admins can mark paths as blocked or crowded directly from the dashboard." />
          <Feature title="Smart ETA" text="Routing combines Dijkstra or A*, crowd level, accessibility, weather, and route status." />
          <Feature title="Personal routing" text="History and favorites support recommendations based on repeated user movement." />
        </section>

        {selectedLocation && (
          <section className="mt-6 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
              <div>
                <h2 className="text-xl font-bold text-gray-950">{selectedLocation.name}</h2>
                <p className="text-sm font-semibold text-gray-500">{selectedLocation.category}</p>
                <p className="mt-1 text-gray-700">{selectedLocation.description}</p>
              </div>
              <button
                onClick={() => handleLocationSelect(selectedLocation)}
                className="rounded-md bg-slate-950 px-4 py-3 font-semibold text-white hover:bg-slate-800"
              >
                Route here
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
};

const getSessionId = () => {
  const existing = localStorage.getItem('campus_session_id');
  if (existing) return existing;
  const sessionId = `campus-${window.crypto?.randomUUID?.() || Math.random().toString(36).slice(2)}`;
  localStorage.setItem('campus_session_id', sessionId);
  return sessionId;
};

const findNearestLocation = (latitude, longitude, locations) => {
  if (!locations.length) return null;
  return locations.reduce((nearest, location) => {
    const distance = distanceMeters(latitude, longitude, location.latitude, location.longitude);
    if (!nearest || distance < nearest.distance) {
      return { ...location, distance };
    }
    return nearest;
  }, null);
};

const distanceMeters = (lat1, lon1, lat2, lon2) => {
  const radius = 6371000;
  const toRad = (value) => (value * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
  return radius * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
};

const Signal = ({ label, value, tone = 'blue' }) => (
  <div className={`rounded-lg border p-3 ${tone === 'green' ? 'border-emerald-100 bg-emerald-50' : 'border-sky-100 bg-sky-50'}`}>
    <p className={`text-xs font-semibold uppercase ${tone === 'green' ? 'text-emerald-700' : 'text-sky-700'}`}>{label}</p>
    <p className={`mt-1 text-xl font-bold ${tone === 'green' ? 'text-emerald-950' : 'text-sky-950'}`}>{value}</p>
  </div>
);

const Feature = ({ title, text }) => (
  <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
    <h3 className="font-bold text-slate-950">{title}</h3>
    <p className="mt-2 text-sm text-slate-600">{text}</p>
  </div>
);

const MapLegend = () => (
  <div className="pointer-events-none absolute bottom-3 left-3 z-[500] rounded-lg bg-white/95 px-3 py-2 text-xs font-semibold text-slate-700 shadow">
    <div className="flex items-center gap-2">
      <span className="h-2.5 w-2.5 rounded-full bg-emerald-600" /> Accessible
    </div>
    <div className="mt-1 flex items-center gap-2">
      <span className="h-2.5 w-2.5 rounded-full bg-red-600" /> Not accessible
    </div>
  </div>
);

export default Home;
