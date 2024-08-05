// src/pages/WebSearchStream.js
import React, { useState } from 'react';
import SearchForm from './SearchForm';
import StreamAnswer from './StreamAnswer';

const WebSearchStream = () => {
  const [query, setQuery] = useState('');

  const handleSearch = (newQuery) => {
    setQuery(newQuery);
  };

  return (
    <div>
      <h1>Web Search Stream</h1>
      <SearchForm onSearch={handleSearch} />
      {query && <StreamAnswer query={query} />}
    </div>
  );
};

export default WebSearchStream;
