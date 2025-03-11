import React, { useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleLogout = async () => {
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        await axios.post('http://127.0.0.1:8000/api/users/logout/', { refresh: refreshToken });
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        alert('Logged out successfully');
        navigate('/');
      } catch (err) {
        console.error(err);
      }
    };
    handleLogout();
  }, [navigate]);

  return <p>Logging out...</p>;
};

export default Logout;