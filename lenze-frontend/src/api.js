// src/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Adjust this if your FastAPI server is running on a different port

export const webSearch = async (query) => {
    try {
        const response = await axios.post(`${API_URL}/web-search`, null, {
            params: { query }
        });
        return response.data;
    } catch (error) {
        console.error('Error performing web search:', error);
        throw error;
    }
};