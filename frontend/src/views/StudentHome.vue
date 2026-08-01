<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get } from '../api/http.js'
import { logout } from '../state/auth.js'

const router = useRouter()
const message = ref('')

onMounted(async () => {
  const res = await get('/student/ping')
  message.value = res.message
})

async function onLogout() {
  await logout()
  router.push('/login')
}
</script>

<template>
  <div class="container" style="margin-top: 4rem">
    <h1>Student Home</h1>
    <p>{{ message }}</p>
    <button class="btn btn-secondary" @click="onLogout">Log out</button>
  </div>
</template>
