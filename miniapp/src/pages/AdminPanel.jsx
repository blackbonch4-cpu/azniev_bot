import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import { deleteWebinar } from '../api/api'
import './AdminPanel.css'

function AdminPanel() {
  const navigate = useNavigate()
  const { webinars, isAdmin, refreshWebinars } = useApp()

  if (!isAdmin) {
    return <div className="page"><div className="empty-state">Доступ запрещен</div></div>
  }

  const handleDelete = async (id) => {
    if (confirm('Удалить этот вебинар?')) {
      try {
        await deleteWebinar(id)
        await refreshWebinars()
      } catch (error) {
        alert('Ошибка при удалении')
      }
    }
  }

  return (
    <div className="page admin-page">
      <div className="admin-header">
        <h1>👑 Админ панель</h1>
        <button className="add-btn" onClick={() => navigate('/admin/add')}>
          ➕ Добавить курс
        </button>
      </div>

      <div className="webinars-list">
        {webinars.map(webinar => (
          <div key={webinar.id} className="admin-webinar-card">
            {webinar.image_url && (
              <img src={webinar.image_url} alt={webinar.title} className="admin-webinar-img" />
            )}
            <div className="admin-webinar-info">
              <h3>{webinar.title}</h3>
              <p>{webinar.price} ₽</p>
              <small>{new Date(webinar.event_datetime).toLocaleDateString('ru-RU')}</small>
            </div>
            <div className="admin-webinar-actions">
              <button onClick={() => navigate(`/admin/edit/${webinar.id}`)}>✏️</button>
              <button onClick={() => handleDelete(webinar.id)}>🗑️</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AdminPanel
