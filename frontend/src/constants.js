// Mirrors app/constants.py — single source of truth for these fixed vocabularies.

export const APPLICATION_STATUSES = [
  { value: 'applied', label: 'Applied' },
  { value: 'shortlisted', label: 'Shortlisted' },
  { value: 'interview', label: 'Interview' },
  { value: 'offer', label: 'Offer' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'placed', label: 'Placed' },
]

export const TERMINAL_APPLICATION_STATUSES = ['placed', 'rejected']

export const JOB_POSITION_STATUSES = [
  { value: 'ongoing', label: 'Ongoing' },
  { value: 'completed', label: 'Completed' },
]

export const COMPANY_APPROVAL_STATUSES = [
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
]

export function statusLabel(list, value) {
  return list.find((s) => s.value === value)?.label || value
}
