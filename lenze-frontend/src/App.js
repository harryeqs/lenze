import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SearchHistory from './components/SearchHistory';
import WebSearchStream from './components/WebSearchStream';
import Home from './components/Home';

const App = () => {
    return (
        <Router>
            <div>
                <Routes>
                    <Route path="/history" element={<SearchHistory />} />
                    <Route path="/stream/:sessionId?" element={<WebSearchStream />} />
                    <Route path="/" element={<Home />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
