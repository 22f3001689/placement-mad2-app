<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { get, post } from '../api/http.js'
import { logout } from '../state/auth.js'
import Modal from '../components/Modal.vue'
import CollapsibleSection from '../components/CollapsibleSection.vue'

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

async function loadTotals() {
  totals.value = await get('/admin/dashboard')
}

async function loadRegisteredCompanies() {
  const query = q.value ? `&q=${encodeURIComponent(q.value)}` : ''
  registeredCompanies.value = await get(`/admin/companies?status=approved${query}`)
}

async function loadRegisteredStudents() {
  const query = q.value ? `?q=${encodeURIComponent(q.value)}` : ''
  registeredStudents.value = await get(`/admin/students${query}`)
}

async function loadPendingCompanies() {
  pendingCompanies.value = await get('/admin/companies?status=pending')
}

async function loadOngoingDrives() {
  ongoingDrives.value = await get('/admin/job-positions?status=ongoing')
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
              <button class="btn btn-sm btn-success me-1" @click="decideCompany(c, 'approved')">
                Approve
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="decideCompany(c, 'rejected')">
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
        <img
          v-if="selectedDrive.company_logo_url"
          :src="selectedDrive.company_logo_url"
          alt="Company logo"
          style="max-height: 4rem"
          class="mb-2"
        />
        <p><strong>Title:</strong> {{ selectedDrive.title }}</p>
        <p><strong>Company:</strong> {{ selectedDrive.company_name }}</p>
        <p><strong>Location:</strong> {{ selectedDrive.location }}</p>
        <p><strong>Description:</strong> {{ selectedDrive.description }}</p>
        <p><strong>Eligible Branches:</strong> {{ selectedDrive.eligible_branches }}</p>
        <p><strong>Min CGPA:</strong> {{ selectedDrive.min_cgpa }}</p>
        <p><strong>Eligible Graduation Year:</strong> {{ selectedDrive.eligible_graduation_year }}</p>
        <p><strong>Salary:</strong> {{ selectedDrive.salary }}</p>
        <p><strong>Skills Required:</strong> {{ selectedDrive.skills_required }}</p>
        <p><strong>Deadline:</strong> {{ selectedDrive.application_deadline }}</p>
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
  </div>
</template>
