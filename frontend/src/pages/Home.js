// src/pages/Home.js

import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { QueryContext } from '../context/QueryContext';
import { searchProperties } from '../services/api';
import axios from 'axios';

const Home = () => {
  const {
    setQuery,
    setUserIntent,
    setTraits,
    setKeyPhrases,
    setPropertyKeywords,
    setSqlQuery,
    setResults,
    setDynamicColumns,
    triggerRefreshSavedSearches, // Import the trigger function
  } = useContext(QueryContext);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) {
      alert('Please enter a valid query.');
      return;
    }

    setLoading(true);
    try {
      console.log(`Performing search for: "${input.trim()}"`);
      const data = await searchProperties(input.trim());

      if (data.error) {
        alert(data.error);
        setLoading(false);
        return;
      }

      // Update context with the received data
      setQuery(data.query);
      setUserIntent(data.user_intent);
      setTraits(data.traits);
      setKeyPhrases(data.key_phrases);
      setPropertyKeywords(data.property_keywords);
      setSqlQuery(data.sql_query);
      setResults(data.result);
      setDynamicColumns(data.dynamic_columns); // Set dynamic columns

      console.log('Context Updated:', {
        query: data.query,
        userIntent: data.user_intent,
        traits: data.traits,
        keyPhrases: data.key_phrases,
        propertyKeywords: data.property_keywords,
        sqlQuery: data.sql_query,
        results: data.result,
        dynamicColumns: data.dynamic_columns,
      });

      // Save the search and its response to the backend
      try {
        console.log(`Saving search: "${input.trim()}"`);
        const saveResponse = await axios.post('/api/save_search', {
          search: input.trim(),
          response: data, // Send the entire response object
        });
        if (saveResponse.data && saveResponse.data.message) {
          console.log(saveResponse.data.message);
          // Trigger a refresh of saved searches
          triggerRefreshSavedSearches();
        }
      } catch (saveError) {
        console.error('Error saving search:', saveError);
        // Optionally, alert the user or handle silently
      }

      // Navigate to the Information page after successful search
      navigate('/information');
    } catch (error) {
      console.error('Error fetching results:', error);
      alert('Failed to fetch results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-10">
      <h1 className="text-3xl font-bold mb-6 text-center">Real Estate Search</h1>
      <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
        <textarea
          className="p-3 border rounded-md resize-none"
          placeholder="Enter your real estate query..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={5}
          required
        />
        <button
          type="submit"
          className={`px-4 py-2 rounded-md text-white ${
            loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
          }`}
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
    </div>
  );
};

export default Home;


// // src/pages/Home.js

// import React, { useContext, useState } from 'react';
// import { useNavigate } from 'react-router-dom';
// import { QueryContext } from '../context/QueryContext';
// import { searchProperties } from '../services/api';
// import axios from 'axios';

// const Home = () => {
//   const {
//     setQuery,
//     setUserIntent,
//     setTraits,
//     setKeyPhrases,
//     setPropertyKeywords,
//     setSqlQuery,
//     setResults,
//     setDynamicColumns,
//     triggerRefreshSavedSearches, // Import the trigger function
//   } = useContext(QueryContext);

//   const [input, setInput] = useState('');
//   const [loading, setLoading] = useState(false);
//   const navigate = useNavigate();

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!input.trim()) {
//       alert('Please enter a valid query.');
//       return;
//     }

//     setLoading(true);
//     try {
//       console.log(`Performing search for: "${input.trim()}"`);
//       const data = await searchProperties(input.trim());

//       if (data.error) {
//         alert(data.error);
//         setLoading(false);
//         return;
//       }

//       // Update context with the received data
//       setQuery(data.query);
//       setUserIntent(data.user_intent);
//       setTraits(data.traits);
//       setKeyPhrases(data.key_phrases);
//       setPropertyKeywords(data.property_keywords);
//       setSqlQuery(data.sql_query);
//       setResults(data.result);
//       setDynamicColumns(data.dynamic_columns); // Set dynamic columns

//       console.log('Context Updated:', {
//         query: data.query,
//         userIntent: data.user_intent,
//         traits: data.traits,
//         keyPhrases: data.key_phrases,
//         propertyKeywords: data.property_keywords,
//         sqlQuery: data.sql_query,
//         results: data.result,
//         dynamicColumns: data.dynamic_columns,
//       });

//       // Save the search to the backend
//       try {
//         console.log(`Saving search: "${input.trim()}"`);
//         const saveResponse = await axios.post('/api/save_search', { search: input.trim() });
//         if (saveResponse.data && saveResponse.data.message) {
//           console.log(saveResponse.data.message);
//           // Trigger a refresh of saved searches
//           triggerRefreshSavedSearches();
//         }
//       } catch (saveError) {
//         console.error('Error saving search:', saveError);
//         // Optionally, alert the user or handle silently
//       }

//       // Navigate to the Information page after successful search
//       navigate('/information');
//     } catch (error) {
//       console.error('Error fetching results:', error);
//       alert('Failed to fetch results. Please try again.');
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="max-w-2xl mx-auto mt-10">
//       <h1 className="text-3xl font-bold mb-6 text-center">Real Estate Search</h1>
//       <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
//         <textarea
//           className="p-3 border rounded-md resize-none"
//           placeholder="Enter your real estate query..."
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           rows={5}
//           required
//         />
//         <button
//           type="submit"
//           className={`px-4 py-2 rounded-md text-white ${
//             loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
//           }`}
//           disabled={loading}
//         >
//           {loading ? 'Searching...' : 'Search'}
//         </button>
//       </form>
//     </div>
//   );
// };

// export default Home;

