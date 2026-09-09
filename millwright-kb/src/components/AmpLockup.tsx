import type { ReactNode } from 'react'

/** The Addictive Media Productions lockup with a line of text beside it (legal and support pages). */
export function AmpLockup({ text }: { text: ReactNode }) {
  return (
    <div className="amp-lockup">
      <img src="/brand/amp-logo.png" alt="Addictive Media Productions" width="640" height="289" />
      <div>{text}</div>
    </div>
  )
}
