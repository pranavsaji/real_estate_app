// src/components/SavedSearches.js

import React, { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import './SavedSearches.css'; // Import CSS for styling
import { QueryContext } from '../context/QueryContext';
import axios from 'axios';

const SavedSearches = () => {
  const [savedSearches, setSavedSearches] = useState([]);
  const navigate = useNavigate();
  const {
    setContextFromSavedSearch,
    refreshSavedSearches, // To listen for refresh triggers
    triggerRefreshSavedSearches,
  } = useContext(QueryContext);

  useEffect(() => {
    // Fetch saved searches from the backend when component mounts or refreshSavedSearches changes
    fetchSavedSearches();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshSavedSearches]); // Depend on refreshSavedSearches

  const fetchSavedSearches = async () => {
    try {
      console.log('Fetching saved searches from backend...');
      const response = await axios.get('/api/get_saved_searches');
      if (response.data && response.data.saved_searches) {
        setSavedSearches(response.data.saved_searches);
        console.log('Saved Searches Retrieved:', response.data.saved_searches);
      } else {
        console.log('No saved searches found.');
        setSavedSearches([]);
      }
    } catch (error) {
      console.error('Error fetching saved searches:', error);
      alert('Failed to fetch saved searches.');
    }
  };

  const handleSelectSearch = (searchEntry) => {
    try {
      console.log(`Loading saved search: "${searchEntry.search}"`);
      // Set the context using the saved response
      setContextFromSavedSearch(searchEntry.response);
      console.log('Context Updated from Saved Search:', searchEntry.response);
      // Navigate to the Results page immediately without delay
      navigate('/results');
    } catch (error) {
      console.error('Error loading saved search:', error);
      alert('Failed to load the saved search. Please try again.');
    }
  };

  const handleDeleteSearch = async (search) => {
    try {
      console.log(`Deleting search: "${search}"`);
      const response = await axios.post('/api/delete_saved_search', { search });
      if (response.data && response.data.message) {
        alert(response.data.message);
        // Trigger refresh to update the saved searches list
        triggerRefreshSavedSearches();
      } else if (response.data && response.data.error) {
        alert(response.data.error);
      }
    } catch (error) {
      console.error('Error deleting search:', error);
      alert('Failed to delete the search.');
    }
  };

  const handleClearAll = async () => {
    if (window.confirm('Are you sure you want to delete all saved searches?')) {
      try {
        console.log('Clearing all saved searches...');
        const response = await axios.post('/api/clear_saved_searches');
        if (response.data && response.data.message) {
          alert(response.data.message);
          setSavedSearches([]);
        } else if (response.data && response.data.error) {
          alert(response.data.error);
        }
      } catch (error) {
        console.error('Error clearing saved searches:', error);
        alert('Failed to clear saved searches.');
      }
    }
  };

  return (
    <div className="saved-searches">
      <h2>Saved Searches</h2>
      {savedSearches.length === 0 ? (
        <p>No saved searches.</p>
      ) : (
        <>
          <ul>
            {savedSearches.map((entry, index) => (
              <li key={index} className="saved-search-item">
                <button
                  onClick={() => handleSelectSearch(entry)}
                  className="search-btn"
                >
                  {entry.search}
                </button>
                <button
                  className="delete-btn"
                  onClick={() => handleDeleteSearch(entry.search)}
                  title={`Delete "${entry.search}"`}
                >
                  &times;
                </button>
              </li>
            ))}
          </ul>
          <button className="clear-all-btn" onClick={handleClearAll}>
            Clear All
          </button>
        </>
      )}
    </div>
  );
};

export default SavedSearches;

