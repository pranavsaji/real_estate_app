// src/pages/BrokerDetails.js

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useLocation, useNavigate } from 'react-router-dom';

const BrokerDetails = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [brokers, setBrokers] = useState([]);
  const [error, setError] = useState('');

  // Helper function to parse query parameters
  const useQuery = () => {
    return new URLSearchParams(location.search);
  };

  const query = useQuery();
  const zipCode = query.get('zip_code');

  useEffect(() => {
    if (zipCode) {
      fetchBrokers(zipCode);
    } else {
      setError('No zip code provided.');
    }
  }, [zipCode]);

  const fetchBrokers = async (zip) => {
    try {
      const response = await axios.get(`/api/get_broker_details`, {
        params: { zip_code: zip },
      });

      if (response.data && response.data.brokers) {
        setBrokers(response.data.brokers);
      } else {
        setError('No brokers found for the provided zip code.');
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else if (err.response && err.response.data && err.response.data.message) {
        setError(err.response.data.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    }
  };

  const handleBack = () => {
    navigate('/results');
  };

  return (
    <div className="brokers-container">
      <h1>Brokers in Zip Code: {zipCode}</h1>

      {error && <p className="error-message">{error}</p>}

      {brokers.length > 0 ? (
        <>
          <table>
            <thead>
              <tr>
                <th>Broker Name</th>
                <th>City</th>
                <th>State</th>
                <th>Zip Code</th>
                <th>Reviews</th>
                <th>Recent Homes Sold</th>
                <th>Negotiations Done</th>
                <th>Years of Experience</th>
                <th>Rating</th>
              </tr>
            </thead>
            <tbody>
              {brokers.map((broker, index) => (
                <tr key={index}>
                  <td>{broker['Broker Name']}</td>
                  <td>{broker.City}</td>
                  <td>{broker.State}</td>
                  <td>{broker['Zip Code']}</td>
                  <td>{broker.Reviews}</td>
                  <td>{broker['Recent Homes Sold']}</td>
                  <td>{broker['Negotiations Done']}</td>
                  <td>{broker['Years of Experience']}</td>
                  <td>{broker.Rating}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : (
        !error && <p>No brokers found for this zip code.</p>
      )}

      {/* Back Button */}
      <button
        className="mt-4 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
        onClick={handleBack}
      >
        &larr; Back to Results
      </button>
    </div>
  );
};

export default BrokerDetails;

// // src/pages/BrokerDetails.js

// import React, { useEffect, useState } from 'react';
// import axios from 'axios';
// import { useLocation } from 'react-router-dom';

// const BrokerDetails = () => {
//   const location = useLocation();
//   const [brokers, setBrokers] = useState([]);
//   const [error, setError] = useState('');

//   // Helper function to parse query parameters
//   const useQuery = () => {
//     return new URLSearchParams(location.search);
//   };

//   const query = useQuery();
//   const zipCode = query.get('zip_code');

//   useEffect(() => {
//     if (zipCode) {
//       fetchBrokers(zipCode);
//     } else {
//       setError('No zip code provided.');
//     }
//   }, [zipCode]);

//   const fetchBrokers = async (zip) => {
//     try {
//       const response = await axios.get(`/api/get_broker_details`, {
//         params: { zip_code: zip },
//       });

//       if (response.data && response.data.brokers) {
//         setBrokers(response.data.brokers);
//       } else {
//         setError('No brokers found for the provided zip code.');
//       }
//     } catch (err) {
//       console.error(err);
//       if (err.response && err.response.data && err.response.data.error) {
//         setError(err.response.data.error);
//       } else if (err.response && err.response.data && err.response.data.message) {
//         setError(err.response.data.message);
//       } else {
//         setError('An unexpected error occurred. Please try again.');
//       }
//     }
//   };

//   return (
//     <div className="brokers-container">
//       <h1>Brokers in Zip Code: {zipCode}</h1>

//       {error && <p className="error-message">{error}</p>}

//       {brokers.length > 0 ? (
//         <table>
//           <thead>
//             <tr>
//               <th>Broker Name</th>
//               <th>City</th>
//               <th>State</th>
//               <th>Zip Code</th>
//               <th>Reviews</th>
//               <th>Recent Homes Sold</th>
//               <th>Negotiations Done</th>
//               <th>Years of Experience</th>
//               <th>Rating</th>
//             </tr>
//           </thead>
//           <tbody>
//             {brokers.map((broker, index) => (
//               <tr key={index}>
//                 <td>{broker['Broker Name']}</td>
//                 <td>{broker.City}</td>
//                 <td>{broker.State}</td>
//                 <td>{broker['Zip Code']}</td>
//                 <td>{broker.Reviews}</td>
//                 <td>{broker['Recent Homes Sold']}</td>
//                 <td>{broker['Negotiations Done']}</td>
//                 <td>{broker['Years of Experience']}</td>
//                 <td>{broker.Rating}</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       ) : (
//         !error && <p>No brokers found for this zip code.</p>
//       )}
//     </div>
//   );
// };

// export default BrokerDetails;
