// src/api/csrf.js
import axios from 'axios';

export const getCsrfToken = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/get-csrf-token/', {
      withCredentials: true, // Включите cookies
    });
    return response.data.csrfToken;
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error);
  }
};