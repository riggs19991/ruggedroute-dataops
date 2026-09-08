import { COMPANY, COMPANY_LOCATION, CONTACT_EMAIL, DONATE_URL } from '../lib/site'

export function SupportPage() {
  return (
    <div className="md" style={{ maxWidth: 720 }}>
      <h1>Support the creator</h1>
      <p>
        Millwright Knowledge Base is free to use, free of ads, and free of tracking. One person writes the reference
        material, draws the diagrams, and pays for the hosting, the app store accounts and the time it takes to keep it going.
      </p>
      <p>
        If the app has saved you time on a job, helped you through a test, or spared you a trip back to the truck for a
        manual, a small donation is a real help and is genuinely appreciated. There is no pressure and nothing is locked
        behind it: everything here stays free for every millwright and apprentice.
      </p>
      {DONATE_URL ? (
        <p><a className="btn primary donate" href={DONATE_URL} target="_blank" rel="noopener noreferrer">☕ Donate</a></p>
      ) : (
        <p className="notice info">The donation page is being set up. In the meantime you can reach the creator at <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.</p>
      )}
      <h2>Other ways to help</h2>
      <ul>
        <li>Add a procedure, chart or manual you wish had existed when you started.</li>
        <li>Upvote articles that are well done so others find them.</li>
        <li>Tell an apprentice or an instructor about the app.</li>
        <li>Report mistakes to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.</li>
      </ul>
      <p className="small muted">Donations go to {COMPANY} ({COMPANY_LOCATION}), which operates this app, and are processed securely by Stripe; card details never touch the app's own servers. They are gifts, not purchases, and are not tax deductible.</p>
    </div>
  )
}
