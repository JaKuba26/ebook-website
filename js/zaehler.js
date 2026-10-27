/* Anonymer Besucherzähler: zählt Seitenaufrufe, Spiel-Runden und Klicks zum E-Book.
   Keine Cookies, nichts wird im Browser gespeichert. Die Zahlen liest der Assistent „Midi“. */
(() => {
  const ziel = "/.netlify/functions/zaehler";
  const aus = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) || location.protocol === "file:" || /[?&]frame=/.test(location.search);
  const senden = (e) => {
    if (aus) return;
    try {
      const d = JSON.stringify({ e });
      if (!(navigator.sendBeacon && navigator.sendBeacon(ziel, new Blob([d], { type: "application/json" }))))
        fetch(ziel, { method: "POST", body: d, keepalive: true }).catch(() => {});
    } catch (_) {}
  };
  const seite = (location.pathname.toLowerCase().replace(/\.html$/, "").replace(/\/index$/, "/")) || "/";
  window.zaehle = senden;
  senden("aufruf:" + seite);
  document.addEventListener("click", (ev) => {
    const a = ev.target.closest && ev.target.closest("a[href]");
    if (!a) return;
    const h = a.getAttribute("href") || "";
    if (/gumroad\.com/.test(a.href) || /^\/?(kaufen|code)\/?$/.test(h)) senden("kauf-klick:" + seite);
  }, true);
})();
