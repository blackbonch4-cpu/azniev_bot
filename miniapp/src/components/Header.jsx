import { useApp } from '../context/AppContext'
import { useNavigate } from 'react-router-dom'
import './Header.css'

function Header() {
  const { profile, user, isAdmin } = useApp()
  const navigate = useNavigate()

  const getAvatarUrl = () => {
    return profile?.avatar_url || `https://ui-avatars.com/api/?name=${user?.first_name || 'User'}&background=random`
  }

  return (
    <header className="app-header">
      <div className="header-profile" onClick={() => navigate('/profile')}>
        <img
          src={getAvatarUrl()}
          alt="Avatar"
          className="header-avatar"
        />
      </div>
      <div className="header-title">
        {isAdmin && <span className="admin-badge">👑 Админ</span>}
        Вебинары
      </div>
      <div className="header-spacer"></div>
    </header>
  )
}

export default Header
