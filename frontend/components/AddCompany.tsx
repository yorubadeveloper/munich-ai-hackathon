'use client'
import { useState } from 'react'
import { createPortal } from 'react-dom'
import { Plus, X, PaperPlaneRight } from '@phosphor-icons/react'
import { addCompany } from '@/lib/api'

export default function AddCompany({ onAdded }: { onAdded?: () => void }) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [companyUrl, setCompanyUrl] = useState('')
  const [jobUrl, setJobUrl] = useState('')
  const [jd, setJd] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const reset = () => {
    setName('')
    setCompanyUrl('')
    setJobUrl('')
    setJd('')
  }

  const submit = async () => {
    if (!name.trim() || submitting) return
    setSubmitting(true)
    await addCompany({
      name: name.trim(),
      company_url: companyUrl.trim(),
      job_url: jobUrl.trim(),
      job_description: jd.trim(),
    })
    setSubmitting(false)
    reset()
    setOpen(false)
    onAdded?.()
  }

  const triggerButton = (
    <button
      onClick={() => setOpen(true)}
      className="btn-ghost"
      style={{ padding: '9px 16px', fontSize: 13 }}
    >
      <Plus size={15} weight="bold" />
      Add a company
    </button>
  )

  if (!open) {
    return triggerButton
  }

  const modalOverlay = (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(28,25,23,0.38)',
        backdropFilter: 'blur(3px)',
        zIndex: 99999, /* High z-index to sit on top of everything */
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        padding: '12vh 20px 20px',
      }}
      onClick={() => setOpen(false)}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: 520,
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-lg)',
          padding: 24,
          animation: 'fadeUp 0.3s var(--ease) both',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 6,
          }}
        >
          <h2 style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--ink)' }}>
            Target a company
          </h2>
          <button
            onClick={() => setOpen(false)}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--muted)',
              display: 'flex',
            }}
          >
            <X size={18} weight="bold" />
          </button>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-dim)', marginBottom: 20, lineHeight: 1.5 }}>
          Paste a company you want to reach. HuntAgent will research it, find the
          right person, and draft your intro for approval.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Field label="Company name *">
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Atira"
              style={inputStyle}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) submit()
              }}
            />
          </Field>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <Field label="Company website (optional)">
              <input
                value={companyUrl}
                onChange={(e) => setCompanyUrl(e.target.value)}
                placeholder="atira.ai"
                style={inputStyle}
              />
            </Field>

            <Field label="Job posting URL (optional)">
              <input
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                placeholder="Ashby / Greenhouse link"
                style={inputStyle}
              />
            </Field>
          </div>

          <Field label="Paste the job description (optional)">
            <textarea
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              placeholder="Paste the role description here to tailor the research and draft…"
              rows={4}
              style={{ ...inputStyle, resize: 'vertical' }}
            />
          </Field>
        </div>

        <div style={{ display: 'flex', gap: 10, marginTop: 22, justifyContent: 'flex-end' }}>
          <button onClick={() => setOpen(false)} className="btn-ghost" style={{ padding: '10px 18px' }}>
            Cancel
          </button>
          <button
            onClick={submit}
            disabled={!name.trim() || submitting}
            className="btn-primary"
            style={{ padding: '10px 20px' }}
          >
            <PaperPlaneRight size={15} weight="fill" />
            {submitting ? 'Researching…' : 'Research & draft'}
          </button>
        </div>
      </div>
    </div>
  )

  // Teleport the modal overlay to document.body so it escapes the header block
  return (
    <>
      {triggerButton}
      {typeof document !== 'undefined' && createPortal(modalOverlay, document.body)}
    </>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
      <label
        style={{
          fontSize: 11,
          color: 'var(--text-dim)',
          letterSpacing: '0.07em',
          textTransform: 'uppercase',
          fontWeight: 700,
        }}
      >
        {label}
      </label>
      {children}
    </div>
  )
}

const inputStyle: React.CSSProperties = {
  background: 'var(--bg)',
  border: '1px solid var(--border)',
  borderRadius: 10,
  padding: '11px 13px',
  color: 'var(--text)',
  fontFamily: 'var(--font)',
  fontSize: 14,
  outline: 'none',
  width: '100%',
}
