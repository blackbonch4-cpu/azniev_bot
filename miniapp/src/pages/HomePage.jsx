import { useState } from 'react'
import { useApp } from '../context/AppContext'
import Header from '../components/Header'
import CourseCard from '../components/CourseCard'
import CourseModal from '../components/CourseModal'
import './HomePage.css'

function HomePage() {
  const { webinars, settings, loading } = useApp()
  const [selectedWebinar, setSelectedWebinar] = useState(null)

  if (loading) {
    return <div className="page loading">Загрузка...</div>
  }

  return (
    <div className="page">
      <Header />

      <div className="courses-gallery">
        {webinars.length === 0 ? (
          <div className="empty-state">Нет доступных курсов</div>
        ) : (
          webinars.map(webinar => (
            <CourseCard
              key={webinar.id}
              webinar={webinar}
              onClick={setSelectedWebinar}
            />
          ))
        )}
      </div>

      {(settings.instagram || settings.telegram || settings.website) && (
        <div className="social-links">
          <h3>Мы в соцсетях</h3>
          <div className="social-buttons">
            {settings.instagram && (
              <a href={settings.instagram} target="_blank" rel="noreferrer" className="social-button">
                📷 Instagram
              </a>
            )}
            {settings.telegram && (
              <a href={settings.telegram} target="_blank" rel="noreferrer" className="social-button">
                ✈️ Telegram
              </a>
            )}
            {settings.website && (
              <a href={settings.website} target="_blank" rel="noreferrer" className="social-button">
                🌐 Сайт
              </a>
            )}
          </div>
        </div>
      )}

      {selectedWebinar && (
        <CourseModal
          webinar={selectedWebinar}
          onClose={() => setSelectedWebinar(null)}
        />
      )}
    </div>
  )
}

export default HomePage
