// Mirrors app/constants.py — single source of truth for these fixed vocabularies.

export const APPLICATION_STATUS_APPLIED = 'applied'
export const APPLICATION_STATUS_INTERVIEW = 'interview'
export const APPLICATION_STATUS_OFFER = 'offer'
export const APPLICATION_STATUS_PLACED = 'placed'
export const APPLICATION_STATUS_REJECTED = 'rejected'

export const APPLICATION_STATUSES = [
  { value: APPLICATION_STATUS_APPLIED, label: 'Applied' },
  { value: 'shortlisted', label: 'Shortlisted' },
  { value: 'interview', label: 'Interview' },
  { value: APPLICATION_STATUS_OFFER, label: 'Offer' },
  { value: APPLICATION_STATUS_REJECTED, label: 'Rejected' },
  { value: APPLICATION_STATUS_PLACED, label: 'Placed' },
]

export const TERMINAL_APPLICATION_STATUSES = [APPLICATION_STATUS_PLACED, APPLICATION_STATUS_REJECTED]

export const JOB_POSITION_STATUS_ONGOING = 'ongoing'
export const JOB_POSITION_STATUS_COMPLETED = 'completed'

export const JOB_POSITION_STATUSES = [
  { value: JOB_POSITION_STATUS_ONGOING, label: 'Ongoing' },
  { value: JOB_POSITION_STATUS_COMPLETED, label: 'Completed' },
]

export const COMPANY_APPROVAL_PENDING = 'pending'
export const COMPANY_APPROVAL_APPROVED = 'approved'
export const COMPANY_APPROVAL_REJECTED = 'rejected'

export const COMPANY_APPROVAL_STATUSES = [
  { value: COMPANY_APPROVAL_PENDING, label: 'Pending' },
  { value: COMPANY_APPROVAL_APPROVED, label: 'Approved' },
  { value: COMPANY_APPROVAL_REJECTED, label: 'Rejected' },
]

export const EXPORT_JOB_STATUS_PENDING = 'pending'
export const EXPORT_JOB_STATUS_RUNNING = 'running'
export const EXPORT_JOB_STATUS_READY = 'ready'
export const EXPORT_JOB_STATUS_FAILED = 'failed'

export const EXPORT_JOB_STATUSES = [
  { value: EXPORT_JOB_STATUS_PENDING, label: 'Pending' },
  { value: EXPORT_JOB_STATUS_RUNNING, label: 'Running' },
  { value: EXPORT_JOB_STATUS_READY, label: 'Ready' },
  { value: EXPORT_JOB_STATUS_FAILED, label: 'Failed' },
]

export function statusLabel(list, value) {
  return list.find((s) => s.value === value)?.label || value
}
