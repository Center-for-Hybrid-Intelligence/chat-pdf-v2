import axios from 'axios';


const baseURL = process.env.NODE_ENV !== 'development' ? "https://hybridintelligence.eu/chat-pdf/api/api" : 'http://localhost:5000/api';

const authService = axios.create({
    baseURL: baseURL,
    withCredentials: true,
    xsrfCookieName: 'csrf_access_token'
});
export { authService };