'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { approveCompany, rejectCompany, ApprovalState } from '@/lib/api'

type ApprovalActionsProps = {
  companyId: string
  approvalState: ApprovalState
}

export default function ApprovalActions({ companyId, approvalState }: ApprovalActionsProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [localStatus, setLocalStatus] = useState<string | null>(null)

  if (approvalState.status !== 'pending' && !localStatus) {
    return null
  }

  const handleApprove = async () => {
    setLoading(true)
    const res = await approveCompany(companyId)
    setLoading(false)
    if (res.status === 'success') {
      setLocalStatus('approved')
      router.refresh()
    }
  }

  const handleReject = async () => {
    setLoading(true)
    const res = await rejectCompany(companyId)
    setLoading(false)
    if (res.status === 'success') {
      setLocalStatus('rejected')
      router.refresh()
    }
  }

  if (localStatus) {
    return (
      <div style={{ marginTop: 16, padding: '8px 12px', borderRadius: 'var(--radius-sm)', background: 'var(--bg-2)', border: '1px solid var(--border)', fontSize: 13, fontWeight: 500, color: 'var(--text-dim)' }}>
        Action submitted: <span style={{ fontWeight: 700, textTransform: 'capitalize', color: 'var(--ink)' }}>{localStatus}</span>. Reloading...
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
      <button
        onClick={handleApprove}
        disabled={loading}
        style={{
          flex: 1,
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#22c55e',
          color: '#ffffff',
          border: 'none',
          borderRadius: 'var(--radius)',
          padding: '10px 16px',
          fontSize: 14,
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'opacity 0.2s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.9')}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
      >
        {loading ? 'Processing...' : 'Approve'}
      </button>
      <button
        onClick={handleReject}
        disabled={loading}
        style={{
          flex: 1,
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#ef4444',
          color: '#ffffff',
          border: 'none',
          borderRadius: 'var(--radius)',
          padding: '10px 16px',
          fontSize: 14,
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'opacity 0.2s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.9')}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
      >
        {loading ? 'Processing...' : 'Reject'}
      </button>
    </div>
  )
}
