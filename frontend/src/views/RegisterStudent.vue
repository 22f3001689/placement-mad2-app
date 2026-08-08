<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get, post } from '../api/http.js'

const router = useRouter()
const username = ref('')
const password = ref('')
const email = ref('')
const name = ref('')
const branchId = ref('')
const branches = ref([])
const error = ref('')

onMounted(async () => {
  branches.value = await get('/auth/branches')
})

async function onSubmit() {
  error.value = ''
  try {
    await post('/auth/register/student', {
      username: username.value,
      password: password.value,
      email: email.value,
      name: name.value,
      branch_id: branchId.value || null,
    })
    router.push('/login')
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div class="container" style="max-width: 400px; margin-top: 4rem">
    <h1 class="mb-4">Register as Student</h1>
    <form @submit.prevent="onSubmit">
      <div class="mb-3">
        <label class="form-label">Full name</label>
        <input v-model="name" type="text" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input v-model="username" type="text" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-control" minlength="6" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Branch</label>
        <select v-model="branchId" class="form-select">
          <option value="">Select a branch</option>
          <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.code }} - {{ b.name }}</option>
        </select>
      </div>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <button type="submit" class="btn btn-primary">Register</button>
    </form>
  </div>
</template>
