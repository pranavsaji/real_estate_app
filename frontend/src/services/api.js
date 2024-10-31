// src/services/api.js

import axios from 'axios';

// Base URL setup
const API_BASE_URL = '/api';

// Search API
export const searchProperties = async (query) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/search`, { query });
    return response.data;
  } catch (error) {
    console.error('Error in searchProperties:', error);
    throw error.response ? error.response.data : { error: 'Network Error' };
  }
};

// Get Broker Details API
export const getBrokerDetails = async (zipCode) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/get_broker_details`, {
      params: { zip_code: zipCode },
    });
    return response.data;
  } catch (error) {
    console.error('Error in getBrokerDetails:', error);
    throw error.response ? error.response.data : { error: 'Network Error' };
  }
};

// Save to TXT API
export const saveToTxt = async (data) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/save_to_txt`, data);
    return response.data;
  } catch (error) {
    console.error('Error in saveToTxt:', error);
    throw error.response ? error.response.data : { error: 'Network Error' };
  }
};

// Extract Information API (Optional)
export const extractInformation = async (query) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/extract_information`, { query });
    return response.data;
  } catch (error) {
    console.error('Error in extractInformation:', error);
    throw error.response ? error.response.data : { error: 'Network Error' };
  }
};

// New Endpoints for Saved Searches

// Save a search along with its response
export const saveSearch = async (search, response) => {
  try {
    const res = await axios.post(`${API_BASE_URL}/save_search`, { search, response });
    return res.data;
  } catch (error) {
    console.error('Error in saveSearch:', error);
    throw error.response ? error.response.data : { error: 'Network Error' };
  }
};

// Get saved searches
export const getSavedSearches = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/get_saved_searches`);
    return response.data;
  } catch (error) {
    console.error('Error in getSavedSearches:', error);
    throw error.response ? error.response.data : { error: 'Network Error' };
  }
};

// Delete a specific search
export const deleteSavedSearch = async (search) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/delete_saved_search`, { search });
    return response.data;
  } catch (error) {
    console.error('Error in deleteSavedSearch:', error);
    throw error.response ? error.response.data : { error: 'Network Error' };
  }
};

// Clear all saved searches
export const clearSavedSearches = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/clear_saved_searches`);
    return response.data;
  } catch (error) {
    console.error('Error in clearSavedSearches:', error);
    throw error.response ? error.response.data : { error: 'Network Error' };
  }
};


// // src/services/api.js

// import axios from 'axios';

// // Base URL setup
// const API_BASE_URL = '/api';

// // Search API
// export const searchProperties = async (query) => {
//   try {
//     const response = await axios.post(`${API_BASE_URL}/search`, { query });
//     return response.data;
//   } catch (error) {
//     console.error('Error in searchProperties:', error);
//     throw error.response ? error.response.data : { error: 'Network Error' };
//   }
// };

// // Get Broker Details API
// export const getBrokerDetails = async (zipCode) => {
//   try {
//     const response = await axios.get(`${API_BASE_URL}/get_broker_details`, {
//       params: { zip_code: zipCode },
//     });
//     return response.data;
//   } catch (error) {
//     console.error('Error in getBrokerDetails:', error);
//     throw error.response ? error.response.data : { error: 'Network Error' };
//   }
// };

// // Save to TXT API
// export const saveToTxt = async (data) => {
//   try {
//     const response = await axios.post(`${API_BASE_URL}/save_to_txt`, data);
//     return response.data;
//   } catch (error) {
//     console.error('Error in saveToTxt:', error);
//     throw error.response ? error.response.data : { error: 'Network Error' };
//   }
// };

// // Extract Information API (Optional)
// export const extractInformation = async (query) => {
//   try {
//     const response = await axios.post(`${API_BASE_URL}/extract_information`, { query });
//     return response.data;
//   } catch (error) {
//     console.error('Error in extractInformation:', error);
//     throw error.response ? error.response.data : { error: 'Network Error' };
//   }
// };

// // New Endpoints for Saved Searches

// // Save a search
// export const saveSearch = async (search) => {
//   try {
//     const response = await axios.post(`${API_BASE_URL}/save_search`, { search });
//     return response.data;
//   } catch (error) {
//     console.error('Error in saveSearch:', error);
//     throw error.response ? error.response.data : { error: 'Network Error' };
//   }
// };

// // Get saved searches
// export const getSavedSearches = async () => {
//   try {
//     const response = await axios.get(`${API_BASE_URL}/get_saved_searches`);
//     return response.data;
//   } catch (error) {
//     console.error('Error in getSavedSearches:', error);
//     throw error.response ? error.response.data : { error: 'Network Error' };
//   }
// };

// // Delete a specific search
// export const deleteSavedSearch = async (search) => {
//   try {
//     const response = await axios.post(`${API_BASE_URL}/delete_saved_search`, { search });
//     return response.data;
//   } catch (error) {
//     console.error('Error in deleteSavedSearch:', error);
//     throw error.response ? error.response.data : { error: 'Network Error' };
//   }
// };

// // Clear all saved searches
// export const clearSavedSearches = async () => {
//   try {
//     const response = await axios.post(`${API_BASE_URL}/clear_saved_searches`);
//     return response.data;
//   } catch (error) {
//     console.error('Error in clearSavedSearches:', error);
//     throw error.response ? error.response.data : { error: 'Network Error' };
//   }
// };
