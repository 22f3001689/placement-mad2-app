<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get } from '../api/http.js'
import { logout } from '../state/auth.js'

const router = useRouter()
const message = ref('')
const approvalStatus = ref('')

onMounted(async () => {
  const res = await get('/company/ping')
  message.value = res.message
  approvalStatus.value = res.approval_status
})

async function onLogout() {
  await logout()
  router.push('/login')
}
</script>

<template>
  <div class="container" style="margin-top: 4rem">
    <h1>Company Home</h1>
    <p>{{ message }}</p>
    <p>
      Approval status:
      <span
        class="badge"
        :class="approvalStatus === 'approved' ? 'bg-success' : 'bg-warning text-dark'"
      >
        {{ approvalStatus }}
      </span>
    </p>
    <button class="btn btn-secondary" @click="onLogout">Log out</button>
  </div>
</template>
