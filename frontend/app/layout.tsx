import { Figtree } from 'next/font/google'
import './globals.css'

const figtree = Figtree({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-figtree',
})

export const metadata = {
  title: 'HuntAgent — your cold email, automated',
  description:
    'Five agents discover companies, research them, draft your intro, and ask you on Telegram before anything is sent.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={figtree.variable}>
      <body>{children}</body>
    </html>
  )
}
