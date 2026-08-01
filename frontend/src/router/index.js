import { createRouter, createWebHistory } from 'vue-router'
import { auth, fetchMe } from '../state/auth.js'
import Login from '../views/Login.vue'
import RegisterStudent from '../views/RegisterStudent.vue'
import RegisterCompany from '../views/RegisterCompany.vue'
import AdminHome from '../views/AdminHome.vue'
import CompanyHome from '../views/CompanyHome.vue'
import StudentHome from '../views/StudentHome.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/register/student', component: RegisterStudent },
  { path: '/register/company', component: RegisterCompany },
  { path: '/admin', component: AdminHome, meta: { role: 'admin' } },
  { path: '/company', component: CompanyHome, meta: { role: 'company' } },
  { path: '/student', component: StudentHome, meta: { role: 'student' } },
  { path: '/', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  if (!auth.checked) {
    await fetchMe()
  }

  const requiredRole = to.meta.role
  if (!requiredRole) {
    return true
  }

  if (!auth.user) {
    return '/login'
  }

  if (auth.user.role !== requiredRole) {
    // Logged in, but as the wrong role - send them to their own home instead.
    return `/${auth.user.role}`
  }

  return true
})

export default router
