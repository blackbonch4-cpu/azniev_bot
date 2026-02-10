import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../context/AppContext';
import { sendSupportTicket } from '../api/api';
import './SupportPage.css';

const SupportPage = () => {
  const navigate = useNavigate();
  const { user } = useContext(AppContext);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (question.trim().length < 10) {
      setError('Вопрос должен содержать минимум 10 символов');
      return;
    }

    setLoading(true);

    try {
      const result = await sendSupportTicket(question.trim());

      if (result.success) {
        setSuccess(true);
        setQuestion('');

        // Скрыть сообщение об успехе через 3 секунды
        setTimeout(() => {
          setSuccess(false);
        }, 3000);
      } else {
        throw new Error(result.error || 'Не удалось отправить вопрос');
      }
    } catch (err) {
      console.error('Error sending support ticket:', err);
      setError(err.message || 'Произошла ошибка при отправке вопроса');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="support-page">
      <div className="support-header">
        <button className="back-btn" onClick={() => navigate('/')}>
          ← Назад
        </button>
        <h1>Поддержка</h1>
      </div>

      <div className="support-content">
        <div className="support-info">
          <div className="info-icon">💬</div>
          <h2>Есть вопрос?</h2>
          <p>
            Напишите ваш вопрос, и наша команда поддержки свяжется с вами в ближайшее время.
          </p>
        </div>

        <form className="support-form" onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}
          {success && (
            <div className="success-message">
              ✓ Ваш вопрос успешно отправлен! Мы свяжемся с вами в ближайшее время.
            </div>
          )}

          <div className="form-group">
            <label>Ваш вопрос</label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Опишите ваш вопрос или проблему подробно..."
              rows="6"
              minLength="10"
              required
              disabled={loading}
            />
            <div className="char-counter">
              {question.length} символов {question.length < 10 ? `(минимум 10)` : ''}
            </div>
          </div>

          <div className="user-info">
            <p className="info-label">Ответ будет отправлен в Telegram:</p>
            <div className="user-details">
              <span className="user-name">
                {user?.first_name || 'Пользователь'} {user?.last_name || ''}
              </span>
              {user?.username && (
                <span className="user-username">@{user.username}</span>
              )}
            </div>
          </div>

          <button
            type="submit"
            className="submit-btn"
            disabled={loading || question.trim().length < 10}
          >
            {loading ? 'Отправка...' : '📨 Отправить вопрос'}
          </button>
        </form>

        <div className="support-faq">
          <h3>Часто задаваемые вопросы</h3>
          <div className="faq-list">
            <div className="faq-item">
              <div className="faq-question">❓ Как получить доступ к группе после оплаты?</div>
              <div className="faq-answer">
                После оплаты ссылка на группу появится в разделе "Мои покупки"
              </div>
            </div>
            <div className="faq-item">
              <div className="faq-question">❓ Как вернуть деньги за курс?</div>
              <div className="faq-answer">
                Для возврата средств напишите нам через эту форму с указанием номера заказа
              </div>
            </div>
            <div className="faq-item">
              <div className="faq-question">❓ Можно ли перенести курс на другую дату?</div>
              <div className="faq-answer">
                Да, напишите нам, и мы поможем перенести на следующий поток
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupportPage;
