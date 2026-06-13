'use client'
import Link from 'next/link'
import {
  ArrowRight,
  MagnifyingGlass,
  Brain,
  PenNib,
  PaperPlaneTilt,
  ChatCircleDots,
  ShieldCheck,
} from '@phosphor-icons/react'
import Lottie from '@/components/Lottie'
import signalAnimation from '@/public/signal.json'

const WORDS_1 = ['One', 'cold', 'email']
const WORDS_2 = ['changed', 'my', 'life.']

function Reveal({
  words,
  delayBase = 0,
  style,
}: {
  words: string[]
  delayBase?: number
  style?: React.CSSProperties
}) {
  return (
    <span style={{ display: 'inline-flex', flexWrap: 'wrap', gap: '0 0.28em' }}>
      {words.map((w, i) => (
        <span key={i} style={{ display: 'inline-block', overflow: 'hidden' }}>
          <span
            style={{
              display: 'inline-block',
              animation: `wordReveal 0.7s var(--ease) both`,
              animationDelay: `${delayBase + i * 0.08}s`,
              ...style,
            }}
          >
            {w}
          </span>
        </span>
      ))}
    </span>
  )
}

const STEPS = [
  { icon: MagnifyingGlass, name: 'Discover', desc: 'Finds companies worth your time.' },
  { icon: Brain, name: 'Research', desc: 'Digs up funding, stack, the right person.' },
  { icon: PenNib, name: 'Draft', desc: 'Writes an intro that sounds like you.' },
  { icon: ShieldCheck, name: 'Approve', desc: 'You say yes on Telegram first.' },
  { icon: PaperPlaneTilt, name: 'Send', desc: 'Delivered by DM or email, then watched.' },
]

