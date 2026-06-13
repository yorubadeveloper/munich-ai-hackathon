'use client'
import { useEffect, useRef, useState } from 'react'

/**
 * Thin wrapper around lottie-web that loads a JSON animation from /public.
 * Client-only; renders nothing until the animation is fetched.
 */
export default function Lottie({
  src,
  style,
  loop = true,
}: {
  src: string
  style?: React.CSSProperties
  loop?: boolean
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    let alive = true
    fetch(src)
      .then((r) => r.json())
      .then((d) => {
        if (alive) setData(d)
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [src])

  useEffect(() => {
    if (!data || !ref.current) return
    let anim: any
    let cancelled = false
    import('lottie-web').then((mod) => {
      if (cancelled || !ref.current) return
      anim = mod.default.loadAnimation({
        container: ref.current,
        renderer: 'svg',
        loop,
        autoplay: true,
        animationData: data,
      })
    })
    return () => {
      cancelled = true
      if (anim) anim.destroy()
    }
  }, [data, loop])

  return <div ref={ref} style={style} aria-hidden />
}
