// src/components/InformationContent.js

import React, { useContext } from 'react';
import { QueryContext } from '../context/QueryContext';

const InformationContent = () => {
  const { userIntent, traits, keyPhrases, propertyKeywords, sqlQuery } = useContext(QueryContext);

  return (
    <div className="max-w-4xl mx-auto p-4 bg-gray-100 rounded-md shadow-md">
      <h1 className="text-2xl font-bold mb-4">Extracted Information</h1>

      <section className="mb-4">
        <h2 className="text-xl font-semibold">User Intent</h2>
        <p className="mt-2">{userIntent}</p>
      </section>

      <section className="mb-4">
        <h2 className="text-xl font-semibold">Traits</h2>
        <ul className="list-disc list-inside mt-2">
          {traits.map((trait, index) => (
            <li key={index}>{trait}</li>
          ))}
        </ul>
      </section>

      <section className="mb-4">
        <h2 className="text-xl font-semibold">Key Phrases</h2>
        <ul className="list-disc list-inside mt-2">
          {keyPhrases.map((phrase, index) => (
            <li key={index}>{phrase}</li>
          ))}
        </ul>
      </section>

      <section className="mb-4">
        <h2 className="text-xl font-semibold">Property Keywords</h2>
        <p className="mt-2">{propertyKeywords}</p>
      </section>

      <section className="mb-4">
        <h2 className="text-xl font-semibold">Generated SQL Query</h2>
        <pre className="bg-white p-2 rounded mt-2 overflow-auto">{sqlQuery}</pre>
      </section>
    </div>
  );
};

export default InformationContent;
