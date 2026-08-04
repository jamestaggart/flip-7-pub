import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Flip 7',
  description: 'A couch co-op turn-based card game',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
