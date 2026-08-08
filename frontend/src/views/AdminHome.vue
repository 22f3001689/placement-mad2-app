<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get, post } from '../api/http.js'
import { logout } from '../state/auth.js'
import Modal from '../components/Modal.vue'
import CollapsibleSection from '../components/CollapsibleSection.vue'
import { APPLICATION_STATUSES, COMPANY_APPROVAL_STATUSES, JOB_POSITION_STATUSES, statusLabel } from '../constants.js'

const router = useRouter()

const totals = ref(null)
const q = ref('')

const registeredCompanies = ref([])
const registeredStudents = ref([])
const pendingCompanies = ref([])
const ongoingDrives = ref([])
const applications = ref([])

const selectedDrive = ref(null)
const selectedApplication = ref(null)
const selectedStudent = ref(null)

async function viewStudentProfile(student) {
  selectedStudent.value = await get(`/admin/students/${student.id}`)
}

async function loadTotals() {
  totals.value = await get('/admin/dashboard')
}

async function loadRegisteredCompanies() {
  const query = q.value ? `&q=${encodeURIComponent(q.value)}` : ''
  registeredCompanies.value = await get(
    `/admin/companies?status=${COMPANY_APPROVAL_STATUSES[1].value}${query}`
  )
}

async function loadRegisteredStudents() {
  const query = q.value ? `?q=${encodeURIComponent(q.value)}` : ''
  registeredStudents.value = await get(`/admin/students${query}`)
}

async function loadPendingCompanies() {
  pendingCompanies.value = await get(
    `/admin/companies?status=${COMPANY_APPROVAL_STATUSES[0].value}`
  )
}

async function loadOngoingDrives() {
  ongoingDrives.value = await get(
    `/admin/job-positions?status=${JOB_POSITION_STATUSES[0].value}`
  )
}

async function loadApplications() {
  applications.value = await get('/admin/applications')
}

function onSearch() {
  loadRegisteredCompanies()
  loadRegisteredStudents()
}

async function decideCompany(company, status) {
  await post(`/admin/companies/${company.id}/decision`, { status })
  await Promise.all([loadPendingCompanies(), loadRegisteredCompanies(), loadTotals()])
}

async function toggleActive(account) {
  await post(`/admin/users/${account.user_id}/toggle-active`)
  await Promise.all([loadRegisteredCompanies(), loadRegisteredStudents()])
}

async function completeDrive(drive) {
  await post(`/admin/job-positions/${drive.id}/complete`)
  selectedDrive.value = null
  await loadOngoingDrives()
}

async function onLogout() {
  await logout()
  router.push('/login')
}

onMounted(() => {
  loadTotals()
  loadRegisteredCompanies()
  loadRegisteredStudents()
  loadPendingCompanies()
  loadOngoingDrives()
  loadApplications()
})
</script>

