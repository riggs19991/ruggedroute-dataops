// Free receipt parser: turns OCR / PDF text into fields with confidence scores.
// No network, no models. Shared by the edge function; unit-tested with node.

const AMOUNT = /(?<![\d.])\$?\s*(-?\d{1,6}(?:,\d{3})*\.\d{2})(?![\d])/g;

const TOTAL_LINE = /\b(grand\s*total|total\s*(?:due|paid|amount|charge|sale)?|amount\s*(?:due|paid|charged)|balance\s*due|order\s*total|invoice\s*total|total\s*\(usd\))\b/i;
const NOT_TOTAL = /\b(sub\s*-?\s*total|savings|saved|items?|qty|quantity|points|tender|tendered|change|cash\s*back|discount|before|tax\s*rate|total\s*tax)\b/i;
const SUBTOTAL_LINE = /\bsub\s*-?\s*total\b/i;
const TAX_LINE = /\b(sales\s*tax|tax|hst|gst|pst|vat)\b/i;
const NOT_TAX = /\b(tax\s*id|tax\s*#|taxable|pre-?tax|tax\s*exempt|before\s*tax|ein)\b/i;
const TIP_LINE = /\b(tip|gratuity)\b/i;

const MONTHS = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, sept: 9, oct: 10, nov: 11, dec: 12 };

const CATEGORY_HINTS = [
  ["car_truck", /\b(chevron|shell|exxon|mobil|conoco|maverik|sinclair|texaco|arco|76|circle k|pilot|flying j|love'?s|gas|fuel|diesel|unleaded|gallons?|gal\b|oil change|tire|les schwab|autozone|o'?reilly|napa|jiffy lube|car wash|parking|toll)\b/i],
  ["meals", /\b(restaurant|cafe|café|coffee|starbucks|dutch bros|grill|pizza|burger|taco|sushi|diner|bistro|brewery|pub|bar & grill|mcdonald|wendy|subway|chipotle|panda express|jimmy john|domino|doordash|uber eats|grubhub|server|table|gratuity)\b/i],
  ["travel", /\b(hotel|motel|inn\b|airbnb|vrbo|campground|camp\s*site|koa\b|rv park|forest service|recreation\.gov|reserveamerica|state park|airline|alaska air|delta|united|southwest|rental car|hertz|enterprise|avis|budget|lodging|resort)\b/i],
  ["software_subscriptions", /\b(google\s*(workspace|cloud|play|one|storage)|adobe|cloudflare|supabase|mapbox|github|microsoft|office 365|dropbox|notion|zoom|canva|apple\.com\/bill|itunes|app store|netflix|spotify|epidemic sound|artlist|envato|subscription|monthly plan|annual plan|renewal|domain|godaddy|namecheap|squarespace|wix|shopify|anthropic|openai)\b/i],
  ["utilities", /\b(verizon|t-mobile|tmobile|at&t|att\b|starlink|spectrum|xfinity|comcast|ziply|internet|wireless|phone bill|electric|power co|avista|idaho power|propane|water bill)\b/i],
  ["equipment", /\b(camera|lens|drone|dji|gopro|sony|canon|nikon|tripod|gimbal|ssd|hard drive|laptop|monitor|best buy|b&h|adorama|micro center|newegg|computer|pc\b|gpu|printer)\b/i],
  ["supplies", /\b(amazon|amzn|walmart|target|costco|sam'?s club|home depot|lowe'?s|ace hardware|staples|office depot|officemax|dollar tree|harbor freight|tractor supply|north 40|batteries|sd card|memory card|cable|adapter|tape|ink)\b/i],
  ["office", /\b(usps|postage|stamps|fedex|ups store|ups\b|shipping|po box|printing|fedex office|kinko)\b/i],
  ["advertising", /\b(facebook ads|meta ads|google ads|adwords|tiktok ads|youtube ads|instagram|sponsored|promotion|boost post|vistaprint|business cards|decals?|stickers?|banner|signage)\b/i],
  ["taxes_licenses", /\b(secretary of state|sosbiz|idaho sos|tax commission|irs\b|department of revenue|business license|permit|registration fee|annual report|filing fee|dmv)\b/i],
  ["legal_professional", /\b(attorney|law office|legal|cpa\b|accountant|bookkeep|notary|registered agent|consulting)\b/i],
  ["insurance", /\b(insurance|policy premium|state farm|geico|progressive|allstate|usaa|farmers|liberty mutual)\b/i],
  ["bank_fees", /\b(monthly maintenance fee|wire fee|overdraft|service charge|stripe fee|paypal fee|merchant fee|processing fee)\b/i],
  ["education", /\b(course|udemy|skillshare|masterclass|workshop|training|seminar|conference|tuition|book)\b/i],
];

