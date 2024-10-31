// src/pages/Information.js

import React, { useContext, useEffect } from 'react';
import { QueryContext } from '../context/QueryContext';
import { Link, useNavigate } from 'react-router-dom';
import InformationContent from '../components/InformationContent';

const Information = () => {
  const { userIntent, traits, keyPhrases, propertyKeywords, sqlQuery } = useContext(QueryContext);
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/results');
    }, 3000); // 3 seconds delay

    return () => clearTimeout(timer); // Cleanup on unmount
  }, [navigate]);

  return (
    <div className="max-w-4xl mx-auto">
      <InformationContent />

      <div className="flex space-x-4">
        <Link
          to="/results"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          View Results
        </Link>
        <Link
          to="/save-to-txt"
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
        >
          Save to TXT
        </Link>
      </div>

      {/* Optional: Show message about automatic redirection */}
      <p className="mt-4 text-gray-500 text-sm">Redirecting to results in 3 seconds...</p>
    </div>
  );
};

export default Information;

// // src/pages/Information.js

// import React, { useContext } from 'react';
// import { QueryContext } from '../context/QueryContext';
// import { Link } from 'react-router-dom';

// const Information = () => {
//   const { userIntent, traits, keyPhrases, propertyKeywords, sqlQuery } = useContext(QueryContext);

//   return (
//     <div className="max-w-4xl mx-auto">
//       <h1 className="text-2xl font-bold mb-4">Extracted Information</h1>

//       <section className="mb-6">
//         <h2 className="text-xl font-semibold">User Intent</h2>
//         <p className="mt-2">{userIntent}</p>
//       </section>

//       <section className="mb-6">
//         <h2 className="text-xl font-semibold">Traits</h2>
//         <ul className="list-disc list-inside mt-2">
//           {traits.map((trait, index) => (
//             <li key={index}>{trait}</li>
//           ))}
//         </ul>
//       </section>

//       <section className="mb-6">
//         <h2 className="text-xl font-semibold">Key Phrases</h2>
//         <ul className="list-disc list-inside mt-2">
//           {keyPhrases.map((phrase, index) => (
//             <li key={index}>{phrase}</li>
//           ))}
//         </ul>
//       </section>

//       <section className="mb-6">
//         <h2 className="text-xl font-semibold">Property Keywords</h2>
//         <p className="mt-2">{propertyKeywords}</p>
//       </section>

//       <section className="mb-6">
//         <h2 className="text-xl font-semibold">Generated SQL Query</h2>
//         <pre className="bg-gray-100 p-2 rounded mt-2">{sqlQuery}</pre>
//       </section>

//       <div className="flex space-x-4">
//         <Link
//           to="/results"
//           className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
//         >
//           View Results
//         </Link>
//         <Link
//           to="/save-to-txt"
//           className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
//         >
//           Save to TXT
//         </Link>
//       </div>
//     </div>
//   );
// };

// export default Information;

