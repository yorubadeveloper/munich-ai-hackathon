const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Backend serializes naive UTC timestamps without a timezone suffix.
// Append "Z" so the browser parses them as UTC rather than local time.
function normalizeTimestamps<T extends Record<string, any>>(row: T): T {
  for (const key of ['created_at', 'discovered_at']) {
    const v = row[key]
    if (
      typeof v === 'string' &&
      v.length > 0 &&
      !v.endsWith('Z') &&
      !/[+-]\d{2}:?\d{2}$/.test(v)
    ) {
      ;(row as Record<string, any>)[key] = v + 'Z'
    }
  }
  return row
}

export async function getCompanies() {
  try {
    const res = await fetch(`${BASE}/api/companies`, { cache: 'no-store' })
    if (!res.ok) return []
    const data = await res.json()
    return Array.isArray(data) ? data.map(normalizeTimestamps) : []
  } catch {
    return []
  }
}

export async function getLog() {
  try {
    const res = await fetch(`${BASE}/api/log?limit=40`, { cache: 'no-store' })
    if (!res.ok) return []
    const data = await res.json()
    return Array.isArray(data) ? data.map(normalizeTimestamps) : []
  } catch {
    return []
  }
}

export async function triggerRun() {
  try {
    await fetch(`${BASE}/api/run`, { method: 'POST' })
  } catch {
    // swallow — UI polls and will reflect state on next refresh
  }
}

export async function rerunResearch(companyId: string) {
  try {
    await fetch(`${BASE}/api/companies/${companyId}/research`, { method: 'POST' })
  } catch {
    // swallow — UI polls and will reflect state on next refresh
  }
}

export async function deleteCompany(companyId: string) {
  try {
    const res = await fetch(`${BASE}/api/companies/${companyId}`, { method: 'DELETE' })
    return res.json()
  } catch {
    return { status: 'error' }
  }
}

export async function addCompany(data: {
  name: string
  url?: string
  job_description?: string
}) {
  try {
    const res = await fetch(`${BASE}/api/companies/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return res.json()
  } catch {
    return { status: 'error' }
  }
}

export async function getProfile() {
  try {
    const res = await fetch(`${BASE}/api/profile`, { cache: 'no-store' })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function saveProfile(data: any) {
  const res = await fetch(`${BASE}/api/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return res.json()
}
