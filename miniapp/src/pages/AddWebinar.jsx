import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../context/AppContext';
import { createWebinar, uploadImage } from '../api/api';
import './AddWebinar.css';

const AddWebinar = () => {
  const navigate = useNavigate();
  const { isAdmin, refreshWebinars } = useContext(AppContext);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    event_date: '',
    event_time: '',
    price: '',
    location: '',
    group_link: '',
    payment_link: ''
  });

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Проверка прав доступа
  if (!isAdmin) {
    return (
      <div className="add-webinar-page">
        <div className="access-denied">
          <h2>❌ Доступ запрещен</h2>
          <p>Только администраторы могут добавлять вебинары</p>
          <button onClick={() => navigate('/')}>На главную</button>
        </div>
      </div>
    );
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
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
      let imageUrl = null;

      // Загрузить изображение, если выбрано
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
      const webinarData = {
        ...restFormData,
        event_datetime: `${event_date}T${event_time}`,
        price: parseFloat(formData.price),
        image_url: imageUrl
      };

      const result = await createWebinar(webinarData);

      if (result.success) {
        // Обновить список вебинаров
        await refreshWebinars();
        // Перейти на страницу админки
        navigate('/admin');
      } else {
        throw new Error(result.error || 'Ошибка создания вебинара');
      }
    } catch (err) {
      console.error('Error creating webinar:', err);
      setError(err.message || 'Произошла ошибка при создании вебинара');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-webinar-page">
      <div className="add-webinar-header">
        <button className="back-btn" onClick={() => navigate('/admin')}>
          ← Назад
        </button>
        <h1>Добавить курс</h1>
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
          <input
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="file-input"
          />
          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="Preview" />
            </div>
          )}
        </div>

        <button
          type="submit"
          className="submit-btn"
          disabled={loading}
        >
          {loading ? 'Создание...' : '✓ Создать курс'}
        </button>
      </form>
    </div>
  );
};

export default AddWebinar;
