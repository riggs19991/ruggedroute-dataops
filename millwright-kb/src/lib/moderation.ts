// Display-name filter for the supporters wall. Runs in the browser for instant feedback and
// again in the Worker (worker/index.ts) before anything is written, so the server copy is the
// one that counts. Profanity and obfuscated spellings come from the obscenity dataset; the
// extra list below covers hate terms and impersonation it does not include.
import { RegExpMatcher, englishDataset, englishRecommendedTransformers } from 'obscenity'

export const REJECT_MESSAGE = "That name can't be shown on the wall. Try another, or stay anonymous."
export const NAME_MAX = 40

const matcher = new RegExpMatcher({ ...englishDataset.build(), ...englishRecommendedTransformers })

// Matched against the name with everything but letters and digits removed and common
// look-alike characters mapped back (so "n4z1" and "n a z i" both hit).
const EXTRA_TERMS = [
  'nazi', 'hitler', 'heil', 'kkk', 'whitepower', 'whitepride', 'lynch', 'genocide', 'jihad', 'isis',
  'pedo', 'paedo', 'rapist', 'rape', 'molest', 'incest', 'porn', 'sex', 'nude', 'onlyfans', 'escort',
  'admin', 'administrator', 'moderator', 'millwrightkb', 'official', 'staff', 'stripe', 'support team',
  'kill', 'murder', 'terrorist', 'suicide',
].map((t) => t.replace(/[^a-z0-9]/g, ''))

const LOOKALIKES: Record<string, string> = { '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '@': 'a', $: 's', '!': 'i', '|': 'l' }

function squash(s: string): string {
  return s.toLowerCase().split('').map((c) => LOOKALIKES[c] ?? c).join('').replace(/[^a-z0-9]/g, '')
}

export type NameCheck = { ok: true; label: string } | { ok: false; reason: string }

/** Validate a name or business for the wall. Returns the cleaned label or a reason to refuse. */
export function checkDisplayName(raw: string): NameCheck {
  const label = String(raw ?? '').replace(/\s+/g, ' ').trim()
  if (label.length < 2) return { ok: false, reason: 'Enter at least two characters, or choose Anonymous.' }
  if (label.length > NAME_MAX) return { ok: false, reason: `Keep it under ${NAME_MAX} characters.` }
  if (!/^[\p{L}\p{N} .,'&()-]+$/u.test(label)) return { ok: false, reason: "Letters, numbers, spaces and . , ' & ( ) - only." }
  if ((label.match(/\p{L}/gu) || []).length < 2) return { ok: false, reason: 'Include at least two letters.' }
  if (/(.)\1{3,}/.test(label)) return { ok: false, reason: 'No repeated characters.' }
  if (/\d{5,}/.test(label.replace(/\D/g, '')) || /\d{3}[ .-]?\d{3}[ .-]?\d{4}/.test(label)) return { ok: false, reason: 'No phone numbers.' }
  const lower = label.toLowerCase()
  if (/https?|www\.|\.(com|net|org|io|co|ca|us|biz|info)\b|@/.test(lower)) return { ok: false, reason: 'No web addresses or emails.' }
  if (matcher.hasMatch(label)) return { ok: false, reason: REJECT_MESSAGE }
  const flat = squash(label)
  if (EXTRA_TERMS.some((t) => flat.includes(t))) return { ok: false, reason: REJECT_MESSAGE }
  return { ok: true, label }
}
