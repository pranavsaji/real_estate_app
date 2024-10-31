// src/App.js

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import SavedSearches from './components/SavedSearches'; // Saved Searches Sidebar

import Home from './pages/Home';
import Information from './pages/Information';
import Results from './pages/Results';
import BrokerDetails from './pages/BrokerDetails';

import { QueryProvider } from './context/QueryContext';

function App() {
  return (
    <QueryProvider>
      <Router>
        <div className="flex flex-col min-h-screen">
          <Navbar />
          <div className="flex flex-1">
            <SavedSearches /> {/* Left Sidebar for Saved Searches */}
            <main className="flex-1 p-4 overflow-auto">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/information" element={<Information />} />
                <Route path="/results" element={<Results />} />
                <Route path="/broker-details" element={<BrokerDetails />} />
              </Routes>
            </main>
          </div>
          <Footer />
        </div>
      </Router>
    </QueryProvider>
  );
}

export default App;


// // src/App.js

// import React from 'react';
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// import Navbar from './components/Navbar';
// import Footer from './components/Footer';
// import SavedSearches from './components/SavedSearches'; // Saved Searches Sidebar

// import Home from './pages/Home';
// import Information from './pages/Information';
// import Results from './pages/Results';
// import BrokerDetails from './pages/BrokerDetails';

// import { QueryProvider } from './context/QueryContext';

// function App() {
//   return (
//     <QueryProvider>
//       <Router>
//         <div className="flex flex-col min-h-screen">
//           <Navbar />
//           <div className="flex flex-1">
//             <SavedSearches /> {/* Left Sidebar for Saved Searches */}
//             <main className="flex-1 p-4 overflow-auto">
//               <Routes>
//                 <Route path="/" element={<Home />} />
//                 <Route path="/information" element={<Information />} />
//                 <Route path="/results" element={<Results />} />
//                 <Route path="/broker-details" element={<BrokerDetails />} />
//               </Routes>
//             </main>
//           </div>
//           <Footer />
//         </div>
//       </Router>
//     </QueryProvider>
//   );
// }

// export default App;

