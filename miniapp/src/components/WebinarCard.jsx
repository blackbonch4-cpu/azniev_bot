import './WebinarCard.css'

function WebinarCard({ webinar }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleClick = () => {
    if (webinar.purchased && webinar.group_link) {
      window.open(webinar.group_link, '_blank')
    }
  }

  return (
    <div
      className={`webinar-card ${webinar.purchased ? 'purchased' : ''}`}
      onClick={handleClick}
      style={{ cursor: webinar.purchased ? 'pointer' : 'default' }}
    >
      <div className="webinar-header">
        <h3 className="webinar-title">{webinar.title}</h3>
        {webinar.purchased && <span className="badge">✅ Куплено</span>}
      </div>

      {webinar.description && (
        <p className="webinar-description">{webinar.description}</p>
      )}

      <div className="webinar-info">
        <div className="info-row">
          <span className="info-label">📅 Дата:</span>
          <span className="info-value">{formatDate(webinar.event_datetime)}</span>
        </div>

        <div className="info-row">
          <span className="info-label">💵 Цена:</span>
          <span className="info-value">{webinar.price} ₽</span>
        </div>

        {webinar.location && (
          <div className="info-row">
            <span className="info-label">📍 Место:</span>
            <span className="info-value">{webinar.location}</span>
          </div>
        )}
      </div>

      {webinar.purchased && webinar.group_link && (
        <div className="webinar-footer">
          <span className="link-hint">👥 Нажмите для перехода в группу</span>
        </div>
      )}
    </div>
  )
}

export default WebinarCard
