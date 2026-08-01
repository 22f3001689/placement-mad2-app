import { reactive } from 'vue'
import { get, post } from '../api/http.js'

export const auth = reactive({
  user: null, // { username, role, approval_status? } or null when logged out
  checked: false, // whether fetchMe() has resolved at least once
})

export async function fetchMe() {
  try {
    auth.user = await get('/auth/me')
  } catch {
    auth.user = null
  } finally {
    auth.checked = true
  }
}

export async function login(username, password) {
  auth.user = await post('/auth/login', { username, password })
  auth.checked = true
}

export async function logout() {
  await post('/auth/logout', {})
  auth.user = null
}