const PAYMENT = [
  ["visa", /\bvisa\b/i], ["mastercard", /\bmaster\s*card\b/i], ["amex", /\b(amex|american express)\b/i],
  ["discover", /\bdiscover\b/i], ["debit", /\bdebit\b/i], ["paypal", /\bpaypal\b/i],
  ["cash", /\bcash\b(?!\s*back)/i], ["check", /\b(check|cheque)\s*(#|no|number)?\s*\d*/i],
  ["other", /\b(apple pay|google pay|credit|card)\b/i],
];

function toNumber(s) { return parseFloat(String(s).replace(/[$,\s]/g, "")); }
function amountsIn(line) {
  const out = []; let m; AMOUNT.lastIndex = 0;
  while ((m = AMOUNT.exec(line)) !== null) out.push(toNumber(m[1]));
  return out;
}
function lastAmount(line) { const a = amountsIn(line); return a.length ? a[a.length - 1] : null; }

export function parseDate(text, now = new Date()) {
  const maxYear = now.getFullYear() + 1;
  const ok = (y, mo, d) => y >= 2010 && y <= maxYear && mo >= 1 && mo <= 12 && d >= 1 && d <= 31;
  const fmt = (y, mo, d) => `${y}-${String(mo).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
  let m;
  // 2026-09-07
  if ((m = text.match(/\b(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\b/)) && ok(+m[1], +m[2], +m[3])) return { value: fmt(+m[1], +m[2], +m[3]), confidence: 0.9 };
  // 09/07/2026 or 9-7-26
  const re = /\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})\b/g;
  while ((m = re.exec(text)) !== null) {
    let y = +m[3]; if (m[3].length === 2) y += 2000;
    if (ok(y, +m[1], +m[2])) return { value: fmt(y, +m[1], +m[2]), confidence: m[3].length === 2 ? 0.75 : 0.85 };
  }
  // Sep 7, 2026 / September 7 2026 / 7 Sep 2026
  const mon = "(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\\.?";
  if ((m = text.match(new RegExp(`\\b${mon}\\s+(\\d{1,2})(?:st|nd|rd|th)?,?\\s+(20\\d{2})\\b`, "i")))) {
    const mo = MONTHS[m[1].toLowerCase().slice(0, 4)] ?? MONTHS[m[1].toLowerCase().slice(0, 3)];
    if (ok(+m[3], mo, +m[2])) return { value: fmt(+m[3], mo, +m[2]), confidence: 0.85 };
  }
  if ((m = text.match(new RegExp(`\\b(\\d{1,2})\\s+${mon}\\s+(20\\d{2})\\b`, "i")))) {
    const mo = MONTHS[m[2].toLowerCase().slice(0, 4)] ?? MONTHS[m[2].toLowerCase().slice(0, 3)];
    if (ok(+m[3], mo, +m[1])) return { value: fmt(+m[3], mo, +m[1]), confidence: 0.85 };
  }
  return { value: null, confidence: 0 };
}

export function parseVendor(lines) {
  const bad = /^(welcome|thank|thanks|receipt|invoice|order|customer|copy|store\s*#?\s*\d*|tel|phone|www\.|http|date|time|cashier|register|trans|merchant id|terminal)/i;
  for (const raw of lines.slice(0, 8)) {
    const l = raw.replace(/[|_]+/g, " ").trim();
    if (l.length < 3 || l.length > 48) continue;
    if ((l.match(/[a-z]/gi) || []).length < 3) continue;
    if (bad.test(l)) continue;
    if (AMOUNT.test(l)) { AMOUNT.lastIndex = 0; continue; }
    AMOUNT.lastIndex = 0;
    if (/\d{3}[-.\s]\d{3}[-.\s]\d{4}/.test(l)) continue; // phone
    if (parseDate(l).value) continue;
    const name = l.replace(/\s*(#|no\.?|store)\s*\d+.*$/i, "").replace(/\s{2,}/g, " ").trim();
    return { value: name.length >= 3 ? titleCase(name) : null, confidence: name.length >= 3 ? 0.7 : 0 };
  }
  return { value: null, confidence: 0 };
}
function titleCase(s) {
  if (s !== s.toUpperCase()) return s;
  return s.toLowerCase().replace(/\b([a-z])/g, (c) => c.toUpperCase()).replace(/\b(Llc|Inc|Usa)\b/g, (w) => w.toUpperCase());
}

export function parseReceipt(text, now = new Date()) {
  const lines = text.split(/\r?\n/).map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean);
  const all = lines.join("\n");
  const vendor = parseVendor(lines);
  const date = parseDate(all, now);

  // Total: prefer keyword lines (last one wins, since totals sit at the bottom).
  let total = { value: null, confidence: 0 };
  let subtotal = { value: null, confidence: 0 };
  let tax = { value: null, confidence: 0 };
  let tip = { value: null, confidence: 0 };
  const allAmounts = [];
  lines.forEach((line, i) => {
    const amts = amountsIn(line);
    // amount may be on the next line (two-column OCR), so peek forward
    const next = amts.length ? amts : amountsIn(lines[i + 1] ?? "");
    const a = next.length ? next[next.length - 1] : null;
    allAmounts.push(...amts);
    if (a === null) return;
    if (SUBTOTAL_LINE.test(line)) { subtotal = { value: a, confidence: 0.85 }; return; }
    if (TOTAL_LINE.test(line) && !NOT_TOTAL.test(line)) { total = { value: a, confidence: 0.9 }; return; }
    if (TIP_LINE.test(line)) { tip = { value: a, confidence: 0.8 }; return; }
    if (TAX_LINE.test(line) && !NOT_TAX.test(line)) { tax = { value: (tax.value ?? 0) + a, confidence: 0.8 }; return; }
  });
  if (total.value === null && allAmounts.length) {
    const positives = allAmounts.filter((x) => x > 0);
    if (positives.length) total = { value: Math.max(...positives), confidence: 0.45 };
  }
  // Sanity: a total below subtotal is probably a tendered/partial line; fall back.
  if (total.value !== null && subtotal.value !== null && total.value < subtotal.value) {
    const maxA = Math.max(...allAmounts.filter((x) => x > 0));
    total = { value: maxA, confidence: 0.5 };
  }
  if (subtotal.value === null && total.value !== null && tax.value !== null && tax.value < total.value) {
    subtotal = { value: Math.round((total.value - tax.value - (tip.value ?? 0)) * 100) / 100, confidence: 0.5 };
  }

  let payment = { value: null, confidence: 0 };
  for (const [k, re] of PAYMENT) { if (re.test(all)) { payment = { value: k, confidence: k === "other" ? 0.4 : 0.8 }; break; } }
  let last4 = { value: null, confidence: 0 };
  let m = all.match(/(?:x{2,}|\*{2,}|#{2,}|ending(?:\s+in)?|acct(?:\s*#)?|card\s*#?)\s*:?\s*(\d{4})\b/i);
  if (m) last4 = { value: m[1], confidence: 0.8 };

  let category = { value: null, confidence: 0 };
  const head = lines.slice(0, 4).join(" ");
  for (const [key, re] of CATEGORY_HINTS) {
    if (re.test(head)) { category = { value: key, confidence: 0.7 }; break; }
  }
  if (!category.value) for (const [key, re] of CATEGORY_HINTS) { if (re.test(all)) { category = { value: key, confidence: 0.5 }; break; } }

  let currency = "USD";
  if (/\b(cad|c\$)\b/i.test(all)) currency = "CAD"; else if (/€|\beur\b/i.test(all)) currency = "EUR";

  const isReceipt = allAmounts.length > 0 || /\b(total|receipt|invoice|paid)\b/i.test(all);
  return { vendor, date, subtotal, tax, tip, total, currency, payment_method: payment, last4, suggested_category_key: category, is_receipt: isReceipt, full_text: all, line_items: [] };
}
