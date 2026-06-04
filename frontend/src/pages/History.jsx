/**
 * History Page
 */
import React, { useState, useEffect } from 'react';
import NavBar from '../components/NavBar';
import api from '../services/api';

const History = () => {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
    fetchStats();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await api.get('/history/user');
      setHistory(response.data.history || []);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/history/statistics');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <NavBar />

      <div className="mx-auto max-w-7xl px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-950">Navigation history</h1>
          <p className="mt-1 text-gray-600">
            Routes you search are saved here and frequent locations help personalize the best route option.
          </p>
        </div>

        {stats && (
          <div className="mb-6 grid gap-4 md:grid-cols-3">
            <StatCard label="Total Navigations" value={stats.total_navigations} />
            <StatCard label="Distance Traveled" value={`${(stats.total_distance_meters / 1000).toFixed(1)} km`} />
            <StatCard label="Most Visited" value={stats.most_visited || '-'} />
          </div>
        )}

        {stats?.frequent_locations?.length > 0 && (
          <div className="mb-6 rounded border border-gray-200 bg-white p-4 shadow-sm">
            <h2 className="mb-3 text-lg font-bold text-gray-950">Frequently visited</h2>
            <div className="grid gap-2 md:grid-cols-4">
              {stats.frequent_locations.map((item) => (
                <div key={item.location} className="rounded border border-blue-100 bg-blue-50 px-3 py-2">
                  <p className="truncate font-semibold text-blue-950">{item.location}</p>
                  <p className="text-sm text-blue-700">{item.visits} visit{item.visits === 1 ? '' : 's'}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading ? (
          <div className="py-8 text-center text-gray-500">Loading history...</div>
        ) : history.length > 0 ? (
          <div className="overflow-x-auto rounded border border-gray-200 bg-white shadow-sm">
            <table className="w-full min-w-[760px]">
              <thead className="bg-gray-50 text-left text-gray-600">
                <tr>
                  <th className="px-6 py-3 font-semibold">Date</th>
                  <th className="px-6 py-3 font-semibold">From</th>
                  <th className="px-6 py-3 font-semibold">To</th>
                  <th className="px-6 py-3 font-semibold">Mode</th>
                  <th className="px-6 py-3 font-semibold">Distance</th>
                  <th className="px-6 py-3 font-semibold">ETA</th>
                </tr>
              </thead>
              <tbody>
                {history.map((entry) => (
                  <tr key={entry.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm">
                      {new Date(entry.timestamp).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 font-semibold">{entry.source}</td>
                    <td className="px-6 py-4 font-semibold">{entry.destination}</td>
                    <td className="px-6 py-4">
                      <span className="inline-block rounded bg-blue-100 px-3 py-1 text-sm font-semibold capitalize text-blue-800">
                        {entry.mode?.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {(entry.distance / 1000).toFixed(2)} km
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {formatTime(entry.estimated_time)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="rounded border border-gray-200 bg-white p-8 text-center text-gray-500 shadow-sm">
            No navigation history yet. Start navigating!
          </div>
        )}
      </div>
    </div>
  );
};

const StatCard = ({ label, value }) => (
  <div className="rounded border border-blue-100 bg-white p-6 shadow-sm">
    <p className="text-sm font-semibold text-gray-600">{label}</p>
    <p className="mt-2 truncate text-2xl font-bold text-blue-700">{value}</p>
  </div>
);

function formatTime(seconds) {
  if (!seconds) return '0m';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
}

export default History;
