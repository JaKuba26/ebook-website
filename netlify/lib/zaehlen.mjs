/* Eigener kleiner Besucherzähler: zählt nur Ereignisse pro Tag (z. B. "aufruf:/spiel").
   Keine Cookies, keine IP-Adressen, keine Profile. Gespeichert in Netlify Blobs. */
import { getStore } from "@netlify/blobs";

export const ERLAUBT = /^(aufruf|kauf-klick|spiel|weiter):[a-z0-9\/\-.]{1,40}$/;
export const BOTS = /bot|crawl|spider|slurp|preview|facebookexternalhit|whatsapp|telegram|discord|skype|headless|lighthouse|curl|wget|python/i;

export const speicher = () => getStore({ name: "zaehler", consistency: "strong" });

export function heute() {
  return new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Berlin" }); // 2026-10-27
}

export async function zaehle(ereignis) {
  if (!ERLAUBT.test(ereignis)) return;
  const store = speicher();
  const tag = heute();
  const daten = (await store.get(tag, { type: "json" })) || {};
  if (!(ereignis in daten) && Object.keys(daten).length >= 200) return; // Schutz gegen Müll
  daten[ereignis] = (daten[ereignis] || 0) + 1;
  await store.setJSON(tag, daten);
}
