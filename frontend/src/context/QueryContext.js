// src/context/QueryContext.js

import React, { createContext, useState } from 'react';

export const QueryContext = createContext();

export const QueryProvider = ({ children }) => {
  const [query, setQuery] = useState('');
  const [userIntent, setUserIntent] = useState('');
  const [traits, setTraits] = useState([]);
  const [keyPhrases, setKeyPhrases] = useState([]);
  const [propertyKeywords, setPropertyKeywords] = useState('');
  const [sqlQuery, setSqlQuery] = useState('');
  const [results, setResults] = useState([]);
  const [dynamicColumns, setDynamicColumns] = useState([]);

  // Add a state variable to trigger refresh of saved searches
  const [refreshSavedSearches, setRefreshSavedSearches] = useState(false);

  const triggerRefreshSavedSearches = () => {
    setRefreshSavedSearches((prev) => !prev);
  };

  // Function to set context from a saved search response
  const setContextFromSavedSearch = (savedResponse) => {
    setQuery(savedResponse.query || '');
    setUserIntent(savedResponse.user_intent || '');
    setTraits(savedResponse.traits || []);
    setKeyPhrases(savedResponse.key_phrases || []);
    setPropertyKeywords(savedResponse.property_keywords || '');
    setSqlQuery(savedResponse.sql_query || '');
    setResults(savedResponse.result || []);
    setDynamicColumns(savedResponse.dynamic_columns || []);
  };

  return (
    <QueryContext.Provider
      value={{
        query,
        setQuery,
        userIntent,
        setUserIntent,
        traits,
        setTraits,
        keyPhrases,
        setKeyPhrases,
        propertyKeywords,
        setPropertyKeywords,
        sqlQuery,
        setSqlQuery,
        results,
        setResults,
        dynamicColumns,
        setDynamicColumns,
        refreshSavedSearches,
        triggerRefreshSavedSearches,
        setContextFromSavedSearch,
      }}
    >
      {children}
    </QueryContext.Provider>
  );
};


// // src/context/QueryContext.js

// import React, { createContext, useState } from 'react';

// export const QueryContext = createContext();

// export const QueryProvider = ({ children }) => {
//   const [query, setQuery] = useState('');
//   const [userIntent, setUserIntent] = useState('');
//   const [traits, setTraits] = useState([]);
//   const [keyPhrases, setKeyPhrases] = useState([]);
//   const [propertyKeywords, setPropertyKeywords] = useState('');
//   const [sqlQuery, setSqlQuery] = useState('');
//   const [results, setResults] = useState([]);
//   const [dynamicColumns, setDynamicColumns] = useState([]);

//   // Add a state variable to trigger refresh of saved searches
//   const [refreshSavedSearches, setRefreshSavedSearches] = useState(false);

//   const triggerRefreshSavedSearches = () => {
//     setRefreshSavedSearches((prev) => !prev);
//   };

//   return (
//     <QueryContext.Provider
//       value={{
//         query,
//         setQuery,
//         userIntent,
//         setUserIntent,
//         traits,
//         setTraits,
//         keyPhrases,
//         setKeyPhrases,
//         propertyKeywords,
//         setPropertyKeywords,
//         sqlQuery,
//         setSqlQuery,
//         results,
//         setResults,
//         dynamicColumns,
//         setDynamicColumns,
//         refreshSavedSearches,
//         triggerRefreshSavedSearches,
//       }}
//     >
//       {children}
//     </QueryContext.Provider>
//   );
// };

