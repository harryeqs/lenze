// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import WebSearch from './components/WebSearch';
import StreamSearch from './components/StreamSearch';

const App = () => {
    return (
        <Router>
            <div>
                <Routes>
                    <Route exact path="/web-search" element={<WebSearch />} />
                    <Route path="/web-search-stream" element={<StreamSearch />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
