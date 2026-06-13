const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export type Company = {
  id: string
  name: string
  status: string
  fit_score?: number | null
  tech_stack?: string[] | null
  hiring_manager?: string | null
  hiring_manager_role?: string | null
  hiring_manager_linkedin?: string | null
  recent_news?: string | null
  funding_stage?: string | null
  created_at?: string
  discovered_at?: string
}

export type AgentLog = {
  id: string
  agent: string
  action: string
  detail?: string | null
  company_id?: string | null
  created_at: string
}

export type Profile = {
  name?: string | null
  role?: string | null
  seniority?: string | null
  stack?: string[] | null
  location?: string | null
  remote_pref?: string | null
  dealbreakers?: string[] | null
  bio?: string | null
  projects?: string | null
  github_url?: string | null
  portfolio_url?: string | null
  linkedin_url?: string | null
  email?: string | null
  target_industries?: string[] | null
  target_funding_stages?: string[] | null
  company_size?: string | null
}

export type ProfilePayload = Omit<
  Required<Profile>,
  'stack' | 'dealbreakers' | 'target_industries' | 'target_funding_stages'
> & {
  stack: string[]
  dealbreakers: string[]
  target_industries: string[]
  target_funding_stages: string[]
}

type TimestampKey = 'created_at' | 'discovered_at'
type TimestampedRow = Partial<Record<TimestampKey, string>> & Record<string, unknown>

// Backend serializes naive UTC timestamps without a timezone suffix.
// Append "Z" so the browser parses them as UTC rather than local time.
function normalizeTimestamps<T extends TimestampedRow>(row: T): T {
  const normalized: TimestampedRow = { ...row }
  for (const key of ['created_at', 'discovered_at'] satisfies TimestampKey[]) {
    const value = normalized[key]
    if (
      typeof value === 'string' &&
      value.length > 0 &&
      !value.endsWith('Z') &&
      !/[+-]\d{2}:?\d{2}$/.test(value)
    ) {
      normalized[key] = `${value}Z`
    }
  }
  return normalized as T
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function normalizeRows<T extends TimestampedRow>(data: unknown): T[] {
  return Array.isArray(data)
    ? data.filter(isRecord).map((row) => normalizeTimestamps(row as T))
    : []
}

export async function getCompanies(): Promise<Company[]> {
  try {
    const res = await fetch(`${BASE}/api/companies`, { cache: 'no-store' })
    if (!res.ok) return []
    const data = await res.json()
    return normalizeRows<Company & TimestampedRow>(data)
  } catch {
    return []
  }
}

export async function getLog(): Promise<AgentLog[]> {
  try {
    const res = await fetch(`${BASE}/api/log?limit=40`, { cache: 'no-store' })
    if (!res.ok) return []
    const data = await res.json()
    return normalizeRows<AgentLog & TimestampedRow>(data)
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
  company_url?: string
  job_url?: string
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

export async function getProfile(): Promise<Profile | null> {
  try {
    const res = await fetch(`${BASE}/api/profile`, { cache: 'no-store' })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function saveProfile(data: ProfilePayload) {
  const res = await fetch(`${BASE}/api/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return res.json()
}
