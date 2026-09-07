import { parseReceipt } from "./parser.js";
import assert from "node:assert/strict";
const now = new Date("2026-09-07");
const t1 = `CHEVRON #2231
1200 HWY 41
BLANCHARD ID 83804
09/04/2026 14:22
PUMP 3  UNLEADED
GALLONS 12.418  PRICE/G $3.899
FUEL TOTAL   $48.42
SALES TAX     $0.00
TOTAL        $48.42
VISA ************9965
APPROVED
THANK YOU`;
const r1 = parseReceipt(t1, now);
assert.equal(r1.vendor.value, "Chevron");
assert.equal(r1.date.value, "2026-09-04");
assert.equal(r1.total.value, 48.42);
assert.equal(r1.payment_method.value, "visa");
assert.equal(r1.last4.value, "9965");
assert.equal(r1.suggested_category_key.value, "car_truck");

const t2 = `Home Depot
Store 4712  Coeur d'Alene, ID
Sep 2, 2026
2x4x8 STUD        14.36
DECK SCREWS       21.97
SUBTOTAL          36.33
SALES TAX 6.0%     2.18
TOTAL             38.51
XXXXXXXXXXXX4412  MASTERCARD
TOTAL SAVINGS      4.00`;
const r2 = parseReceipt(t2, now);
assert.equal(r2.vendor.value, "Home Depot");
assert.equal(r2.date.value, "2026-09-02");
assert.equal(r2.subtotal.value, 36.33);
assert.equal(r2.tax.value, 2.18);
assert.equal(r2.total.value, 38.51);
assert.equal(r2.payment_method.value, "mastercard");
assert.equal(r2.last4.value, "4412");
assert.equal(r2.suggested_category_key.value, "supplies");

const t3 = `Invoice #TDFLRR-00009
Supabase Pte. Ltd.
Paid on Sep 1, 2026
Pro plan (monthly)
Amount due  $25.00
Amount paid $25.00`;
const r3 = parseReceipt(t3, now);
assert.equal(r3.total.value, 25);
assert.equal(r3.date.value, "2026-09-01");
assert.equal(r3.suggested_category_key.value, "software_subscriptions");

const t4 = `Mountain Grill
Server: Kim  Table 7
8/30/26 7:41 PM
Burger          14.00
Beer             6.00
Subtotal        20.00
Tax              1.20
Tip              4.00
Total           25.20
Visa 1234`;
const r4 = parseReceipt(t4, now);
assert.equal(r4.total.value, 25.2);
assert.equal(r4.tip.value, 4);
assert.equal(r4.date.value, "2026-08-30");
assert.equal(r4.suggested_category_key.value, "meals");
console.log("parser tests passed");