export default function Landing() {
  return (
    <div style={{ minHeight: '100vh' }}>
      {/* ── Nav ── */}
      <nav
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 50,
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          maxWidth: 1152,
          margin: '0 auto',
          padding: '0 24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 9, fontWeight: 700, fontSize: 16 }}>
          <span style={{ fontSize: 17 }}>🎯</span>
          HuntAgent
        </div>
        <Link href="/dashboard" className="btn-primary" style={{ padding: '8px 16px', fontSize: 13.5 }}>
          Open dashboard
          <ArrowRight size={15} weight="bold" />
        </Link>
      </nav>

      {/* ── Hero ── */}
      <section
        style={{
          maxWidth: 1152,
          margin: '0 auto',
          padding: '0 24px',
          minHeight: 'calc(92vh - 64px)',
          display: 'grid',
          gridTemplateColumns: '1.1fr 0.9fr',
          alignItems: 'center',
          gap: 56,
        }}
      >
        {/* Left: copy */}
        <div>
          <div
            className="eyebrow fade-in"
            style={{ animationDelay: '0.1s', marginBottom: 22 }}
          >
            Agentic job search
          </div>

          <h1
            style={{
              fontSize: 'clamp(2.4rem, 5vw, 4.25rem)',
              lineHeight: 1.08,
              letterSpacing: '-0.03em',
              fontWeight: 800,
              color: 'var(--ink)',
              marginBottom: 24,
            }}
          >
            <Reveal words={WORDS_1} delayBase={0.15} />
            <br />
            <Reveal words={WORDS_2} delayBase={0.4} />
          </h1>

          <p
            className="fade-in"
            style={{
              animationDelay: '0.7s',
              fontSize: 17,
              lineHeight: 1.6,
              color: 'var(--text-dim)',
              maxWidth: 520,
              marginBottom: 34,
            }}
          >
            In 2020 I wrote one cold email to a CTO and it took me from Nigeria to
            Munich. No network, no referral. Just research, one honest message, and one
            shot. HuntAgent does that for every company you care about, and asks you
            before anything is sent.
          </p>

          <div
            className="fade-in"
            style={{ animationDelay: '0.85s', display: 'flex', gap: 12, flexWrap: 'wrap' }}
          >
            <Link href="/dashboard" className="btn-primary">
              Run the hunt
              <ArrowRight size={16} weight="bold" />
            </Link>
            <a href="#how" className="btn-ghost">
              See how it works
            </a>
          </div>

          <div
            className="fade-in"
            style={{
              animationDelay: '1s',
              marginTop: 22,
              fontSize: 13,
              color: 'var(--faint)',
              display: 'flex',
              alignItems: 'center',
              gap: 7,
            }}
          >
            <ShieldCheck size={15} weight="fill" />
            Nothing is sent without your approval.
          </div>
        </div>

        {/* Right: Lottie visual */}
        <div
          className="fade-in"
          style={{
            animationDelay: '0.5s',
            position: 'relative',
            aspectRatio: '1',
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border)',
            background:
              'radial-gradient(120% 120% at 50% 0%, #ffffff 0%, #f5f5f4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
          }}
        >
          <Lottie animationData={signalAnimation} style={{ width: '78%', height: '78%' }} />
          <div
            style={{
              position: 'absolute',
              bottom: 18,
              left: 0,
              right: 0,
              textAlign: 'center',
              fontFamily: 'var(--mono)',
              fontSize: 11,
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
              color: 'var(--faint)',
            }}
          >
            reaching out · on your behalf
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section id="how" style={{ maxWidth: 1152, margin: '0 auto', padding: '72px 24px 40px' }}>
        <div className="eyebrow" style={{ marginBottom: 14 }}>
          How it works
        </div>
        <h2
          style={{
            fontSize: 'clamp(1.6rem, 3vw, 2.2rem)',
            fontWeight: 700,
            letterSpacing: '-0.025em',
            marginBottom: 40,
            maxWidth: 620,
            lineHeight: 1.15,
          }}
        >
          Five agents run the loop you used to run by hand.
        </h2>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
            gap: 14,
          }}
        >
          {STEPS.map((s, i) => {
            const Icon = s.icon
            return (
              <div
                key={s.name}
                style={{
                  background: 'var(--surface)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '22px 20px',
                  position: 'relative',
                }}
              >
                <div
                  style={{
                    width: 38,
                    height: 38,
                    borderRadius: 10,
                    background: 'var(--bg-2)',
                    border: '1px solid var(--border)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 16,
                  }}
                >
                  <Icon size={19} weight="duotone" color="#1c1917" />
                </div>
                <div
                  style={{
                    fontFamily: 'var(--mono)',
                    fontSize: 11,
                    color: 'var(--faint)',
                    marginBottom: 4,
                  }}
                >
                  0{i + 1}
                </div>
                <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 5 }}>{s.name}</div>
                <div style={{ fontSize: 13, color: 'var(--text-dim)', lineHeight: 1.5 }}>
                  {s.desc}
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* ── Closing CTA ── */}
      <section style={{ maxWidth: 1152, margin: '0 auto', padding: '40px 24px 100px' }}>
        <div
          style={{
            borderRadius: 'var(--radius-xl)',
            border: '1px solid var(--border)',
            background: 'var(--ink)',
            color: '#fff',
            padding: '56px 48px',
            textAlign: 'center',
          }}
        >
          <h2
            style={{
              fontSize: 'clamp(1.6rem, 3vw, 2.4rem)',
              fontWeight: 700,
              letterSpacing: '-0.025em',
              marginBottom: 14,
            }}
          >
            Stop sending applications into the void.
          </h2>
          <p
            style={{
              fontSize: 16,
              color: 'rgba(255,255,255,0.7)',
              maxWidth: 480,
              margin: '0 auto 30px',
              lineHeight: 1.6,
            }}
          >
            Set your profile once. Let the agents find the companies, write the intro,
            and wait for your yes.
          </p>
          <Link
            href="/dashboard"
            className="btn-primary"
            style={{ background: '#fff', color: 'var(--ink)', borderColor: '#fff' }}
          >
            Open the dashboard
            <ArrowRight size={16} weight="bold" />
          </Link>
        </div>
        <div
          style={{
            textAlign: 'center',
            marginTop: 40,
            fontSize: 12.5,
            color: 'var(--faint)',
          }}
        >
          HuntAgent · Gemini · Tavily · GLiNER2 on Pioneer · Unipile · Telegram
        </div>
      </section>
    </div>
  )
}
