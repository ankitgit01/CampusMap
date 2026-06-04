/**
 * SearchBar Component
 */
import React, { useEffect, useState } from 'react';
import { mapService } from '../services/mapService';

export const SearchBar = ({
  onSearch = null,
  onLocationSelect = null,
  placeholder = 'Search locations...',
  value = '',
  onChange = null,
  rightSlot = null,
  resetSearchKey = 0,
}) => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [hasUserTyped, setHasUserTyped] = useState(false);

  useEffect(() => {
    setHasUserTyped(false);
    setShowResults(false);
    setResults([]);
  }, [resetSearchKey]);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (hasUserTyped && value.trim().length > 1) {
        handleSearch(value.trim());
      } else {
        setResults([]);
        setShowResults(false);
      }
    }, 250);

    return () => clearTimeout(debounceTimer);
  }, [value, hasUserTyped]);

  const handleSearch = async (searchTerm = value) => {
    setIsLoading(true);
    onSearch?.(searchTerm);

    try {
      const response = await mapService.searchLocations(searchTerm, null, 10);
      setResults(response.results || []);
      setShowResults(true);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
      setShowResults(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLocationClick = (location) => {
    setHasUserTyped(false);
    setShowResults(false);
    onChange?.(location.name);
    onLocationSelect?.(location);
  };

  return (
    <div className="relative w-full">
      <div className="flex h-11 items-center overflow-hidden rounded border border-gray-300 bg-white shadow-sm focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100">
        <input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(event) => {
            setHasUserTyped(true);
            onChange?.(event.target.value);
          }}
          className="min-w-0 flex-1 px-3 py-2 outline-none"
        />

        {isLoading && (
          <span className="px-3 text-sm text-gray-500">
            ...
          </span>
        )}
        {rightSlot && <div className="flex items-center pr-2">{rightSlot}</div>}
      </div>

      {showResults && results.length > 0 && (
        <div className="absolute left-0 right-0 top-full z-[1000] mt-1 max-h-80 overflow-y-auto rounded border border-gray-200 bg-white shadow-lg">
          {results.map((location) => (
            <button
              key={location.id}
              onClick={() => handleLocationClick(location)}
              className="w-full border-b px-4 py-3 text-left last:border-b-0 hover:bg-blue-50"
            >
              <div className="font-semibold text-gray-900">
                {location.name}
              </div>

              <div className="text-sm text-gray-500">
                {location.category}
              </div>

              {location.description && (
                <div className="mt-1 line-clamp-2 text-xs text-gray-500">
                  {location.description}
                </div>
              )}
            </button>
          ))}
        </div>
      )}

      {showResults && value && results.length === 0 && !isLoading && (
        <div className="absolute left-0 right-0 top-full z-[1000] mt-1 rounded border border-gray-200 bg-white p-4 text-center text-sm text-gray-500 shadow-lg">
          No locations found
        </div>
      )}
    </div>
  );
};

export default SearchBar;
