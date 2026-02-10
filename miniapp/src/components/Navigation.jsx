import { useNavigate, useLocation } from 'react-router-dom'
import { useApp } from '../context/AppContext'
import './Navigation.css'

function Navigation() {
  const navigate = useNavigate()
  const location = useLocation()
  const { isAdmin } = useApp()

  const isActive = (path) => location.pathname === path

  return (
    <nav className="bottom-navigation">
      <button
        className={`nav-item ${isActive('/') ? 'active' : ''}`}
        onClick={() => navigate('/')}
      >
        <span className="nav-icon">🏠</span>
        <span className="nav-label">Главная</span>
      </button>

      {isAdmin && (
        <button
          className={`nav-item ${isActive('/admin') ? 'active' : ''}`}
          onClick={() => navigate('/admin')}
        >
          <span className="nav-icon">⚙️</span>
          <span className="nav-label">Админ</span>
        </button>
      )}

      <button
        className={`nav-item ${isActive('/purchases') ? 'active' : ''}`}
        onClick={() => navigate('/purchases')}
      >
        <span className="nav-icon">🎫</span>
        <span className="nav-label">Покупки</span>
      </button>

      <button
        className={`nav-item ${isActive('/support') ? 'active' : ''}`}
        onClick={() => navigate('/support')}
      >
        <span className="nav-icon">💬</span>
        <span className="nav-label">Поддержка</span>
      </button>
    </nav>
  )
}

export default Navigation
