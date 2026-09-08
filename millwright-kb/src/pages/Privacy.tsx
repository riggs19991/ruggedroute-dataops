export function Privacy() {
  return (
    <div className="md" style={{ maxWidth: 720 }}>
      <h1>Privacy</h1>
      <p><em>Last updated September 2026.</em></p>
      <p>Millwright Knowledge Base is a study and reference tool for millwright students and instructors. This page says what the app stores and why.</p>
      <h2>What we store</h2>
      <ul>
        <li><b>Account</b>: your email address, a password (stored hashed by our provider), the display name and school you enter. Needed to sign in, to show who wrote a contribution and to run class groups.</li>
        <li><b>Contributions</b>: articles you write, group posts, bookmarks and the files you upload (PDFs, photos, documents). Uploaded files are private: only signed-in users can open them, through short-lived links.</li>
        <li><b>Usage</b>: an article view counter (a number per article, not per person). No advertising, no analytics trackers, no selling of data.</li>
        <li><b>On your device</b>: the installed app keeps copies of articles and diagrams you have opened so they work offline, and your sign-in session. Clearing the app's data removes them.</li>
      </ul>
      <h2>Where it is stored</h2>
      <p>Accounts, content and files are hosted by Supabase (Postgres database and file storage) and the website is served by Cloudflare. Both encrypt data in transit and at rest.</p>
      <h2>Who can see what</h2>
      <ul>
        <li>Published articles are public. Drafts are visible only to you (and to the site moderator).</li>
        <li>Group posts and files are visible to members of that group.</li>
        <li>Community contributions are not reviewed before they appear. Anyone can edit or delete their own articles; the site moderator can remove anything. Upvotes are stored with your account so you can undo them.</li>
      </ul>
      <h2>Your choices</h2>
      <p>You can edit your name and school on the profile page and delete files you uploaded. To delete your account and everything linked to it, ask your instructor or email the site owner; it is removed within a few days.</p>
      <h2>Children</h2>
      <p>The app is intended for trade-school students and adults. It is not directed at children under 13.</p>
      <h2>Contact</h2>
      <p>Questions about this policy go to the site owner through your instructor.</p>
    </div>
  )
}
