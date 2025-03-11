// src/api/userApi.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/users';

export const login = async (username, password) => {
//   console.log(csrfToken);
  const response = await axios.post(
    `${API_BASE_URL}/login`,
    { username, password },
    // {
    // //   headers: { 'X-CSRFToken': csrfToken },
    // //   withCredentials: true, // Включите cookies
    // }
  );
  return response.data;
};

export const register = async (userData, csrfToken) => {
  const response = await axios.post(
    `${API_BASE_URL}/register`,
    userData,
    {
      headers: { 'X-CSRFToken': csrfToken },
      withCredentials: true, // Включите cookies
    }
  );
  return response.data;
};