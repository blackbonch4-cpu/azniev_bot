import WebApp from '@twa-dev/sdk'
import './CourseModal.css'

function CourseModal({ webinar, onClose }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' })
  }

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }

  const handleAction = () => {
    if (webinar.is_purchased && webinar.group_link) {
      WebApp.openTelegramLink(webinar.group_link)
    } else if (webinar.payment_link) {
      WebApp.openLink(webinar.payment_link)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>

        {webinar.image_url && (
          <img src={webinar.image_url} alt={webinar.title} className="modal-image" />
        )}

        <h2 className="modal-title">{webinar.title}</h2>

        {webinar.description && <p className="modal-description">{webinar.description}</p>}

        <div className="modal-info">
          <div className="info-item">
            <span className="info-icon">📅</span>
            <span className="info-text">{formatDate(webinar.event_datetime)}</span>
          </div>
          <div className="info-item">
            <span className="info-icon">🕐</span>
            <span className="info-text">{formatTime(webinar.event_datetime)}</span>
          </div>
          <div className="info-item">
            <span className="info-icon">💵</span>
            <span className="info-text">{webinar.price} ₽</span>
          </div>
          {webinar.location && (
            <div className="info-item">
              <span className="info-icon">📍</span>
              <span className="info-text">{webinar.location}</span>
            </div>
          )}
        </div>

        {webinar.is_purchased ? (
          <button className="modal-button purchased" onClick={handleAction}>
            Перейти в группу
          </button>
        ) : (
          <button className="modal-button" onClick={handleAction}>
            Купить билет
          </button>
        )}
      </div>
    </div>
  )
}

export default CourseModal
