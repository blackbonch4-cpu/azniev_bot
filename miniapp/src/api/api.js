import axios from 'axios'
import WebApp from '@twa-dev/sdk'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1'

// Получить Telegram ID текущего пользователя
const getTelegramId = () => {
  return WebApp.initDataUnsafe?.user?.id
}

// Получить заголовки с Telegram данными
const getHeaders = () => {
  return {
    'Content-Type': 'application/json',
    'X-Telegram-Init-Data': WebApp.initData
  }
}

// ===== PUBLIC API =====

export const getWebinars = async () => {
  const telegramId = getTelegramId()
  const response = await axios.get(`${API_URL}/webinars`, {
    params: { telegram_id: telegramId },
    headers: getHeaders()
  })
  return response.data
}

export const getUserPurchases = async () => {
  const telegramId = getTelegramId()
  const response = await axios.get(`${API_URL}/purchases`, {
    params: { telegram_id: telegramId },
    headers: getHeaders()
  })
  return response.data
}

export const getUserProfile = async () => {
  const telegramId = getTelegramId()
  const response = await axios.get(`${API_URL}/profile`, {
    params: { telegram_id: telegramId },
    headers: getHeaders()
  })
  return response.data
}

export const getSettings = async () => {
  const response = await axios.get(`${API_URL}/settings`, {
    headers: getHeaders()
  })
  return response.data
}

export const sendSupportTicket = async (question) => {
  const telegramId = getTelegramId()
  const response = await axios.post(`${API_URL}/support/ticket`, {
    telegram_id: telegramId,
    question
  }, {
    headers: getHeaders()
  })
  return response.data
}

// ===== ADMIN API =====

export const createWebinar = async (webinarData) => {
  const telegramId = getTelegramId()
  const response = await axios.post(`${API_URL}/admin/webinars`, {
    telegram_id: telegramId,
    ...webinarData
  }, {
    headers: getHeaders()
  })
  return response.data
}

export const updateWebinar = async (webinarId, webinarData) => {
  const telegramId = getTelegramId()
  const response = await axios.put(`${API_URL}/admin/webinars/${webinarId}`, {
    telegram_id: telegramId,
    ...webinarData
  }, {
    headers: getHeaders()
  })
  return response.data
}

export const deleteWebinar = async (webinarId) => {
  const telegramId = getTelegramId()
  const response = await axios.delete(`${API_URL}/admin/webinars/${webinarId}`, {
    params: { telegram_id: telegramId },
    headers: getHeaders()
  })
  return response.data
}

export const uploadImage = async (imageBase64) => {
  const telegramId = getTelegramId()
  const response = await axios.post(`${API_URL}/admin/upload`, {
    telegram_id: telegramId,
    image: imageBase64
  }, {
    headers: getHeaders()
  })
  return response.data
}

export const updateSocialLinks = async (socialLinks) => {
  const telegramId = getTelegramId()
  const response = await axios.post(`${API_URL}/admin/social-links`, {
    telegram_id: telegramId,
    ...socialLinks
  }, {
    headers: getHeaders()
  })
  return response.data
}
