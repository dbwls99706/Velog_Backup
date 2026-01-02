import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Velog Backup - 블로그 자동 백업',
  description: 'Velog 포스트를 서버에 무료로 백업하세요',
  verification: {
    google: 'M6Qy42LQloJEnVHEY82cNKuYyPFjFkHsOhz5Gc5OAcY',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  )
}
