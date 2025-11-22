import axios from 'axios';

const API_URL = 'https://repogenesis-1.onrender.com/api';

export const registerUser = async (username, password) => {
    try {
        const response = await axios.post(`${API_URL}/auth/register`, { username, password });
        return response.data;
    } catch (error) {
        console.error('Registration error', error);
        throw error;
    }
};

export const loginUser = async (username, password) => {
    try {
        const response = await axios.post(`${API_URL}/auth/login`, { username, password });
        return response.data;
    } catch (error) {
        console.error('Login error', error);
        throw error;
    }
};

export const logSleep = async (userId, hours) => {
    try {
        const response = await axios.post(`${API_URL}/sleep/log`, { user_id: userId, hours: parseFloat(hours) });
        return response.data;
    } catch (error) {
        console.error('Log sleep error', error);
        throw error;
    }
};

export const startSleep = async (userId) => {
    try {
        const response = await axios.post(`${API_URL}/sleep/start`, { user_id: userId });
        return response.data;
    } catch (error) {
        console.error('Start sleep error', error);
        throw error;
    }
};

export const endSleep = async (userId) => {
    try {
        const response = await axios.post(`${API_URL}/sleep/end`, { user_id: userId });
        return response.data;
    } catch (error) {
        console.error('End sleep error', error);
        throw error;
    }
};

export const getStats = async (userId) => {
    try {
        const response = await axios.get(`${API_URL}/sleep/stats/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Get stats error', error);
        throw error;
    }
};

export const getLeaderboard = async () => {
    try {
        const response = await axios.get(`${API_URL}/social/leaderboard`);
        return response.data;
    } catch (error) {
        console.error('Get leaderboard error', error);
        throw error;
    }
};

export const getFriends = async (userId) => {
    try {
        const response = await axios.get(`${API_URL}/social/friends/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Get friends error', error);
        return []; // Return empty array on error
    }
};

export const getUserReliability = async (userId) => {
    try {
        const response = await axios.get(`${API_URL}/sleep/reliability/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Get reliability error', error);
        return { score: 0.75, grade: 'B', description: 'Default' };
    }
};

export const getLogs = async (userId) => {
    try {
        const response = await axios.get(`${API_URL}/sleep/logs/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Get logs error', error);
        return [];
    }
};

export const logEvent = async (userId, eventType, metadata = {}) => {
    try {
        await axios.post(`${API_URL}/sleep/event`, { user_id: userId, event_type: eventType, metadata });
    } catch (error) {
        console.error('Log event error', error);
    }
};