<template>
  <div class="container" style="margin-top: 3rem">
    <!-- Section 1: welcome, totals, search -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1>Welcome Admin</h1>
      <button class="btn btn-danger" @click="onLogout">Log out</button>
    </div>

    <div class="row g-3 mb-3" v-if="totals">
      <div class="col-md-3">
        <div class="card text-center p-2">
          <div class="fs-4">{{ totals.students }}</div>
          <div class="text-muted small">Students</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center p-2">
          <div class="fs-4">{{ totals.companies }}</div>
          <div class="text-muted small">Companies</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center p-2">
          <div class="fs-4">{{ totals.job_positions }}</div>
          <div class="text-muted small">Drives</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center p-2">
          <div class="fs-4">{{ totals.applications }}</div>
          <div class="text-muted small">Applications</div>
        </div>
      </div>
    </div>

    <form class="d-flex mb-4" @submit.prevent="onSearch">
      <input v-model="q" class="form-control me-2" placeholder="Search Students or Companies" />
      <button class="btn btn-outline-secondary" type="submit">Search</button>
    </form>

    <!-- Section 2: five collapsible subsections -->
    <CollapsibleSection title="Registered Companies">
      <table class="table">
        <tbody>
          <tr v-for="c in registeredCompanies" :key="c.id">
            <td>{{ c.company_name }}</td>
            <td class="text-end">
              <button
                class="btn btn-sm"
                :class="c.is_active ? 'btn-danger' : 'btn-success'"
                @click="toggleActive(c)"
              >
                {{ c.is_active ? 'Blacklist' : 'Whitelist' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </CollapsibleSection>

    <CollapsibleSection title="Registered Students">
      <table class="table">
        <tbody>
          <tr v-for="s in registeredStudents" :key="s.id">
            <td>{{ s.name }}</td>
            <td class="text-end">
              <button
                class="btn btn-sm btn-outline-primary me-1"
                @click="viewStudentProfile(s)"
              >
                View Profile
              </button>
              <button
                class="btn btn-sm"
                :class="s.is_active ? 'btn-danger' : 'btn-success'"
                @click="toggleActive(s)"
              >
                {{ s.is_active ? 'Blacklist' : 'Whitelist' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </CollapsibleSection>

    <CollapsibleSection title="Company Applications">
      <table class="table">
        <tbody>
          <tr v-for="c in pendingCompanies" :key="c.id">
            <td>{{ c.company_name }}</td>
            <td class="text-end">
              <button
                class="btn btn-sm btn-success me-1"
                @click="decideCompany(c, COMPANY_APPROVAL_STATUSES[1].value)"
              >
                Approve
              </button>
              <button
                class="btn btn-sm btn-outline-danger"
                @click="decideCompany(c, COMPANY_APPROVAL_STATUSES[2].value)"
              >
                Reject
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </CollapsibleSection>

    <CollapsibleSection title="Ongoing Drives">
      <table class="table">
        <thead>
          <tr>
            <th>#</th>
            <th>Drive Name</th>
            <th></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(d, i) in ongoingDrives" :key="d.id">
            <td>{{ i + 1 }}</td>
            <td>{{ d.title }}</td>
            <td><button class="btn btn-sm btn-outline-primary" @click="selectedDrive = d">View details</button></td>
            <td><button class="btn btn-sm btn-outline-success" @click="completeDrive(d)">Mark as complete</button></td>
          </tr>
        </tbody>
      </table>
    </CollapsibleSection>

    <CollapsibleSection title="Student Applications">
      <table class="table">
        <thead>
          <tr>
            <th>#</th>
            <th>Name</th>
            <th>Drive</th>
            <th>Company</th>
            <th>Date</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(a, i) in applications" :key="a.id">
            <td>{{ i + 1 }}</td>
            <td>{{ a.student_name }}</td>
            <td>{{ a.job_title }}</td>
            <td>{{ a.company_name }}</td>
            <td>{{ a.application_date }}</td>
            <td><button class="btn btn-sm btn-outline-primary" @click="selectedApplication = a">View</button></td>
          </tr>
        </tbody>
      </table>
    </CollapsibleSection>

    <Modal :show="!!selectedDrive" title="Drive Details" @close="selectedDrive = null">
      <template v-if="selectedDrive">
        <div class="row">
          <div class="col-8">
            <p><strong>Job Title:</strong> {{ selectedDrive.title }}</p>
            <p><strong>Job Description:</strong> {{ selectedDrive.description }}</p>
            <p><strong>Location:</strong> {{ selectedDrive.location }}</p>
            <p><strong>Salary:</strong> {{ selectedDrive.salary }}</p>
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
      </template>
    </Modal>

    <Modal :show="!!selectedApplication" title="Application Details" @close="selectedApplication = null">
      <template v-if="selectedApplication">
        <img
          v-if="selectedApplication.student_photo_url"
          :src="selectedApplication.student_photo_url"
          alt="Student photo"
          style="max-height: 4rem"
          class="mb-2"
        />
        <p><strong>Student:</strong> {{ selectedApplication.student_name }}</p>
        <p><strong>Drive:</strong> {{ selectedApplication.job_title }}</p>
        <p><strong>Company:</strong> {{ selectedApplication.company_name }}</p>
        <p><strong>Date:</strong> {{ selectedApplication.application_date }}</p>
        <p><strong>Status:</strong> {{ selectedApplication.status }}</p>
        <a
          v-if="selectedApplication.student_resume_url"
          :href="selectedApplication.student_resume_url"
          download
          class="btn btn-sm btn-outline-primary"
        >
          View Resume
        </a>
      </template>
    </Modal>

    <Modal :show="!!selectedStudent" title="Student Profile" @close="selectedStudent = null">
      <template v-if="selectedStudent">
        <img
          v-if="selectedStudent.photo_url"
          :src="selectedStudent.photo_url"
          alt="Student photo"
          style="max-height: 4rem"
          class="mb-2"
        />
        <p><strong>Name:</strong> {{ selectedStudent.name }}</p>
        <p><strong>Branch:</strong> {{ selectedStudent.branch?.name }}</p>
        <p><strong>Graduation Year:</strong> {{ selectedStudent.graduation_year }}</p>
        <p><strong>CGPA:</strong> {{ selectedStudent.cgpa }}</p>
        <p><strong>Skills:</strong> {{ selectedStudent.skills.map((s) => s.name).join(', ') }}</p>
        <p><strong>Contact:</strong> {{ selectedStudent.contact }}</p>
        <a
          v-if="selectedStudent.resume_url"
          :href="selectedStudent.resume_url"
          download
          class="btn btn-sm btn-outline-primary mb-2"
        >
          View Resume
        </a>
        <h5>Application History</h5>
        <table class="table">
          <thead>
            <tr>
              <th>Job Title</th>
              <th>Company</th>
              <th>Status</th>
              <th>Date</th>
              <th>Placement</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in selectedStudent.applications" :key="a.id">
              <td>{{ a.job_title }}</td>
              <td>{{ a.company_name }}</td>
              <td>{{ statusLabel(APPLICATION_STATUSES, a.status) }}</td>
              <td>{{ a.application_date }}</td>
              <td>
                <span v-if="a.placement">{{ a.placement.position_title }}</span>
                <span v-else>—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </template>
    </Modal>
  </div>
</template>
