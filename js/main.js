  /* ======================= CONFIG =======================
     Hier stellst du alles ein. Nur den Text zwischen den
     Anführungszeichen ändern, dann speichern.
     ====================================================== */
  const CONFIG = {
    preis: "19 €",              // Preis, der überall auf der Seite steht
    gumroadLink: "https://businessmind355.gumroad.com/l/popdsw",   // dein Gumroad-Produkt
    name: "Normal sein kostet dich dein Leben"   // erscheint auf Cover, beim Autor und unten auf der Seite
  };
  /* ====================================================== */

  document.querySelectorAll(".js-price").forEach(el => el.textContent = CONFIG.preis);
  document.querySelectorAll(".js-name").forEach(el => el.textContent = CONFIG.name);

  // Kauf-Buttons auf Gumroad leiten, sobald ein Link eingetragen ist
  if (CONFIG.gumroadLink) {
    document.querySelectorAll(".js-buy").forEach(el => {
      el.href = CONFIG.gumroadLink;
      el.target = "_blank";
      el.rel = "noopener";
    });
  }

  // Kauf-Leiste auf dem Handy erst nach dem Hero einblenden
  const bar = document.getElementById("mobileBuy");
  const hero = document.querySelector(".hero");
  const buy = document.getElementById("kaufen");
  if (bar && hero && buy) {
  let heroGone = false, buyVisible = false;
  const update = () => bar.classList.toggle("show", heroGone && !buyVisible);
  new IntersectionObserver(([e]) => { heroGone = !e.isIntersecting; update(); }).observe(hero);
  new IntersectionObserver(([e]) => { buyVisible = e.isIntersecting; update(); }).observe(buy);
  }
