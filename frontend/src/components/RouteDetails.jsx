/**
 * RouteDetails Component
 */
import React from 'react';

export const RouteDetails = ({ route = null, loading = false }) => {
  if (!route) {
    return (
      <div className="rounded border border-gray-200 bg-white p-4 text-center text-gray-500">
        Select a route to see details.
      </div>
    );
  }

  const distanceKm = route.distance ? (route.distance / 1000).toFixed(2) : null;
  const crowdScore = Number(route.crowdedness_score || 0);
  const etaText = route.eta_formatted || (route.walking_time ? `${Math.round(route.walking_time / 60)} min` : 'Pending');

  return (
    <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-950">Route details</h3>
        {loading && <span className="text-sm font-semibold text-gray-500">Loading...</span>}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Metric label="Source" value={route.source || 'Selected start'} />
        <Metric label="Destination" value={route.destination || 'Selected end'} />
        <Metric label="Distance" value={distanceKm ? `${distanceKm} km` : 'Unknown'} emphasis />
        <Metric label="ETA" value={etaText} emphasis />
        <Metric label="Mode" value={(route.mode || 'route').replace('_', ' ')} />
        <Metric label="Algorithm" value={route.algorithm || 'Calculated'} />
      </div>

      <div className="mt-4">
        <div className="mb-1 flex justify-between text-sm font-semibold text-gray-700">
          <span>Crowd level</span>
          <span className="capitalize">{route.crowdedness_level || 'low'}</span>
        </div>
        <div className="h-2 rounded-full bg-gray-200">
          <div
            className="h-2 rounded-full bg-amber-500"
            style={{ width: `${Math.min(100, Math.max(0, crowdScore * 100))}%` }}
          />
        </div>
      </div>

      <div className="mt-4 rounded bg-gray-50 p-3 text-sm text-gray-700">
        {route.num_stops ?? Math.max((route.path?.length || 1) - 1, 0)} stops
        {route.eta_confidence ? `, ${Math.round(route.eta_confidence * 100)}% ETA confidence` : ''}
        {route.signals ? (
          <span>
            {`, ${route.signals.weather?.condition || 'clear'} weather`}
            {route.personalized_via ? `, personalized via ${route.personalized_via}` : ''}
          </span>
        ) : null}
      </div>
    </div>
  );
};

const Metric = ({ label, value, emphasis = false }) => (
  <div className="rounded border border-gray-100 bg-white p-3">
    <p className="text-xs font-semibold uppercase text-gray-500">{label}</p>
    <p className={`mt-1 break-words ${emphasis ? 'text-lg font-bold text-blue-700' : 'font-semibold text-gray-900'}`}>
      {value}
    </p>
  </div>
);

export default RouteDetails;
