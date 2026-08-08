<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get, post } from '../api/http.js'
import { auth, logout } from '../state/auth.js'
import Modal from '../components/Modal.vue'
import {
  APPLICATION_STATUS_APPLIED,
  APPLICATION_STATUS_INTERVIEW,
  APPLICATION_STATUS_OFFER,
  APPLICATION_STATUS_PLACED,
  APPLICATION_STATUSES,
  JOB_POSITION_STATUS_COMPLETED,
  JOB_POSITION_STATUS_ONGOING,
  TERMINAL_APPLICATION_STATUSES,
} from '../constants.js'

const router = useRouter()

const upcomingDrives = ref([])
const closedDrives = ref([])
const showCreateDrive = ref(false)

function emptyDrive() {
  return {
    drive_name: '',
    title: '',
    description: '',
    eligibility_criteria: '',
    application_deadline: '',
  }
}

const newDrive = ref(emptyDrive())

const currentDrive = ref(null)
const applicationsForDrive = ref(null) // { drive, applications } or null
const selectedApplication = ref(null)

// "Placed" is set via the separate Mark-as-Placed form below, not this dropdown.
const decisionStatuses = APPLICATION_STATUSES.filter(
  (s) => ![APPLICATION_STATUS_APPLIED, APPLICATION_STATUS_PLACED].includes(s.value)
)
const isFinalStatus = (status) => TERMINAL_APPLICATION_STATUSES.includes(status)

const pendingStatus = ref('')
const pendingInterviewDatetime = ref('')
const placementJoiningDate = ref('')

const saveMessage = ref('')
function flashSaveMessage() {
  saveMessage.value = 'Record updated successfully'
  setTimeout(() => (saveMessage.value = ''), 2000)
}

async function loadDrives() {
  ;[upcomingDrives.value, closedDrives.value] = await Promise.all([
    get(`/company/drives?status=${JOB_POSITION_STATUS_ONGOING}`),
    get(`/company/drives?status=${JOB_POSITION_STATUS_COMPLETED}`),
  ])
}

async function createDrive() {
  await post('/company/drives', newDrive.value)
  showCreateDrive.value = false
  newDrive.value = emptyDrive()
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
  // The dropdown only offers decision statuses (no "applied"), so an application still
  // "applied" must default to the first selectable option to keep the select's visible
  // value in sync with pendingStatus - otherwise Save sees no diff and does nothing.
  pendingStatus.value = decisionStatuses.some((s) => s.value === selectedApplication.value.status)
    ? selectedApplication.value.status
    : decisionStatuses[0].value
  pendingInterviewDatetime.value = selectedApplication.value.interview_datetime || ''
  applicationsForDrive.value = null
}

async function backToApplications() {
  selectedApplication.value = null
  await openApplications(currentDrive.value)
}

async function saveDecision() {
  if (pendingInterviewDatetime.value && pendingInterviewDatetime.value !== selectedApplication.value.interview_datetime) {
    await post(`/company/applications/${selectedApplication.value.id}/interview`, {
      interview_datetime: pendingInterviewDatetime.value,
    })
    selectedApplication.value.interview_datetime = pendingInterviewDatetime.value
  }
  if (pendingStatus.value !== selectedApplication.value.status) {
    await post(`/company/applications/${selectedApplication.value.id}/decision`, {
      status: pendingStatus.value,
    })
    selectedApplication.value.status = pendingStatus.value
  }
  flashSaveMessage()
}

async function markPlaced() {
  await post(`/company/applications/${selectedApplication.value.id}/decision`, {
    status: APPLICATION_STATUS_PLACED,
    joining_date: placementJoiningDate.value,
  })
  selectedApplication.value.status = APPLICATION_STATUS_PLACED
  pendingStatus.value = APPLICATION_STATUS_PLACED
  placementJoiningDate.value = ''
  flashSaveMessage()
}

async function onLogout() {
  await logout()
  router.push('/login')
}

const showExports = ref(false)
const exportJobs = ref([])

