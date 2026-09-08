import { Link } from 'react-router-dom'
import { COMPANY, CONTACT_EMAIL, COPYRIGHT_YEAR } from '../lib/site'

export function Terms() {
  return (
    <div className="md" style={{ maxWidth: 760 }}>
      <h1>Terms of use and legal notices</h1>
      <p><em>Last updated September {COPYRIGHT_YEAR}.</em></p>
      <p>
        Millwright Knowledge Base (the "app", including the website, the installable web app and the Android and iOS
        apps) is owned and operated by <strong>{COMPANY}</strong> ("we", "us"). By using the app you agree to these
        terms. If you do not agree, do not use the app.
      </p>

      <h2>1. What the app is, and is not</h2>
      <p>
        The app is an educational reference for millwrights, apprentices and instructors. Values such as amperages,
        torques, clearances, pressures, capacities and procedures are starting points collected from public sources and
        from community members. They are <strong>not</strong> a substitute for the equipment manufacturer's manual, your
        training, your employer's procedures, applicable codes and standards, or a competent person's judgement on site.
      </p>
      <p>
        Industrial work is dangerous. You are responsible for verifying any information before acting on it, for
        following lockout, hot work, confined space, fall protection and rigging rules that apply to you, and for
        deciding whether a task is within your competence. <strong>Use of the app is at your own risk.</strong>
      </p>

      <h2>2. Community content</h2>
      <p>
        Members can publish articles, files and posts without prior review. Community contributions are marked as such.
        We do not verify them, do not endorse them, and are not responsible for their accuracy, completeness or legality.
        We may edit, hide or remove any content at any time, for any reason, without notice.
      </p>
      <p>
        When you publish content you confirm that it is your own work or that you have the right to share it, that it
        does not contain personal information about others or material you are not permitted to distribute (for example
        an employer's internal procedures or copyrighted documents without permission), and that it is accurate to the
        best of your knowledge. You keep ownership of what you write. You grant {COMPANY} and every user of the app a
        worldwide, non-exclusive, royalty-free licence to store, display, reproduce and share it within the app for as
        long as it remains published, so that the knowledge base can work.
      </p>

      <h2>3. Acceptable use</h2>
      <ul>
        <li>No content that is unlawful, defamatory, harassing, discriminatory or deliberately misleading.</li>
        <li>No advertising, spam or content posted mainly to promote a product or service.</li>
        <li>No attempts to access other people's accounts, groups or data, or to disrupt the service.</li>
        <li>No uploading of malware or of files you do not have the right to share.</li>
      </ul>
      <p>We may suspend or delete accounts that break these rules.</p>

      <h2>4. Accounts and groups</h2>
      <p>
        You must give a working email address and keep your password private. Anyone can create a group and becomes its
        instructor; instructors are responsible for what they post to their group and for whom they give the join code
        to. We can remove groups that are misused.
      </p>

      <h2>5. Copyright and trademarks</h2>
      <p>
        The app's original text, diagrams, design and software are © {COPYRIGHT_YEAR} {COMPANY}. All rights reserved.
        You may print or copy individual articles for personal, educational or on-the-job use with attribution; you
        may not republish the collection or sell it. Manufacturer names, product names and standards referenced in the
        app (for example Lincoln, Victor, SKF, Dodge, AWS, CSA) are trademarks of their respective owners and are used
        only to identify equipment and documents; no affiliation or endorsement is implied.
      </p>
      <p>
        If you believe content in the app infringes your copyright, email <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>{' '}
        with the location of the material, a description of the work, your contact details and a statement that you own
        the work or act for the owner. We will remove infringing material promptly.
      </p>

      <h2>6. No warranty</h2>
      <p>
        THE APP AND ALL CONTENT ARE PROVIDED "AS IS" AND "AS AVAILABLE", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING WARRANTIES OF ACCURACY, MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
        NON-INFRINGEMENT. We do not promise that the app will be available, error-free or up to date.
      </p>

      <h2>7. Limitation of liability</h2>
      <p>
        TO THE FULLEST EXTENT PERMITTED BY LAW, {COMPANY.toUpperCase()}, ITS OWNERS, CONTRIBUTORS AND SUPPLIERS SHALL NOT
        BE LIABLE FOR ANY INJURY, DEATH, PROPERTY DAMAGE, LOSS OF DATA, LOSS OF PROFITS OR ANY INDIRECT, INCIDENTAL,
        SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES ARISING FROM YOUR USE OF, OR RELIANCE ON, THE APP OR ITS CONTENT. Where
        liability cannot be excluded, it is limited to the amount you paid us to use the app, which is nothing.
      </p>
      <p>
        You agree to indemnify {COMPANY} against claims arising from content you publish or from your breach of these
        terms.
      </p>

      <h2>8. Donations</h2>
      <p>
        Donations are voluntary gifts to support the creator. They do not buy goods, services, features or any
        obligation, are not tax deductible, and are not refundable except where the law requires.
      </p>

      <h2>9. Privacy</h2>
      <p>How we handle your data is described in the <Link to="/privacy">privacy policy</Link>, which forms part of these terms.</p>

      <h2>10. Changes and termination</h2>
      <p>
        We may change these terms or the app at any time; the date at the top shows the current version and continued
        use means you accept the changes. We may stop providing the app or close your account at any time. You can stop
        using it and ask us to delete your account at any time.
      </p>

      <h2>11. Governing law</h2>
      <p>
        These terms are governed by the laws of the jurisdiction in which {COMPANY} is registered, without regard to
        conflict-of-law rules, and disputes are subject to the courts there. If a part of these terms is found
        unenforceable, the rest still applies.
      </p>

      <h2>12. Contact</h2>
      <p>{COMPANY}, <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.</p>
    </div>
  )
}
