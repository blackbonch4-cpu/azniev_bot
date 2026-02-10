import { useState, useContext, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AppContext } from '../context/AppContext';
import { updateWebinar, uploadImage } from '../api/api';
import './EditWebinar.css';

const EditWebinar = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin, webinars, refreshWebinars } = useContext(AppContext);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    event_date: '',
    event_time: '',
    price: '',
    location: '',
    group_link: '',
    payment_link: '',
    is_active: true
  });

  const [currentImage, setCurrentImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [webinarNotFound, setWebinarNotFound] = useState(false);

  // Загрузить данные вебинара
  useEffect(() => {
    const webinar = webinars.find(w => w.id === parseInt(id));
    if (webinar) {
      // Преобразовать дату в отдельные поля date и time
      const eventDate = new Date(webinar.event_datetime);
      const dateStr = eventDate.toISOString().slice(0, 10); // YYYY-MM-DD
      const timeStr = eventDate.toISOString().slice(11, 16); // HH:MM

      setFormData({
        title: webinar.title || '',
        description: webinar.description || '',
        event_date: dateStr,
        event_time: timeStr,
        price: webinar.price?.toString() || '',
        location: webinar.location || '',
        group_link: webinar.group_link || '',
        payment_link: webinar.payment_link || '',
        is_active: webinar.is_active !== false
      });

      setCurrentImage(webinar.image_url);
    } else {
      setWebinarNotFound(true);
    }
  }, [id, webinars]);

  // Проверка прав доступа
  if (!isAdmin) {
    return (
      <div className="edit-webinar-page">
        <div className="access-denied">
          <h2>❌ Доступ запрещен</h2>
          <p>Только администраторы могут редактировать вебинары</p>
          <button onClick={() => navigate('/')}>На главную</button>
        </div>
      </div>
    );
  }

  if (webinarNotFound) {
    return (
      <div className="edit-webinar-page">
        <div className="access-denied">
          <h2>❌ Вебинар не найден</h2>
          <button onClick={() => navigate('/admin')}>К списку курсов</button>
        </div>
      </div>
    );
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);

      // Создать preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const validateForm = () => {
    if (!formData.title.trim()) {
      setError('Введите название вебинара');
      return false;
    }
    if (!formData.event_date) {
      setError('Выберите дату');
      return false;
    }
    if (!formData.event_time) {
      setError('Выберите время');
      return false;
    }
    if (!formData.price || parseFloat(formData.price) < 0) {
      setError('Введите корректную цену');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      let imageUrl = undefined;

      // Загрузить новое изображение, если выбрано
      if (imageFile) {
        const uploadResult = await uploadImage(imagePreview);
        if (uploadResult.success) {
          imageUrl = uploadResult.image_url;
        } else {
          throw new Error('Ошибка загрузки изображения');
        }
      }

      // Собрать дату и время в единое поле
      const { event_date, event_time, ...restFormData } = formData;
      const updateData = {
        ...restFormData,
        event_datetime: `${event_date}T${event_time}`,
        price: parseFloat(formData.price)
      };

      // Добавить image_url только если загружено новое
      if (imageUrl) {
        updateData.image_url = imageUrl;
      }

      const result = await updateWebinar(parseInt(id), updateData);

      if (result.success) {
        // Обновить список вебинаров
        await refreshWebinars();
        // Перейти на страницу админки
        navigate('/admin');
      } else {
        throw new Error(result.error || 'Ошибка обновления вебинара');
      }
    } catch (err) {
      console.error('Error updating webinar:', err);
      setError(err.message || 'Произошла ошибка при обновлении вебинара');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="edit-webinar-page">
      <div className="edit-webinar-header">
        <button className="back-btn" onClick={() => navigate('/admin')}>
          ← Назад
        </button>
        <h1>Редактировать курс</h1>
      </div>

      <form className="webinar-form" onSubmit={handleSubmit}>
        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label>Название курса *</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            placeholder="Например: Основы Python"
            required
          />
        </div>

        <div className="form-group">
          <label>Описание</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Краткое описание курса"
            rows="4"
          />
        </div>

        <div className="form-group">
          <label>Дата *</label>
          <input
            type="date"
            name="event_date"
            value={formData.event_date}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Время *</label>
          <input
            type="time"
            name="event_time"
            value={formData.event_time}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Цена (₽) *</label>
          <input
            type="number"
            name="price"
            value={formData.price}
            onChange={handleInputChange}
            placeholder="5000"
            min="0"
            step="0.01"
            required
          />
        </div>

        <div className="form-group">
          <label>Место проведения</label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleInputChange}
            placeholder="Online / Москва"
          />
        </div>

        <div className="form-group">
          <label>Ссылка на группу Telegram</label>
          <input
            type="url"
            name="group_link"
            value={formData.group_link}
            onChange={handleInputChange}
            placeholder="https://t.me/..."
          />
        </div>

        <div className="form-group">
          <label>Ссылка на оплату</label>
          <input
            type="url"
            name="payment_link"
            value={formData.payment_link}
            onChange={handleInputChange}
            placeholder="https://..."
          />
        </div>

        <div className="form-group">
          <label>Изображение курса</label>
          {currentImage && !imagePreview && (
            <div className="current-image">
              <p className="image-label">Текущее изображение:</p>
              <img src={currentImage} alt="Current" />
            </div>
          )}
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="file-input"
          />
          {imagePreview && (
            <div className="image-preview">
              <p className="image-label">Новое изображение:</p>
              <img src={imagePreview} alt="Preview" />
            </div>
          )}
        </div>

        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleInputChange}
            />
            <span>Курс активен (виден пользователям)</span>
          </label>
        </div>

        <button
          type="submit"
          className="submit-btn"
          disabled={loading}
        >
          {loading ? 'Сохранение...' : '✓ Сохранить изменения'}
        </button>
      </form>
    </div>
  );
};

export default EditWebinar;