async function loadExports() {
  exportJobs.value = await get('/company/exports')
}

async function requestExport() {
  await post('/company/exports')
  await loadExports()
}

async function openExports() {
  await loadExports()
  showExports.value = true
}

const showReports = ref(false)
const reportJobs = ref([])

async function openReports() {
  reportJobs.value = await get('/company/reports')
  showReports.value = true
}

onMounted(loadDrives)
</script>

<template>
  <div class="container" style="margin-top: 3rem">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1>Welcome {{ auth.user?.company_name }}</h1>
      <div>
        <button class="btn btn-primary me-2" @click="showCreateDrive = true">Create Drive</button>
        <button class="btn btn-outline-secondary me-2" @click="openExports">
          Export Applications
        </button>
        <button class="btn btn-outline-secondary me-2" @click="openReports">
          Placement Reports
        </button>
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

    <Modal :show="!!selectedApplication" title="Student Application" @close="backToApplications">
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
        <p><strong>Graduation Year:</strong> {{ selectedApplication.student_graduation_year }}</p>
        <p><strong>CGPA:</strong> {{ selectedApplication.student_cgpa }}</p>
        <p><strong>Skills:</strong> {{ selectedApplication.student_skills?.join(', ') }}</p>
        <p><strong>Contact:</strong> {{ selectedApplication.student_contact }}</p>
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

        <div v-if="isFinalStatus(selectedApplication.status)" class="mb-2">
          <span class="badge bg-secondary">Final status: {{ selectedApplication.status }}</span>
        </div>
        <template v-else>
          <div class="mb-2">
            <label class="form-label">Status</label>
            <select class="form-select" v-model="pendingStatus">
              <option v-for="s in decisionStatuses" :key="s.value" :value="s.value">
                {{ s.label }}
              </option>
            </select>
          </div>
          <div v-if="pendingStatus === APPLICATION_STATUS_INTERVIEW" class="mb-2">
            <label class="form-label">Interview Date/Time</label>
            <input
              type="datetime-local"
              class="form-control"
              v-model="pendingInterviewDatetime"
            />
          </div>
          <button class="btn btn-sm btn-primary mb-2" @click="saveDecision">Save</button>
          <Transition name="fade">
            <span v-if="saveMessage" class="text-success ms-2">{{ saveMessage }}</span>
          </Transition>

          <div v-if="selectedApplication.status === APPLICATION_STATUS_OFFER" class="card p-2 mb-2">
            <label class="form-label">Mark as Placed</label>
            <input v-model="placementJoiningDate" type="date" class="form-control mb-2" placeholder="Joining Date" />
            <button
              class="btn btn-sm btn-success"
              :disabled="!placementJoiningDate"
              @click="markPlaced"
            >
              Confirm Placement
            </button>
          </div>
        </template>
      </template>
    </Modal>

    <Modal :show="showExports" title="Export Applications" @close="showExports = false">
      <button class="btn btn-sm btn-primary mb-2" @click="requestExport">
        Request New Export
      </button>
      <button class="btn btn-sm btn-outline-secondary mb-2 ms-2" @click="loadExports">
        Refresh
      </button>
      <table class="table">
        <thead>
          <tr>
            <th>Requested</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in exportJobs" :key="job.id">
            <td>{{ job.created_at }}</td>
            <td>{{ job.status }}</td>
            <td>
              <a
                v-if="job.download_url"
                :href="job.download_url"
                download
                class="btn btn-sm btn-outline-primary"
              >
                Download
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </Modal>

    <Modal :show="showReports" title="Placement Reports" @close="showReports = false">
      <table class="table">
        <thead>
          <tr>
            <th>Period</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in reportJobs" :key="job.id">
            <td>{{ job.period_start }} – {{ job.period_end }}</td>
            <td>{{ job.status }}</td>
            <td>
              <a
                v-if="job.download_url"
                :href="job.download_url"
                download
                class="btn btn-sm btn-outline-primary"
              >
                Download
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </Modal>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
