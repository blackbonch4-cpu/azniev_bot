import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../context/AppContext';
import './ProfilePage.css';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, profile, isAdmin } = useContext(AppContext);

  const getAvatarUrl = () => {
    if (profile?.avatar_url) {
      return profile.avatar_url;
    }
    const name = user?.first_name || 'User';
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&size=200&background=667eea&color=fff`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Не указано';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="profile-page">
      <div className="profile-header">
        <button className="back-btn" onClick={() => navigate('/')}>
          ← Назад
        </button>
        <h1>Профиль</h1>
      </div>

      <div className="profile-content">
        <div className="profile-avatar-section">
          <img
            src={getAvatarUrl()}
            alt="Avatar"
            className="profile-avatar-large"
          />
          {isAdmin && (
            <div className="admin-badge-large">👑 Администратор</div>
          )}
        </div>

        <div className="profile-info">
          <div className="info-item">
            <span className="info-label">Имя</span>
            <span className="info-value">
              {user?.first_name || 'Не указано'} {user?.last_name || ''}
            </span>
          </div>

          <div className="info-item">
            <span className="info-label">Username</span>
            <span className="info-value">
              {user?.username ? `@${user.username}` : 'Не указан'}
            </span>
          </div>

          <div className="info-item">
            <span className="info-label">Email</span>
            <span className="info-value">
              {profile?.email || 'Не указан'}
            </span>
          </div>

          <div className="info-item">
            <span className="info-label">Дата регистрации</span>
            <span className="info-value">
              {formatDate(profile?.registration_date)}
            </span>
          </div>
        </div>

        <div className="profile-stats">
          <div className="stat-card">
            <div className="stat-value">{profile?.total_purchases || 0}</div>
            <div className="stat-label">Куплено курсов</div>
          </div>

          <div className="stat-card">
            <div className="stat-value">
              {profile?.total_spent ? `${profile.total_spent.toLocaleString('ru-RU')} ₽` : '0 ₽'}
            </div>
            <div className="stat-label">Потрачено</div>
          </div>
        </div>

        <div className="profile-actions">
          <button
            className="action-btn"
            onClick={() => navigate('/purchases')}
          >
            🎫 Мои покупки
          </button>

          {isAdmin && (
            <button
              className="action-btn admin-btn"
              onClick={() => navigate('/admin')}
            >
              👑 Админ-панель
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
