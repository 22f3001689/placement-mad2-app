<script setup>
import { ref, onMounted } from 'vue'
import { get, post, postForm } from '../api/http.js'
import { auth } from '../state/auth.js'
import Modal from '../components/Modal.vue'
import { APPLICATION_STATUSES, EXPORT_JOB_STATUSES, statusLabel } from '../constants.js'

const organizations = ref([])
const applications = ref([])
const q = ref('')

const showEditProfile = ref(false)
const profile = ref(null)
const profilePhoto = ref(null)
const profileResume = ref(null)
const branches = ref([])
const selectedBranchId = ref('')
const skillOptions = ref([])
const selectedSkillIds = ref([])

const selectedOrganization = ref(null)
const organizationDrives = ref([])

const selectedDrive = ref(null)

const showHistory = ref(false)
const hasPlacement = ref(false)

const showExports = ref(false)
const exportJobs = ref([])

async function loadExports() {
  exportJobs.value = await get('/student/exports')
}

async function requestExport() {
  await post('/student/exports')
  await loadExports()
}

async function openExports() {
  await loadExports()
  showExports.value = true
}

async function checkPlacement() {
  const res = await fetch('/api/student/placement/confirmation', { credentials: 'include' })
  hasPlacement.value = res.ok
}

async function loadOrganizations() {
  const query = q.value ? `?q=${encodeURIComponent(q.value)}` : ''
  organizations.value = await get(`/student/organizations${query}`)
}

async function loadApplications() {
  applications.value = await get('/student/applications')
}

async function openEditProfile() {
  profile.value = await get('/student/profile')
  selectedBranchId.value = profile.value.branch?.id || ''
  selectedSkillIds.value = profile.value.skills.map((s) => s.id)
  if (!branches.value.length) branches.value = await get('/auth/branches')
  if (!skillOptions.value.length) skillOptions.value = await get('/auth/skills')
  showEditProfile.value = true
}

async function saveProfile() {
  const formData = new FormData()
  formData.set('name', profile.value.name || '')
  if (selectedBranchId.value) formData.set('branch_id', selectedBranchId.value)
  formData.set('graduation_year', profile.value.graduation_year || '')
  formData.set('cgpa', profile.value.cgpa || '')
  selectedSkillIds.value.forEach((id) => formData.append('skill_ids', id))
  formData.set('contact', profile.value.contact || '')
  if (profilePhoto.value) formData.set('photo', profilePhoto.value)
  if (profileResume.value) formData.set('resume', profileResume.value)

  profile.value = await postForm('/student/profile', formData)
  profilePhoto.value = null
  profileResume.value = null
  showEditProfile.value = false
}

async function openOrganization(org) {
  ;[selectedOrganization.value, organizationDrives.value] = await Promise.all([
    get(`/student/organizations/${org.id}`),
    get(`/student/drives?company_id=${org.id}`),
  ])
}

async function openDrive(drive) {
  selectedDrive.value = await get(`/student/drives/${drive.id}`)
  selectedOrganization.value = null
}

async function applyToDrive() {
  await post(`/student/drives/${selectedDrive.value.id}/apply`)
  selectedDrive.value.already_applied = true
  await loadApplications()
}

onMounted(() => {
  loadOrganizations()
  loadApplications()
  checkPlacement()
})
</script>

