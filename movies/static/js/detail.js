(function () {
  // Showtime pills -> enable the booking button
  const bookBtn = document.getElementById("book-btn");
  document.querySelectorAll(".showtime-radio").forEach(radio => {
    radio.addEventListener("change", () => {
      bookBtn.href = radio.dataset.url;
      bookBtn.classList.remove("disabled");
      bookBtn.removeAttribute("aria-disabled");
      bookBtn.textContent = "Select seats →";
    });
  });

  // 1-5 star rating input
  const stars = [...document.querySelectorAll(".star-btn")];
  const hidden = document.getElementById("id_rating");
  if (!stars.length || !hidden) return;
  const paint = v => stars.forEach(s => s.classList.toggle("active", parseInt(s.dataset.value) <= v));
  paint(parseInt(hidden.value) || 0);
  stars.forEach(s => {
    s.addEventListener("click", () => { hidden.value = s.dataset.value; paint(parseInt(s.dataset.value)); });
    s.addEventListener("mouseenter", () => paint(parseInt(s.dataset.value)));
  });
  document.getElementById("star-input").addEventListener("mouseleave", () => paint(parseInt(hidden.value) || 0));
})();
