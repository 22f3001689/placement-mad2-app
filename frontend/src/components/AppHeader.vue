<script setup>
import { useRouter } from 'vue-router'
import { auth, logout } from '../state/auth.js'

const router = useRouter()

async function onLogout() {
  await logout()
  router.push('/login')
}
</script>

<template>
  <header class="d-flex justify-content-between align-items-center px-4 py-2 border-bottom bg-light">
    <span class="fw-semibold">Placement Portal Application</span>
    <button v-if="auth.user" class="btn btn-sm btn-outline-danger" @click="onLogout">Log out</button>
  </header>
</template>