<template>
  <div class="container" style="margin-top: 3rem">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1>Welcome {{ auth.user?.student_name }}</h1>
      <div>
        <button class="btn btn-outline-secondary me-2" @click="openEditProfile">Edit Profile</button>
        <button class="btn btn-outline-secondary me-2" @click="showHistory = true">History</button>
        <button class="btn btn-outline-secondary me-2" @click="openExports">
          Export My Applications
        </button>
        <a
          v-if="hasPlacement"
          href="/api/student/placement/confirmation"
          download
          class="btn btn-outline-success me-2"
        >
          Download Placement Confirmation
        </a>
      </div>
    </div>

    <form class="d-flex mb-4" @submit.prevent="loadOrganizations">
      <input v-model="q" class="form-control me-2" placeholder="Search companies / skills" />
      <button class="btn btn-outline-secondary" type="submit">Search</button>
    </form>

    <h3>Organizations</h3>
    <table class="table">
      <tbody>
        <tr v-for="org in organizations" :key="org.id">
          <td>{{ org.company_name }}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-primary" @click="openOrganization(org)">View Details</button>
          </td>
        </tr>
      </tbody>
    </table>

    <h3>Applied Drives</h3>
    <table class="table">
      <thead>
        <tr>
          <th>Sr No.</th>
          <th>Drive Name</th>
          <th>Company</th>
          <th>Date</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(a, i) in applications" :key="a.id">
          <td>{{ i + 1 }}</td>
          <td>{{ a.drive_name }}</td>
          <td>{{ a.company_name }}</td>
          <td>{{ a.application_date }}</td>
          <td>
            <button
              class="btn btn-sm btn-outline-primary"
              @click="openDrive({ id: a.job_position_id })"
            >
              View Details
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <Modal :show="showEditProfile" title="Edit Profile" @close="showEditProfile = false">
      <form v-if="profile" @submit.prevent="saveProfile">
        <div class="mb-2">
          <label class="form-label">Name</label>
          <input v-model="profile.name" class="form-control" />
        </div>
        <div class="mb-2">
          <label class="form-label">Branch</label>
          <select v-model="selectedBranchId" class="form-select">
            <option value="">Select a branch</option>
            <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.code }} - {{ b.name }}</option>
          </select>
        </div>
        <div class="mb-2">
          <label class="form-label">Graduation Year</label>
          <input v-model="profile.graduation_year" type="number" class="form-control" />
        </div>
        <div class="mb-2">
          <label class="form-label">CGPA</label>
          <input v-model="profile.cgpa" type="number" step="0.01" class="form-control" />
        </div>
        <div class="mb-2">
          <label class="form-label">Skills</label>
          <select v-model="selectedSkillIds" class="form-select" multiple>
            <option v-for="s in skillOptions" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div class="mb-2">
          <label class="form-label">Contact</label>
          <input v-model="profile.contact" class="form-control" />
        </div>
        <div class="mb-2">
          <label class="form-label">Photo</label>
          <input type="file" class="form-control" @change="profilePhoto = $event.target.files[0]" />
        </div>
        <div class="mb-2">
          <label class="form-label">Resume</label>
          <input type="file" class="form-control" @change="profileResume = $event.target.files[0]" />
        </div>
        <button type="submit" class="btn btn-success">Save</button>
      </form>
    </Modal>

    <Modal
      :show="!!selectedOrganization"
      :title="selectedOrganization?.company_name || ''"
      @close="selectedOrganization = null"
    >
      <template v-if="selectedOrganization">
        <img
          v-if="selectedOrganization.logo_url"
          :src="selectedOrganization.logo_url"
          alt="Company logo"
          style="max-height: 4rem"
          class="mb-2"
        />
        <h5>Overview</h5>
        <p>{{ selectedOrganization.overview }}</p>
        <h5>Current Drives</h5>
        <div v-for="d in organizationDrives" :key="d.id" class="d-flex justify-content-between align-items-center mb-2">
          <span>{{ d.drive_name }}</span>
          <button class="btn btn-sm btn-outline-primary" @click="openDrive(d)">View Details</button>
        </div>
      </template>
    </Modal>

    <Modal :show="!!selectedDrive" :title="selectedDrive?.drive_name || ''" @close="selectedDrive = null">
      <template v-if="selectedDrive">
        <div class="row">
          <div class="col-8">
            <p><strong>Job Title:</strong> {{ selectedDrive.title }}</p>
            <p><strong>Job Description:</strong> {{ selectedDrive.description }}</p>
            <p><strong>Eligibility Criteria:</strong> {{ selectedDrive.eligibility_criteria }}</p>
            <p><strong>Location:</strong> {{ selectedDrive.location }}</p>
            <p><strong>Salary:</strong> {{ selectedDrive.salary }}</p>
            <p><strong>Skills Required:</strong> {{ selectedDrive.skills?.map((s) => s.name).join(', ') }}</p>
          </div>
          <div class="col-4 text-center">
            <img
              v-if="selectedDrive.company_logo_url"
              :src="selectedDrive.company_logo_url"
              alt="Company logo"
              style="max-height: 4rem"
              class="mb-2"
            />
            <div>{{ selectedDrive.company_name }}</div>
          </div>
        </div>
        <button
          v-if="!selectedDrive.already_applied"
          class="btn btn-sm btn-primary"
          @click="applyToDrive"
        >
          Apply
        </button>
        <span v-else class="badge bg-secondary">Already Applied</span>
      </template>
    </Modal>

    <Modal :show="showHistory" title="Student Application History" @close="showHistory = false">
      <p><strong>Student Name:</strong> {{ profile?.name || auth.user?.username }}</p>
      <p><strong>Department:</strong> {{ profile?.branch?.name }}</p>
      <table class="table">
        <thead>
          <tr>
            <th>Drive No.</th>
            <th>Interview</th>
            <th>Job Title</th>
            <th>Results</th>
            <th>Remark</th>
            <th>Placement</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(a, i) in applications" :key="a.id">
            <td>{{ i + 1 }}</td>
            <td>{{ a.interview_mode || 'Not scheduled' }}</td>
            <td>{{ a.job_title }}</td>
            <td>{{ statusLabel(APPLICATION_STATUSES, a.status) }}</td>
            <td>{{ a.company_remark || 'None' }}</td>
            <td>
              <span v-if="a.placement">
                {{ a.placement.position_title }} · ₹{{ a.placement.salary }} · joining
                {{ a.placement.joining_date }}
              </span>
              <span v-else>—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </Modal>

    <Modal :show="showExports" title="Export My Applications" @close="showExports = false">
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
            <td>{{ statusLabel(EXPORT_JOB_STATUSES, job.status) }}</td>
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
