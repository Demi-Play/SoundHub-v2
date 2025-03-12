// src/api/userApi.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/users';

export const login = async (username, password) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/login`, { username, password });
    console.log("Server response:", response.data); // Логирование ответа
    return response.data;
  } catch (error) {
    console.error("Login failed:", error.response?.data || error.message);
    throw error;
  }
};

export const register = async (userData) => {
  const response = await axios.post(
    `${API_BASE_URL}/register`,
    userData,
    // {
    //   headers: { 'X-CSRFToken': csrfToken },
    //   withCredentials: true, // Включите cookies
    // }
  );
  return response.data;
};

export const logout = async () => {
  const token = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  const response = await axios.post(`${API_BASE_URL}/logout`, { 'refresh': refreshToken },  { 
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

