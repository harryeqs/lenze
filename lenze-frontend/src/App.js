// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import WebSearch from './components/WebSearch';
import WebSearchStream from './components/WebSearchStream';

const App = () => {
    return (
        <Router>
            <div>
                <Routes>
                    <Route exact path="/web-search" element={<WebSearch />} />
                    <Route path="/web-search-stream" element={<WebSearchStream />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
