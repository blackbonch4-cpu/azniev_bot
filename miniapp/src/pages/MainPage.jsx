import { useState, useEffect } from 'react'
import { getWebinars } from '../api/api'
import WebinarCard from '../components/WebinarCard'

function MainPage({ user }) {
  const [webinars, setWebinars] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadWebinars()
  }, [user])

  const loadWebinars = async () => {
    if (!user) return

    try {
      setLoading(true)
      const data = await getWebinars(user.id)
      setWebinars(data)
    } catch (err) {
      setError('Ошибка загрузки вебинаров')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="page"><div className="loading">Загрузка...</div></div>
  }

  if (error) {
    return <div className="page"><div className="error">{error}</div></div>
  }

  return (
    <div className="page">
      <h1 className="page-title">🎓 Мои Вебинары</h1>

      {webinars.length === 0 ? (
        <div className="empty">Нет доступных вебинаров</div>
      ) : (
        <div className="webinars-list">
          {webinars.map((webinar) => (
            <WebinarCard key={webinar.id} webinar={webinar} />
          ))}
        </div>
      )}
    </div>
  )
}

export default MainPage
