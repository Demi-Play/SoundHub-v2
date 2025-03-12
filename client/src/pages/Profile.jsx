import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { logout } from '../api/userApi';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        console.log(token);
        if (!token) {
          alert('You are not logged in');
          navigate('/login');
          return;
        }

        const response = await axios.get('http://127.0.0.1:8000/api/users/profile', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProfile(response.data);
      } catch (err) {
        console.error(err);
        setError('Failed to load profile');
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [navigate]);

  const handleUpdate = async (updatedData) => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await axios.put(
        'http://127.0.0.1:8000/api/users/profile',
        updatedData,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setProfile(response.data);
      alert('Profile updated successfully');
    } catch (err) {
      console.error('Failed to update profile:', err);
      setError('Failed to update profile');
    }
  };

  if (loading) return <p>Loading...</p>;

  if (error) return <p>{error}</p>;

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h2>Profile</h2>
      {profile ? (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleUpdate({
              bio: profile.bio,
              genres: profile.genres,
              instruments: profile.instruments,
              social_links: profile.social_links,
            });
          }}
        >
          <div>
            <label>Bio:</label>
            <textarea
              value={profile.bio}
              onChange={(e) =>
                setProfile({ ...profile, bio: e.target.value })
              }
            />
          </div>
          <div>
            <label>Genres:</label>
            <input
              type="text"
              value={profile.genres.join(', ')}
              onChange={(e) =>
                setProfile({ ...profile, genres: e.target.value.split(', ') })
              }
            />
          </div>
          <div>
            <label>Instruments:</label>
            <input
              type="text"
              value={profile.instruments.join(', ')}
              onChange={(e) =>
                setProfile({ ...profile, instruments: e.target.value.split(', ') })
              }
            />
          </div>
          <div>
            <label>Social Links:</label>
            <input
              type="text"
              value={JSON.stringify(profile.social_links)}
              onChange={(e) =>
                setProfile({ ...profile, social_links: JSON.parse(e.target.value) })
              }
            />
          </div>
          <button type="submit">Save Changes</button>
        </form>

      ) : (
        <div>
          <p>No profile data available</p>
        </div>
      )}
      <button onClick={logout}>Logout</button>

    </div>
  );
};

export default Profile;