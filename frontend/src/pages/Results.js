// src/pages/Results.js

import React, { useContext, useState } from 'react';
import './Results.css'; // Ensure this imports your CSS file
import { useNavigate } from 'react-router-dom';
import { QueryContext } from '../context/QueryContext';
import InformationContent from '../components/InformationContent';

const Results = () => {
  const navigate = useNavigate();
  const { results, dynamicColumns } = useContext(QueryContext);
  const [showThinking, setShowThinking] = useState(false);

  console.log('Results Data:', { results, dynamicColumns });

  // If results are still loading
  if (results.length === 0) {
    return <div className="results-container">No Results Found...</div>;
  }

  // Handler for viewing brokers
  const handleViewBrokers = (zipCode) => {
    navigate(`/broker-details?zip_code=${zipCode}`);
  };

  // Handler for receiving realtor proposal (Placeholder)
  const handleRealtorProposal = () => {
    alert('Realtor proposal has been sent!');
  };

  return (
    <div className="results-container">
      <h1>🏡 Search Results</h1>

      {/* Show Thinking Button */}
      <button
        className="bg-blue-500 text-white px-3 py-1 rounded mb-4"
        onClick={() => setShowThinking(!showThinking)}
      >
        {showThinking ? 'Hide Thinking' : 'Show Thinking'}
      </button>

      {/* Thinking Section */}
      {showThinking && (
        <div className="thinking-section mb-6">
          <InformationContent />
        </div>
      )}

      {results.length > 0 ? (
        <>
          <table>
            <thead>
              <tr>
                <th>Property Link</th>
                <th>Price</th>
                {dynamicColumns.map((col, idx) => (
                  <th key={idx}>{col.replace(/_/g, ' ')}</th>
                ))}
                <th>Description</th>
                <th>Broker</th>
                <th>Receive Realtor Proposal</th>
              </tr>
            </thead>
            <tbody>
              {results.map((property, index) => (
                <tr key={index}>
                  {/* Property Link */}
                  <td>
                    {property.listingurl ? (
                      <a href={property.listingurl} target="_blank" rel="noopener noreferrer">
                        View Property
                      </a>
                    ) : (
                      'N/A'
                    )}
                  </td>

                  {/* Price */}
                  <td>
                    {property.price ? `$${Number(property.price).toLocaleString()}` : 'N/A'}
                  </td>

                  {/* Dynamic Trait Columns */}
                  {dynamicColumns.map((col, idx) => (
                    <td key={idx}>
                      {property[col] === '🟢' && <span title="Yes">🟢</span>}
                      {property[col] === '🟡' && <span title="Unsure">🟡</span>}
                      {property[col] === '⚪' && <span title="No">⚪</span>}
                      {!['🟢', '🟡', '⚪'].includes(property[col]) && 'N/A'}
                    </td>
                  ))}

                  {/* Description */}
                  <td>
                    {property.neighborhood_desc ? (
                      <div className="description-cell">{property.neighborhood_desc}</div>
                    ) : (
                      'N/A'
                    )}
                  </td>

                  {/* Broker */}
                  <td>
                    {property.zip_code ? (
                      <button onClick={() => handleViewBrokers(property.zip_code)}>
                        🔗 Click to view brokers
                      </button>
                    ) : (
                      'N/A'
                    )}
                  </td>

                  {/* Receive Realtor Proposal */}
                  <td>
                    <button onClick={handleRealtorProposal}>📨 Receive Proposal</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Download Button */}
          <button
            onClick={() => {
              const csvContent = [
                [
                  'Property Link',
                  'Price',
                  ...dynamicColumns.map((col) => col.replace(/_/g, ' ')),
                  'Description',
                  'Broker',
                  'Receive Realtor Proposal',
                ],
                ...results.map((prop) => [
                  prop.listingurl ? `View Property (${prop.listingurl})` : 'N/A',
                  prop.price ? `$${Number(prop.price).toLocaleString()}` : 'N/A',
                  ...dynamicColumns.map((col) => prop[col] || 'N/A'),
                  prop.neighborhood_desc || 'N/A',
                  prop.zip_code ? `View Brokers for ${prop.zip_code}` : 'N/A',
                  'Receive Proposal',
                ]),
              ]
                .map((e) => e.join(','))
                .join('\n');

              const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.setAttribute('href', url);
              link.setAttribute('download', 'query_results.csv');
              link.style.visibility = 'hidden';
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }}
          >
            📥 Download Results as CSV
          </button>
        </>
      ) : (
        <div className="error-message">❌ No results found for the given query.</div>
      )}
    </div>
  );
};

export default Results;

