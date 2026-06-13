'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Target, Play, User, ArrowLeft } from '@phosphor-icons/react'
import PipelineBoard from '@/components/PipelineBoard'
import ActivityFeed from '@/components/ActivityFeed'
import StatBar from '@/components/StatBar'
import { getCompanies, getLog, triggerRun } from '@/lib/api'

export default function Dashboard() {
  const [companies, setCompanies] = useState<any[]>([])
  const [logs, setLogs] = useState<any[]>([])
  const [running, setRunning] = useState(false)

  const refresh = async () => {
    const [c, l] = await Promise.all([getCompanies(), getLog()])
    setCompanies(c)
    setLogs(l)
  }

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 4000)
    return () => clearInterval(interval)
  }, [])

  const handleRun = async () => {
    if (running) return
    setRunning(true)
    await triggerRun()
    setTimeout(async () => {
      await refresh()
      setRunning(false)
    }, 1800)
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* ── Header ── */}
      <header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 20,
          height: 60,
          padding: '0 26px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(250,250,249,0.82)',
          backdropFilter: 'blur(12px)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Link
            href="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              color: 'var(--muted)',
              fontSize: 13,
              fontWeight: 500,
            }}
          >
            <ArrowLeft size={15} weight="bold" />
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Target size={18} weight="fill" color="#1c1917" />
            <span style={{ fontWeight: 700, fontSize: 16, letterSpacing: '-0.02em' }}>
              HuntAgent
            </span>
          </div>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              marginLeft: 4,
              padding: '3px 9px',
              borderRadius: 999,
              background: 'var(--surface-2)',
              border: '1px solid var(--border)',
              fontSize: 11,
              color: 'var(--text-dim)',
              fontWeight: 600,
            }}
          >
            <span className="live-dot" />
            Live
          </span>
        </div>

        <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
          <Link
            href="/setup"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              color: 'var(--text-dim)',
              fontSize: 13,
              fontWeight: 600,
            }}
          >
            <User size={15} weight="bold" />
            Profile
          </Link>
          <button onClick={handleRun} disabled={running} className="btn-primary" style={{ padding: '8px 16px', fontSize: 13 }}>
            <Play size={14} weight="fill" />
            {running ? 'Hunting…' : 'Run Hunt'}
          </button>
        </div>
      </header>

      {/* ── Body ── */}
      <main
        style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) 350px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            padding: '26px 28px 60px',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 22,
          }}
        >
          <StatBar companies={companies} />
          <PipelineBoard companies={companies} onRun={handleRun} running={running} />
        </div>

        <aside
          style={{
            borderLeft: '1px solid var(--border)',
            overflowY: 'auto',
            padding: '24px 20px 60px',
            background: 'var(--surface)',
          }}
        >
          <ActivityFeed logs={logs} running={running} />
        </aside>
      </main>
    </div>
  )
}
