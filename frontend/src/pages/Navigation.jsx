/**
 * Navigation Page - Main routing interface
 */
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import NavBar from '../components/NavBar';
import SearchBar from '../components/SearchBar';
import RouteDetails from '../components/RouteDetails';
import MapComponent from '../components/MapComponent';
import { mapService } from '../services/mapService';

const modes = [
  { id: 'fastest', label: 'Fastest', hint: 'Best ETA' },
  { id: 'shortest', label: 'Shortest', hint: 'Least distance' },
  { id: 'accessible', label: 'Accessible', hint: 'Ramp friendly' },
  { id: 'low_crowd', label: 'Best route (Low crowd + frequently visited)', hint: 'Personalized' },
];

const Navigation = () => {
  const location = useLocation();
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState(location.state?.destination || '');
  const [sourceInput, setSourceInput] = useState('');
  const [destinationInput, setDestinationInput] = useState(location.state?.destination || '');
  const [sourceSearchReset, setSourceSearchReset] = useState(0);
  const [destinationSearchReset, setDestinationSearchReset] = useState(0);
  const [mode, setMode] = useState('fastest');
  const [algorithm, setAlgorithm] = useState('dijkstra');
  const [route, setRoute] = useState(null);
  const [locations, setLocations] = useState([]);
  const [signals, setSignals] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadLocations = async () => {
      try {
        const [response, signalResponse] = await Promise.all([
          mapService.getAllLocations(),
          mapService.getSignals(),
        ]);
        setLocations(response.items || []);
        setSignals(signalResponse);
      } catch (err) {
        setError('Unable to load local campus locations. Start the backend server first.');
      }
    };

    loadLocations();
  }, []);

  const setSourceSilently = (locationName) => {
    setSource(locationName);
    setSourceInput(locationName);
    setSourceSearchReset((key) => key + 1);
  };

  const setDestinationSilently = (locationName) => {
    setDestination(locationName);
    setDestinationInput(locationName);
    setDestinationSearchReset((key) => key + 1);
  };

  const handleFindRoute = async () => {
    if (!source || !destination) {
      setError('Choose both source and destination.');
      return;
    }

    setLoading(true);
    setError('');
    setComparison(null);

    try {
      const result = await mapService.findRoute(source, destination, mode, algorithm);
      setRoute(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to find route.');
    } finally {
      setLoading(false);
    }
  };

  const handleCompareRoutes = async () => {
    if (!source || !destination) {
      setError('Choose both source and destination.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await mapService.compareRoutes(source, destination);
      setComparison(result.routes || {});
    } catch (err) {
      setError('Failed to compare routes.');
    } finally {
      setLoading(false);
    }
  };

  const handleDetectSource = () => {
    setError('');

    if (!navigator.geolocation) {
      setError('Location detection is not supported in this browser.');
      return;
    }

    if (!locations.length) {
      setError('Campus locations are still loading.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const nearest = findNearestLocation(
          position.coords.latitude,
          position.coords.longitude,
          locations
        );

        if (!nearest) {
          setError('Unable to match your current position to a campus location.');
          return;
        }

        setSourceSilently(nearest.name);
        setSelectedLocation(nearest);
      },
      () => setError('Unable to detect location. Please allow browser location access.'),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const handleMapLocationClick = (campusLocation) => {
    setSelectedLocation(campusLocation);

    if (!source) {
      setSourceSilently(campusLocation.name);
      return;
    }

    setDestinationSilently(campusLocation.name);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />

      <div className="mx-auto max-w-7xl px-4 py-6">
        <div className="mb-4 flex flex-col justify-between gap-3 md:flex-row md:items-end">
          <div>
            <h1 className="text-3xl font-bold text-slate-950">Campus navigator</h1>
            <p className="mt-1 text-slate-600">
              Search local campus data, compare routes, and use the map even when tiles are offline.
            </p>
          </div>
          <div className="rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-800">
            {locations.length} local locations loaded
          </div>
        </div>

        <div className="grid gap-5 lg:grid-cols-[380px_minmax(0,1fr)]">
          <aside className="space-y-4">
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold text-slate-950">Plan route</h2>
                <select
                  value={algorithm}
                  onChange={(event) => setAlgorithm(event.target.value)}
                  className="rounded border border-gray-300 px-2 py-1 text-sm"
                >
                  <option value="dijkstra">Dijkstra</option>
                  <option value="astar">A*</option>
                </select>
              </div>

              {/* {signals?.weather && (
                <div className="mb-4 rounded border border-emerald-200 bg-emerald-50 px-3 py-2">
                  <p className="text-xs font-bold uppercase text-emerald-700">ETA weather signal</p>
                  <p className="text-sm font-semibold text-emerald-950">
                    {signals.weather.condition} {signals.weather.temperature_c ? `, ${Math.round(signals.weather.temperature_c)} C` : ''}
                  </p>
                </div>
              )} */}

              {error && (
                <div className="mb-4 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">
                  {error}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-semibold text-gray-700">From</label>
                  <SearchBar
                    value={sourceInput}
                    placeholder="Search start point"
                    resetSearchKey={sourceSearchReset}
                    onLocationSelect={(loc) => setSourceSilently(loc.name)}
                    onChange={(value) => {
                      setSourceInput(value);
                      setSource('');
                    }}
                    rightSlot={
                      <div className="flex items-center gap-1">
                        <button
                          type="button"
                          onClick={handleDetectSource}
                          title="Use current location"
                          className="rounded-md p-1.5 text-slate-500 hover:bg-emerald-50 hover:text-emerald-700"
                        >
                          <LocationIcon />
                        </button>
                        {source && (
                          <button
                            type="button"
                            onClick={() => setSourceSilently('')}
                            title="Clear source"
                            className="rounded-md px-2 py-1 text-sm font-bold text-slate-500 hover:bg-red-50 hover:text-red-600"
                          >
                            x
                          </button>
                        )}
                      </div>
                    }
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-semibold text-gray-700">To</label>
                  <SearchBar
                    value={destinationInput}
                    placeholder="Search destination"
                    resetSearchKey={destinationSearchReset}
                    onLocationSelect={(loc) => setDestinationSilently(loc.name)}
                    onChange={(value) => {
                      setDestinationInput(value);
                      setDestination('');
                    }}
                    rightSlot={
                      destination ? (
                        <button
                          type="button"
                          onClick={() => setDestinationSilently('')}
                          title="Clear destination"
                          className="rounded-md px-2 py-1 text-sm font-bold text-slate-500 hover:bg-red-50 hover:text-red-600"
                        >
                          x
                        </button>
                      ) : null
                    }
                  />
                </div>
              </div>

              <div className="mt-5 grid grid-cols-2 gap-2">
                {modes.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setMode(item.id)}
                    className={`rounded-md border px-3 py-2 text-left transition ${
                      mode === item.id
                        ? 'border-slate-950 bg-slate-950 text-white'
                        : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <span className="block text-sm font-bold">{item.label}</span>
                    <span className="block text-xs">{item.hint}</span>
                  </button>
                ))}
              </div>

              <div className="mt-5 grid grid-cols-2 gap-2">
                <button
                  onClick={handleFindRoute}
                  disabled={loading}
                  className="rounded-md bg-slate-950 px-4 py-3 font-semibold text-white shadow-sm hover:bg-slate-800 disabled:bg-gray-400"
                >
                  {loading ? 'Finding...' : 'Find route'}
                </button>
                <button
                  onClick={handleCompareRoutes}
                  disabled={loading}
                  className="rounded-md border border-slate-300 bg-white px-4 py-3 font-semibold text-slate-800 hover:bg-slate-50 disabled:text-gray-400"
                >
                  Compare
                </button>
              </div>
            </div>

            {selectedLocation && (
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <h3 className="font-bold text-slate-950">{selectedLocation.name}</h3>
                <p className="text-sm text-gray-500">{selectedLocation.category}</p>
                <p className="mt-2 text-sm text-gray-700">{selectedLocation.description}</p>
              </div>
            )}

            {route && <RouteDetails route={route} loading={loading} />}

            {comparison && (
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <h3 className="mb-3 font-bold text-slate-950">Route comparison</h3>
                <div className="space-y-2">
                  {Object.entries(comparison).map(([key, value]) => (
                    <button
                      key={key}
                      onClick={() => value?.path && setRoute({ ...value, source, destination, mode: key })}
                      className="flex w-full items-center justify-between rounded border border-gray-200 px-3 py-2 text-left hover:bg-gray-50"
                    >
                      <span className="font-semibold capitalize text-gray-800">{key.replace('_', ' ')}</span>
                      <span className="text-sm text-gray-500">
                        {value?.distance ? `${Math.round(value.distance)} m` : 'No route'}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </aside>

          <main className="relative min-h-[620px] overflow-hidden rounded-lg border border-slate-200 bg-white shadow-md">
            <MapComponent
              locations={locations}
              route={route}
              onLocationClick={handleMapLocationClick}
            />
            <RouteLegend />
          </main>
        </div>
      </div>
    </div>
  );
};

const LocationIcon = () => (
  <svg
    aria-hidden="true"
    viewBox="0 0 24 24"
    className="h-5 w-5"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 21s7-5.4 7-12a7 7 0 1 0-14 0c0 6.6 7 12 7 12z" />
    <circle cx="12" cy="9" r="2.5" />
  </svg>
);

const RouteLegend = () => (
  <div className="pointer-events-none absolute bottom-3 left-3 z-[500] rounded-lg bg-white/95 px-3 py-2 text-xs font-semibold text-slate-700 shadow">
    <div className="flex items-center gap-2">
      <span className="h-1.5 w-6 rounded bg-emerald-600" /> Low crowd
    </div>
    <div className="mt-1 flex items-center gap-2">
      <span className="h-1.5 w-6 rounded bg-amber-500" /> Crowded
    </div>
    <div className="mt-1 flex items-center gap-2">
      <span className="h-1.5 w-6 rounded bg-red-600" /> Very crowded
    </div>
  </div>
);

const findNearestLocation = (latitude, longitude, locations) => {
  if (!locations.length) return null;
  return locations.reduce((nearest, campusLocation) => {
    const distance = distanceMeters(
      latitude,
      longitude,
      campusLocation.latitude,
      campusLocation.longitude
    );

    if (!nearest || distance < nearest.distance) {
      return { ...campusLocation, distance };
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

export default Navigation;
