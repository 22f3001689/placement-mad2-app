<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get, post } from '../api/http.js'
import { auth, logout } from '../state/auth.js'
import Modal from '../components/Modal.vue'

const router = useRouter()

const upcomingDrives = ref([])
const closedDrives = ref([])
const showCreateDrive = ref(false)
const newDrive = ref({
  drive_name: '',
  title: '',
  description: '',
  eligibility_criteria: '',
  application_deadline: '',
})

const currentDrive = ref(null)
const applicationsForDrive = ref(null) // { drive, applications } or null
const selectedApplication = ref(null)

async function loadDrives() {
  upcomingDrives.value = await get('/company/drives?status=ongoing')
  closedDrives.value = await get('/company/drives?status=completed')
}

async function createDrive() {
  await post('/company/drives', newDrive.value)
  showCreateDrive.value = false
  newDrive.value = {
    drive_name: '',
    title: '',
    description: '',
    eligibility_criteria: '',
    application_deadline: '',
  }
  await loadDrives()
}

async function completeDrive(drive) {
  await post(`/company/drives/${drive.id}/complete`)
  await loadDrives()
}

async function openApplications(drive) {
  currentDrive.value = drive
  applicationsForDrive.value = await get(`/company/drives/${drive.id}/applications`)
}

async function reviewApplication(application) {
  selectedApplication.value = await get(`/company/applications/${application.id}`)
  applicationsForDrive.value = null
}

async function backToApplications() {
  selectedApplication.value = null
  await openApplications(currentDrive.value)
}

async function setStatus(status) {
  await post(`/company/applications/${selectedApplication.value.id}/decision`, { status })
  selectedApplication.value.status = status
}

async function setInterview(interviewDatetime) {
  await post(`/company/applications/${selectedApplication.value.id}/interview`, {
    interview_datetime: interviewDatetime,
  })
  selectedApplication.value.interview_datetime = interviewDatetime
}

async function onLogout() {
  await logout()
  router.push('/login')
}

onMounted(loadDrives)
</script>

<template>
  <div class="container" style="margin-top: 3rem">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1>Welcome {{ auth.user?.company_name }}</h1>
      <div>
        <button class="btn btn-primary me-2" @click="showCreateDrive = true">Create Drive</button>
        <button class="btn btn-danger" @click="onLogout">Log out</button>
      </div>
    </div>

    <h3>Upcoming Drives</h3>
    <table class="table">
      <thead>
        <tr>
          <th>Sr No.</th>
          <th>Drive Name</th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(d, i) in upcomingDrives" :key="d.id">
          <td>{{ i + 1 }}</td>
          <td>{{ d.drive_name }}</td>
          <td><button class="btn btn-sm btn-outline-primary" @click="openApplications(d)">View Details</button></td>
          <td><button class="btn btn-sm btn-outline-success" @click="completeDrive(d)">Mark as Complete</button></td>
        </tr>
      </tbody>
    </table>

    <h3>Closed Drives</h3>
    <table class="table">
      <thead>
        <tr>
          <th>Sr No.</th>
          <th>Drive Name</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(d, i) in closedDrives" :key="d.id">
          <td>{{ i + 1 }}</td>
          <td>{{ d.drive_name }}</td>
          <td><button class="btn btn-sm btn-outline-primary" @click="openApplications(d)">Update</button></td>
        </tr>
      </tbody>
    </table>

    <Modal :show="showCreateDrive" title="Create a Drive" @close="showCreateDrive = false">
      <form @submit.prevent="createDrive">
        <div class="mb-2">
          <label class="form-label">Drive Name</label>
          <input v-model="newDrive.drive_name" class="form-control" required />
        </div>
        <div class="mb-2">
          <label class="form-label">Job Title</label>
          <input v-model="newDrive.title" class="form-control" required />
        </div>
        <div class="mb-2">
          <label class="form-label">Job Description</label>
          <textarea v-model="newDrive.description" class="form-control"></textarea>
        </div>
        <div class="mb-2">
          <label class="form-label">Eligibility Criteria</label>
          <input v-model="newDrive.eligibility_criteria" class="form-control" />
        </div>
        <div class="mb-2">
          <label class="form-label">Application Deadline</label>
          <input v-model="newDrive.application_deadline" type="datetime-local" class="form-control" required />
        </div>
        <button type="submit" class="btn btn-success">Save</button>
      </form>
    </Modal>

    <Modal
      :show="!!applicationsForDrive"
      :title="`Update Applications for the Drive — ${currentDrive?.title || ''}`"
      @close="applicationsForDrive = null; currentDrive = null"
    >
      <template v-if="applicationsForDrive">
        <div v-for="a in applicationsForDrive" :key="a.id" class="d-flex justify-content-between align-items-center mb-2">
          <span>{{ a.student_name }}</span>
          <button class="btn btn-sm btn-outline-primary" @click="reviewApplication(a)">Review Application</button>
        </div>
      </template>
    </Modal>

    <Modal :show="!!selectedApplication" title="Student Application" @close="selectedApplication = null">
      <template v-if="selectedApplication">
        <img
          v-if="selectedApplication.student_photo_url"
          :src="selectedApplication.student_photo_url"
          alt="Student photo"
          style="max-height: 4rem"
          class="mb-2"
        />
        <p><strong>Student Name:</strong> {{ selectedApplication.student_name }}</p>
        <p><strong>Department:</strong> {{ selectedApplication.student_branch }}</p>
        <p><strong>CGPA:</strong> {{ selectedApplication.student_cgpa }}</p>
        <p><strong>Skills:</strong> {{ selectedApplication.student_skills?.join(', ') }}</p>
        <p><strong>Drive:</strong> {{ selectedApplication.drive_name }}</p>
        <p><strong>Job Title:</strong> {{ selectedApplication.job_title }}</p>
        <a
          v-if="selectedApplication.student_resume_url"
          :href="selectedApplication.student_resume_url"
          download
          class="btn btn-sm btn-outline-primary mb-2"
        >
          View Resume
        </a>
        <div class="mb-2">
          <label class="form-label">Status</label>
          <select
            class="form-select"
            :value="selectedApplication.status"
            @change="setStatus($event.target.value)"
          >
            <option value="applied">Applied</option>
            <option value="shortlisted">Shortlist</option>
            <option value="waiting">Waiting</option>
            <option value="selected">Select</option>
            <option value="rejected">Reject</option>
          </select>
        </div>
        <div class="mb-2">
          <label class="form-label">Interview Date/Time</label>
          <input
            type="datetime-local"
            class="form-control"
            :value="selectedApplication.interview_datetime"
            @change="setInterview($event.target.value)"
          />
        </div>
        <button class="btn btn-sm btn-secondary" @click="backToApplications">Back</button>
      </template>
    </Modal>
  </div>
</template>
