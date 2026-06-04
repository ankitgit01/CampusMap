/**
 * AdminPanel Component - For admin dashboard
 */
import React, { useEffect, useMemo, useState } from 'react';
import api from '../services/api';
import { mapService } from '../services/mapService';
import MapComponent from './MapComponent';

const emptyLocation = {
  name: '',
  category: 'Building',
  description: '',
  latitude: '',
  longitude: '',
  is_accessible: true,
  has_ramp: true,
  has_elevator: false,
  has_wheelchair_access: true,
  accessibility_score: 0.8,
};

const emptyRoute = {
  source_id: '',
  destination_id: '',
  distance: '',
  walking_time: '',
  route_type: 'Footpath',
  crowdedness_score: 0.15,
  accessibility_score: 0.8,
  is_blocked: false,
  blocked_reason: '',
  is_wheelchair_accessible: true,
  has_weather_cover: false,
  has_lighting: true,
  has_stairs: false,
  has_slope: false,
};

const routeTypes = ['Footpath', 'Road', 'Corridor', 'Bridge', 'Ramp'];
const crowdLevels = [
  { label: 'Low', value: 0.15 },
  { label: 'Crowded', value: 0.5 },
  { label: 'Very crowded', value: 0.8 },
];

export const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('routes');
  const [statistics, setStatistics] = useState(null);
  const [locations, setLocations] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [signals, setSignals] = useState(null);
  const [locationForm, setLocationForm] = useState(emptyLocation);
  const [routeForm, setRouteForm] = useState(emptyRoute);
  const [editingLocationId, setEditingLocationId] = useState(null);
  const [mapMode, setMapMode] = useState('location');
  const [routeReason, setRouteReason] = useState({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const locationsById = useMemo(
    () => new Map(locations.map((location) => [location.id, location])),
    [locations]
  );

  useEffect(() => {
    refreshAdminData();
  }, []);

  const refreshAdminData = async () => {
    setLoading(true);
    try {
      const [statsResponse, locationResponse, routeResponse, signalResponse] = await Promise.all([
        api.get('/admin/statistics'),
        mapService.getAllLocations(),
        mapService.getAllRoutes(),
        mapService.getSignals(),
      ]);
      setStatistics(statsResponse.data);
      setLocations(locationResponse.items || []);
      setRoutes(routeResponse.items || []);
      setSignals(signalResponse);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to load admin data.');
    } finally {
      setLoading(false);
    }
  };

  const normalizedLocationPayload = {
    ...locationForm,
    latitude: Number(locationForm.latitude),
    longitude: Number(locationForm.longitude),
    accessibility_score: Number(locationForm.accessibility_score),
  };

  const normalizedRoutePayload = {
    ...routeForm,
    source_id: Number(routeForm.source_id),
    destination_id: Number(routeForm.destination_id),
    distance: Number(routeForm.distance),
    walking_time: Number(routeForm.walking_time),
    crowdedness_score: Number(routeForm.crowdedness_score),
    accessibility_score: Number(routeForm.accessibility_score),
    blocked_reason: routeForm.is_blocked ? routeForm.blocked_reason || 'Marked by admin' : null,
  };

  const handleSaveLocation = async (event) => {
    event.preventDefault();
    setMessage('');
    try {
      if (editingLocationId) {
        await mapService.updateLocation(editingLocationId, normalizedLocationPayload);
        setMessage('Location updated.');
      } else {
        await api.post('/admin/locations', normalizedLocationPayload);
        setMessage('Location added.');
      }
      setLocationForm(emptyLocation);
      setEditingLocationId(null);
      refreshAdminData();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to save location.');
    }
  };

  const startLocationMapSelection = () => {
    setActiveTab('map');
    setMapMode('location');
    setMessage('Click the map to fill latitude and longitude for the location form.');
  };

  const startRouteMapSelection = () => {
    setRouteForm({ ...routeForm, source_id: '', destination_id: '', distance: '', walking_time: '' });
    setActiveTab('map');
    setMapMode('route');
    setMessage('Click two existing markers to select route endpoints.');
  };

  const handleEditLocation = (location) => {
    setEditingLocationId(location.id);
    setLocationForm({
      name: location.name,
      category: location.category,
      description: location.description || '',
      latitude: location.latitude,
      longitude: location.longitude,
      is_accessible: location.is_accessible,
      has_ramp: location.has_ramp,
      has_elevator: location.has_elevator,
      has_wheelchair_access: location.has_wheelchair_access,
      accessibility_score: location.accessibility_score ?? 0.8,
    });
    setActiveTab('locations');
  };

  const handleDeleteLocation = async (locationId) => {
    setMessage('');
    try {
      await api.delete(`/admin/locations/${locationId}`);
      setMessage('Location removed.');
      refreshAdminData();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to remove location.');
    }
  };

  const handleCreateRoute = async (event) => {
    event.preventDefault();
    setMessage('');
    if (!routeForm.source_id || !routeForm.destination_id || routeForm.source_id === routeForm.destination_id) {
      setMessage('Select two different locations for the route.');
      return;
    }
    try {
      await mapService.createRoute(normalizedRoutePayload);
      setRouteForm(emptyRoute);
      setMessage('Route added.');
      refreshAdminData();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to add route.');
    }
  };

  const handleAdminMapClick = (latlng) => {
    if (mapMode !== 'location') return;
    setLocationForm({
      ...locationForm,
      latitude: latlng.lat.toFixed(6),
      longitude: latlng.lng.toFixed(6),
    });
    setActiveTab('locations');
    setMessage('Map point selected for the location form.');
  };

  const handleAdminLocationClick = (location) => {
    if (mapMode !== 'route') {
      handleEditLocation(location);
      return;
    }
    if (!routeForm.source_id) {
      setRouteForm({ ...routeForm, source_id: location.id });
      setMessage(`${location.name} selected as route start.`);
      return;
    }
    if (String(routeForm.source_id) === String(location.id)) {
      setMessage('Choose a different destination location.');
      return;
    }
    const source = locationsById.get(Number(routeForm.source_id));
    const distance = source ? Math.round(distanceMeters(source.latitude, source.longitude, location.latitude, location.longitude)) : routeForm.distance;
    setRouteForm({
      ...routeForm,
      destination_id: location.id,
      distance,
      walking_time: Math.max(30, Math.round(distance / 1.25)),
    });
    setMessage(`${location.name} selected as route destination.`);
  };

  const handleRouteStatus = async (route) => {
    setMessage('');
    try {
      if (route.is_blocked) {
        await api.patch(`/admin/routes/${route.id}/unblock`);
        setMessage('Route unblocked.');
      } else {
        await api.patch(`/admin/routes/${route.id}/block`, null, {
          params: { reason: routeReason[route.id] || 'Marked by admin' },
        });
        setMessage('Route blocked.');
      }
      refreshAdminData();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to update route status.');
    }
  };

  const handleDeleteRoute = async (routeId) => {
    setMessage('');
    try {
      await mapService.deleteRoute(routeId);
      setMessage('Route removed.');
      refreshAdminData();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to remove route.');
    }
  };

  const handleCrowdChange = async (route, crowdednessScore) => {
    setMessage('');
    try {
      await mapService.updateRoute(route.id, {
        crowdedness_score: Number(crowdednessScore),
      });
      setMessage('Admin crowd severity updated. Live crowd also includes app check-ins and weather.');
      refreshAdminData();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Unable to update crowdedness.');
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-950">Admin dashboard</h1>
          <p className="mt-1 text-gray-600">Manage campus locations and live route conditions.</p>
        </div>
        <button
          onClick={refreshAdminData}
          className="rounded border border-gray-300 bg-white px-4 py-2 font-semibold text-gray-800 hover:bg-gray-50"
        >
          Refresh
        </button>
      </div>

      {message && (
        <div className="rounded border border-blue-200 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-800">
          {message}
        </div>
      )}

      {statistics && (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-6">
          <StatCard label="Locations" value={statistics.total_locations} />
          <StatCard label="Routes" value={statistics.total_routes} />
          <StatCard label="Active" value={statistics.active_routes} />
          <StatCard label="Blocked" value={statistics.blocked_routes} danger />
          <StatCard label="Users" value={statistics.total_users} />
          <StatCard label="Admins" value={statistics.admin_users} />
        </div>
      )}

      {signals && (
        <div className="grid gap-3 md:grid-cols-3">
          {/* <StatCard label="Campus" value="IIT Roorkee" /> */}
          {/* <StatCard label="Live users" value={signals.active_presence} /> */}
          {/* <StatCard label="Weather" value={signals.weather?.condition || 'auto'} /> */}
        </div>
      )}

      <div className="flex gap-2 border-b border-gray-200">
        {['routes', 'locations', 'map'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-3 font-semibold capitalize ${
              activeTab === tab
                ? 'border-b-2 border-blue-600 text-blue-700'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'routes' && (
        <div className="space-y-5">
        <form onSubmit={handleCreateRoute} className="rounded border border-gray-200 bg-white p-4 shadow-sm">
          <div className="mb-4 flex flex-col justify-between gap-2 md:flex-row md:items-center">
            <div>
              <h2 className="text-lg font-bold text-gray-950">Add route</h2>
              <p className="text-sm text-gray-600">Use the map tab in route mode, or choose two locations here.</p>
            </div>
            <button
              type="button"
              onClick={startRouteMapSelection}
              className="rounded border border-blue-200 px-3 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-50"
            >
              Select on map
            </button>
          </div>
          <div className="grid gap-3 md:grid-cols-4">
            <SelectInput label="Start" value={routeForm.source_id} onChange={(value) => setRouteForm({ ...routeForm, source_id: value })} locations={locations} />
            <SelectInput label="End" value={routeForm.destination_id} onChange={(value) => setRouteForm({ ...routeForm, destination_id: value })} locations={locations} />
            <TextInput label="Distance meters" value={routeForm.distance} onChange={(value) => setRouteForm({ ...routeForm, distance: value })} required />
            <TextInput label="Walking seconds" value={routeForm.walking_time} onChange={(value) => setRouteForm({ ...routeForm, walking_time: value })} required />
            <OptionInput label="Type" value={routeForm.route_type} onChange={(value) => setRouteForm({ ...routeForm, route_type: value })} options={routeTypes} />
            <CrowdInput label="Crowd" value={routeForm.crowdedness_score} onChange={(value) => setRouteForm({ ...routeForm, crowdedness_score: value })} />
            <TextInput label="Status reason" value={routeForm.blocked_reason} onChange={(value) => setRouteForm({ ...routeForm, blocked_reason: value })} />
            <label className="mt-6 flex items-center gap-2 text-sm font-semibold text-gray-700">
              <input
                type="checkbox"
                checked={routeForm.is_blocked}
                onChange={(event) => setRouteForm({ ...routeForm, is_blocked: event.target.checked })}
              />
              Blocked
            </label>
          </div>
          <button className="mt-4 rounded bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-700">
            Add route
          </button>
        </form>

        <div className="overflow-x-auto rounded border border-gray-200 bg-white shadow-sm">
          <table className="w-full min-w-[760px] text-sm">
            <thead className="bg-gray-50 text-left text-gray-600">
              <tr>
                <th className="px-4 py-3">Route</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Crowd</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Reason</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {routes.map((route) => (
                <tr key={route.id} className="border-t border-gray-100">
                  <td className="px-4 py-3 font-semibold text-gray-900">
                    {locationsById.get(route.source_id)?.name || route.source_id}
                    <span className="text-gray-400"> to </span>
                    {locationsById.get(route.destination_id)?.name || route.destination_id}
                  </td>
                  <td className="px-4 py-3">{route.route_type}</td>
                  <td className="px-4 py-3">
                    <select
                      value={route.crowdedness_score >= 0.66 ? 0.8 : route.crowdedness_score >= 0.33 ? 0.5 : 0.15}
                      onChange={(event) => handleCrowdChange(route, event.target.value)}
                      className="rounded border border-gray-300 px-2 py-1"
                    >
                      <option value={0.15}>Low</option>
                      <option value={0.5}>Crowded</option>
                      <option value={0.8}>Very crowded</option>
                    </select>
                    <p className="mt-1 text-xs text-gray-500">
                      Live: {signals?.routes?.[route.id]?.crowdedness_level?.replace('_', ' ') || 'loading'}
                      {signals?.routes?.[route.id]?.presence_count ? `, ${signals.routes[route.id].presence_count} users nearby` : ''}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`rounded px-2 py-1 text-xs font-bold ${route.is_blocked ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {route.is_blocked ? 'Blocked' : 'Open'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <input
                      value={routeReason[route.id] ?? route.blocked_reason ?? ''}
                      onChange={(event) => setRouteReason({ ...routeReason, [route.id]: event.target.value })}
                      placeholder="Reason"
                      className="w-44 rounded border border-gray-300 px-2 py-1"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => handleRouteStatus(route)}
                      className={`rounded px-3 py-2 font-semibold text-white ${route.is_blocked ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-red-600 hover:bg-red-700'}`}
                    >
                      {route.is_blocked ? 'Unblock' : 'Block'}
                    </button>
                    <button
                      onClick={() => handleDeleteRoute(route.id)}
                      className="rounded border border-red-200 px-3 py-2 font-semibold text-red-700 hover:bg-red-50"
                    >
                      Remove
                    </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </div>
      )}

      {activeTab === 'locations' && (
        <div className="grid gap-5 lg:grid-cols-[360px_minmax(0,1fr)]">
          <form onSubmit={handleSaveLocation} className="rounded border border-gray-200 bg-white p-4 shadow-sm">
            <div className="mb-4 flex items-center justify-between gap-2">
              <h2 className="text-lg font-bold text-gray-950">{editingLocationId ? 'Update location' : 'Add location'}</h2>
              <button
                type="button"
                onClick={startLocationMapSelection}
                className="rounded border border-blue-200 px-3 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-50"
              >
                Select on map
              </button>
            </div>
            <div className="space-y-3">
              <TextInput label="Name" value={locationForm.name} onChange={(value) => setLocationForm({ ...locationForm, name: value })} required />
              <TextInput label="Category" value={locationForm.category} onChange={(value) => setLocationForm({ ...locationForm, category: value })} required />
              <TextInput label="Latitude" value={locationForm.latitude} onChange={(value) => setLocationForm({ ...locationForm, latitude: value })} required />
              <TextInput label="Longitude" value={locationForm.longitude} onChange={(value) => setLocationForm({ ...locationForm, longitude: value })} required />
              <TextInput label="Accessibility score" value={locationForm.accessibility_score} onChange={(value) => setLocationForm({ ...locationForm, accessibility_score: value })} />
              <label className="block">
                <span className="mb-1 block text-sm font-semibold text-gray-700">Description</span>
                <textarea
                  value={locationForm.description}
                  onChange={(event) => setLocationForm({ ...locationForm, description: event.target.value })}
                  className="h-24 w-full rounded border border-gray-300 px-3 py-2"
                />
              </label>
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <input
                  type="checkbox"
                  checked={locationForm.is_accessible}
                  onChange={(event) => setLocationForm({ ...locationForm, is_accessible: event.target.checked })}
                />
                Accessible
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button className="rounded bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-700">
                  {editingLocationId ? 'Save changes' : 'Add location'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setEditingLocationId(null);
                    setLocationForm(emptyLocation);
                  }}
                  className="rounded border border-gray-300 bg-white px-4 py-3 font-semibold text-gray-800 hover:bg-gray-50"
                >
                  Clear
                </button>
              </div>
            </div>
          </form>

          <div className="overflow-hidden rounded border border-gray-200 bg-white shadow-sm">
            {locations.map((location) => (
              <div key={location.id} className="flex items-center justify-between gap-3 border-b border-gray-100 px-4 py-3 last:border-b-0">
                <div>
                  <p className="font-bold text-gray-950">{location.name}</p>
                  <p className="text-sm text-gray-500">{location.category}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEditLocation(location)}
                    className="rounded border border-blue-200 px-3 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-50"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteLocation(location.id)}
                    className="rounded border border-red-200 px-3 py-2 text-sm font-semibold text-red-700 hover:bg-red-50"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'map' && (
        <div className="grid gap-5 lg:grid-cols-[320px_minmax(0,1fr)]">
          <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
            <h2 className="text-lg font-bold text-gray-950">Map selection</h2>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <button
                onClick={() => {
                  setMapMode('location');
                  setMessage('Click the map to fill latitude and longitude for the location form.');
                }}
                className={`rounded border px-3 py-2 text-sm font-semibold ${mapMode === 'location' ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-700'}`}
              >
                Location point
              </button>
              <button
                onClick={() => {
                  setMapMode('route');
                  setMessage('Click two existing markers to select route endpoints.');
                }}
                className={`rounded border px-3 py-2 text-sm font-semibold ${mapMode === 'route' ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-700'}`}
              >
                Route endpoints
              </button>
            </div>
            <p className="mt-3 text-sm text-gray-600">
              {mapMode === 'location'
                ? 'Click anywhere on the map to fill latitude and longitude in the location form.'
                : 'Click two existing markers to fill the route start and end fields.'}
            </p>
            {routeForm.source_id && (
              <div className="mt-3 rounded bg-gray-50 p-3 text-sm font-semibold text-gray-700">
                Start: {locationsById.get(Number(routeForm.source_id))?.name || 'selected'}
                <br />
                End: {locationsById.get(Number(routeForm.destination_id))?.name || 'not selected'}
              </div>
            )}
            {mapMode === 'route' && (
              <button
                type="button"
                onClick={() => {
                  setActiveTab('routes');
                  setMessage('Route endpoints selected. Add type, crowd, status, and reason before saving.');
                }}
                className="mt-3 w-full rounded bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-700"
              >
                Continue route details
              </button>
            )}
          </div>
          <div className="h-[620px] overflow-hidden rounded border border-gray-200 bg-white shadow-sm">
            <MapComponent
              locations={locations}
              onMapClick={handleAdminMapClick}
              onLocationClick={handleAdminLocationClick}
            />
          </div>
        </div>
      )}

      {loading && <div className="text-center text-sm font-semibold text-gray-500">Loading...</div>}
    </div>
  );
};

const StatCard = ({ label, value, danger = false }) => (
  <div className={`rounded border p-4 ${danger ? 'border-red-200 bg-red-50' : 'border-blue-100 bg-blue-50'}`}>
    <p className="text-xs font-semibold uppercase text-gray-600">{label}</p>
    <p className={`mt-1 text-2xl font-bold ${danger ? 'text-red-700' : 'text-blue-700'}`}>{value}</p>
  </div>
);

const TextInput = ({ label, value, onChange, required = false }) => (
  <label className="block">
    <span className="mb-1 block text-sm font-semibold text-gray-700">{label}</span>
    <input
      value={value}
      onChange={(event) => onChange(event.target.value)}
      required={required}
      className="w-full rounded border border-gray-300 px-3 py-2"
    />
  </label>
);

const SelectInput = ({ label, value, onChange, locations }) => (
  <label className="block">
    <span className="mb-1 block text-sm font-semibold text-gray-700">{label}</span>
    <select
      value={value}
      onChange={(event) => onChange(event.target.value)}
      required
      className="w-full rounded border border-gray-300 px-3 py-2"
    >
      <option value="">Choose location</option>
      {locations.map((location) => (
        <option key={location.id} value={location.id}>
          {location.name}
        </option>
      ))}
    </select>
  </label>
);

const OptionInput = ({ label, value, onChange, options }) => (
  <label className="block">
    <span className="mb-1 block text-sm font-semibold text-gray-700">{label}</span>
    <select
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="w-full rounded border border-gray-300 px-3 py-2"
    >
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  </label>
);

const CrowdInput = ({ label, value, onChange }) => (
  <label className="block">
    <span className="mb-1 block text-sm font-semibold text-gray-700">{label}</span>
    <select
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="w-full rounded border border-gray-300 px-3 py-2"
    >
      {crowdLevels.map((level) => (
        <option key={level.value} value={level.value}>
          {level.label}
        </option>
      ))}
    </select>
  </label>
);

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

export default AdminPanel;
