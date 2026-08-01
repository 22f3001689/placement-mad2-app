<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth, login } from '../state/auth.js'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')

async function onSubmit() {
  error.value = ''
  try {
    await login(username.value, password.value)
    router.push(`/${auth.user.role}`)
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div class="container" style="max-width: 400px; margin-top: 4rem">
    <h1 class="mb-4">Log in</h1>
    <form @submit.prevent="onSubmit">
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input v-model="username" type="text" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <button type="submit" class="btn btn-primary">Log in</button>
    </form>
    <p class="mt-3">
      Not registered?
      <router-link to="/register/student">Register as Student</router-link>
      or
      <router-link to="/register/company">Register as Company</router-link>
    </p>
  </div>
</template>
