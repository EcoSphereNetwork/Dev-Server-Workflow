// src/api/client.ts
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor für das Hinzufügen des Auth-Tokens
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor für die Fehlerbehandlung
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Globale Fehlerbehandlung
    if (error.response) {
      // Der Server hat mit einem Statuscode geantwortet, der außerhalb des Bereichs 2xx liegt
      console.error('API Error:', error.response.status, error.response.data);
      
      // Bei 401 Unauthorized: Benutzer ausloggen und zur Login-Seite weiterleiten
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    } else if (error.request) {
      // Die Anfrage wurde gestellt, aber keine Antwort erhalten
      console.error('API Error: No response received', error.request);
    } else {
      // Beim Einrichten der Anfrage ist ein Fehler aufgetreten
      console.error('API Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;