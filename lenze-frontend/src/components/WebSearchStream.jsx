import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import SearchForm from './SearchForm';
import ResponseDisplay from './ResponseDisplay';
import RelatedQueries from './RelatedQueries';
import SourcesList from './SourcesList';

const API_URL = 'http://localhost:8000';

const useQuery = () => {
    return new URLSearchParams(useLocation().search);
};

const WebSearchStream = () => {
    const { sessionId } = useParams();
    const query = useQuery().get('query');
    const navigate = useNavigate();
    const responseRef = useRef('');
    const [response, setResponse] = useState('');
    const [previousConversations, setPreviousConversations] = useState([]); // State to store previous conversations
    const [isStreaming, setIsStreaming] = useState(false);
    const [isSearching, setIsSeaching] = useState(false);
    const [hasStartedStreaming, setHasStartedStreaming] = useState(false);
    const [relatedQueries, setRelatedQueries] = useState([]);
    const [timeTaken, setTimeTaken] = useState('');
    const [sources, setSources] = useState([]);
    const [currentQuery, setCurrentQuery] = useState(query || ''); // State to store the current query
    const abortControllerRef = useRef(null);

    const fetchPreviousConversations = useCallback(async () => {
        if (!sessionId) return;
        try {
            const response = await fetch(`${API_URL}/conversations/${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                setPreviousConversations(data);
            } else {
                console.error('Failed to fetch previous conversations');
            }
        } catch (error) {
            console.error('Error fetching previous conversations:', error);
        }
    }, [sessionId]);

    const handleSearch = useCallback((query) => {
        if (!sessionId) {
            alert('No session ID available.');
            return;
        };
        setCurrentQuery(query); // Update the current query state
        setIsSeaching(true);
        setHasStartedStreaming(false);
        responseRef.current = '';
        setResponse('');
        setRelatedQueries([]);
        setTimeTaken('');
        setSources([]);
        abortControllerRef.current = new AbortController();

        console.log(`Connecting to ${API_URL}/web-search-stream/${sessionId}?query=${encodeURIComponent(query)}`);

        fetchEventSource(`${API_URL}/web-search-stream/${sessionId}?query=${encodeURIComponent(query)}`, {
            method: "POST",
            headers: { Accept: "text/event-stream" },
            signal: abortControllerRef.current.signal,
            onopen(response) {
                console.log('Connection to stream opened');
                if (response.ok && response.status === 200) {
                    console.log('Connected!');
                } else if (response.status >= 400 && response.status < 500 && response.status !== 429) {
                    console.error(`Client side error: ${response.status}`);
                    throw new Error('Client side error');
                }
            },
            onmessage(event) {
                console.log('Message received:', event.data);
                if (event.event === 'finaljson') {
                    const finalData = JSON.parse(event.data);
                    setRelatedQueries(finalData.related);
                    setTimeTaken(finalData.time_taken);
                    setIsStreaming(false);
                    console.log("Related queries and time taken received")
                } else if (event.event === 'source') {
                    const sourcesData = JSON.parse(event.data);
                    setSources(sourcesData);
                    console.log("Sources received");
                    setIsSeaching(false)
                } else if (event.data) {
                    responseRef.current += event.data;
                    setResponse(responseRef.current);
                    setIsStreaming(true);
                    setHasStartedStreaming(true);
                }
            },
            onclose() {
                console.log('Connection to stream closed');
                setIsStreaming(false);
            },
            onerror(err) {
                console.error('EventSource error:', err);
                abortControllerRef.current.abort();
                setIsStreaming(false);
            },
        });
    }, [sessionId]);

    useEffect(() => {
        if (query) {
            handleSearch(query);
        }

        // Fetch previous conversations when component mounts
        fetchPreviousConversations();

        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, [query, handleSearch, fetchPreviousConversations]);

    return (
        <div>
            <h1>Web Search Stream</h1>
            {previousConversations.length > 0 && (
                <div>
                    <ul>
                        {previousConversations.map((conv, index) => (
                            <li key={index}>
                                <h2>{conv.query}</h2>
                                <h3>Answer</h3>
                                <ResponseDisplay response={conv.response} />
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            <button onClick={() => navigate('/')}>Start New Session</button>
            <SearchForm onSearch={handleSearch} />
            {currentQuery && <h2>{currentQuery}</h2>}
            {isSearching && <p>Searching...</p>}
            <SourcesList sources={sources} />
            {hasStartedStreaming && <h3>Answer</h3>}
            {isStreaming && <p>Streaming response...</p>}
            <ResponseDisplay response={response} />
            <RelatedQueries queries={relatedQueries} />
            {timeTaken && <p>{timeTaken}</p>}
        </div>
    );
};

export default WebSearchStream;
