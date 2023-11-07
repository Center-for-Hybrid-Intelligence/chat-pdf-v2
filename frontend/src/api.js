import axios from 'axios';


const baseURL = process.env.NODE_ENV === 'production' ? "https://hybridintelligence.eu/chat-pdf/api/api" : 'http://localhost:3052/api';

const authService = axios.create({
    baseURL: baseURL,
    withCredentials: true,
    xsrfCookieName: 'csrf_access_token'
});
export { authService };