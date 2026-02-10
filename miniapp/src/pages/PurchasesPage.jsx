import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserPurchases } from '../api/api';
import './PurchasesPage.css';

const PurchasesPage = () => {
  const navigate = useNavigate();
  const [purchases, setPurchases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPurchases();
  }, []);

  const loadPurchases = async () => {
    try {
      setLoading(true);
      const data = await getUserPurchases();
      setPurchases(data);
    } catch (err) {
      console.error('Error loading purchases:', err);
      setError('Ошибка загрузки покупок');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const openGroupLink = (link) => {
    if (window.Telegram?.WebApp) {
      if (link.includes('t.me/')) {
        window.Telegram.WebApp.openTelegramLink(link);
      } else {
        window.Telegram.WebApp.openLink(link);
      }
    } else {
      window.open(link, '_blank');
    }
  };

  const upcomingPurchases = purchases.filter(p => p.is_upcoming);
  const pastPurchases = purchases.filter(p => !p.is_upcoming);

  if (loading) {
    return (
      <div className="purchases-page">
        <div className="loading">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="purchases-page">
      <div className="purchases-header">
        <button className="back-btn" onClick={() => navigate('/')}>
          ← Назад
        </button>
        <h1>Мои покупки</h1>
      </div>

      {error && <div className="error-message">{error}</div>}

      {purchases.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🎫</div>
          <h3>У вас пока нет покупок</h3>
          <p>Купите свой первый курс, чтобы увидеть его здесь</p>
          <button
            className="browse-btn"
            onClick={() => navigate('/')}
          >
            Смотреть курсы
          </button>
        </div>
      ) : (
        <div className="purchases-content">
          {upcomingPurchases.length > 0 && (
            <div className="purchases-section">
              <h2 className="section-title">Предстоящие ({upcomingPurchases.length})</h2>
              <div className="purchases-list">
                {upcomingPurchases.map((purchase) => (
                  <div key={purchase.id} className="purchase-card upcoming">
                    {purchase.webinar_image_url && (
                      <img
                        src={purchase.webinar_image_url}
                        alt={purchase.webinar_title}
                        className="purchase-img"
                      />
                    )}
                    <div className="purchase-info">
                      <h3>{purchase.webinar_title}</h3>
                      <div className="purchase-details">
                        <span className="purchase-date">
                          📅 {formatDate(purchase.webinar_datetime)}
                        </span>
                        <span className="purchase-time">
                          🕐 {formatTime(purchase.webinar_datetime)}
                        </span>
                        {purchase.webinar_location && (
                          <span className="purchase-location">
                            📍 {purchase.webinar_location}
                          </span>
                        )}
                      </div>
                      {purchase.webinar_group_link && (
                        <button
                          className="group-btn"
                          onClick={() => openGroupLink(purchase.webinar_group_link)}
                        >
                          ✈️ Перейти в группу
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {pastPurchases.length > 0 && (
            <div className="purchases-section">
              <h2 className="section-title">Прошедшие ({pastPurchases.length})</h2>
              <div className="purchases-list">
                {pastPurchases.map((purchase) => (
                  <div key={purchase.id} className="purchase-card past">
                    {purchase.webinar_image_url && (
                      <img
                        src={purchase.webinar_image_url}
                        alt={purchase.webinar_title}
                        className="purchase-img"
                      />
                    )}
                    <div className="purchase-info">
                      <h3>{purchase.webinar_title}</h3>
                      <div className="purchase-details">
                        <span className="purchase-date">
                          📅 {formatDate(purchase.webinar_datetime)}
                        </span>
                        <span className="purchase-price">
                          💰 {purchase.amount.toLocaleString('ru-RU')} ₽
                        </span>
                      </div>
                      {purchase.webinar_group_link && (
                        <button
                          className="group-btn"
                          onClick={() => openGroupLink(purchase.webinar_group_link)}
                        >
                          ✈️ Перейти в группу
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PurchasesPage;
