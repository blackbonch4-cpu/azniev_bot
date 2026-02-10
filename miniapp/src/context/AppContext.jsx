import { createContext, useState, useEffect, useContext } from 'react'
import WebApp from '@twa-dev/sdk'
import { getWebinars, getUserProfile, getSettings } from '../api/api'

export const AppContext = createContext()

// ADMIN_IDS должен совпадать с .env на сервере
const ADMIN_IDS = import.meta.env.VITE_ADMIN_IDS ?
  import.meta.env.VITE_ADMIN_IDS.split(',').map(id => parseInt(id.trim())) :
  [398130967] // Временно, замените на свой ID

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [webinars, setWebinars] = useState([])
  const [settings, setSettings] = useState({})
  const [loading, setLoading] = useState(true)
  const [isAdmin, setIsAdmin] = useState(false)

  useEffect(() => {
    initApp()
  }, [])

  const initApp = async () => {
    try {
      // Получаем пользователя из Telegram
      const tgUser = WebApp.initDataUnsafe?.user
      setUser(tgUser)

      // Проверяем, админ ли пользователь
      if (tgUser && ADMIN_IDS.includes(tgUser.id)) {
        setIsAdmin(true)
      }

      // Загружаем данные параллельно
      const [profileData, webinarsData, settingsData] = await Promise.all([
        getUserProfile().catch(() => null),
        getWebinars().catch(() => ({ webinars: [] })),
        getSettings().catch(() => ({ social_links: {} }))
      ])

      if (profileData) {
        setProfile(profileData.user)
      }
      setWebinars(webinarsData.webinars || [])
      setSettings(settingsData.social_links || {})
    } catch (error) {
      console.error('Error initializing app:', error)
    } finally {
      setLoading(false)
    }
  }

  const refreshWebinars = async () => {
    try {
      const data = await getWebinars()
      setWebinars(data.webinars || [])
    } catch (error) {
      console.error('Error refreshing webinars:', error)
    }
  }

  const refreshSettings = async () => {
    try {
      const data = await getSettings()
      setSettings(data.social_links || {})
    } catch (error) {
      console.error('Error refreshing settings:', error)
    }
  }

  return (
    <AppContext.Provider value={{
      user,
      profile,
      webinars,
      settings,
      loading,
      isAdmin,
      refreshWebinars,
      refreshSettings
    }}>
      {children}
    </AppContext.Provider>
  )
}

export const useApp = () => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}
