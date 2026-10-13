(function () {
  const app = document.getElementById("seat-app");
  if (!app) return;

  const price = parseFloat(app.dataset.price);
  const maxSeats = parseInt(app.dataset.max, 10);
  const booked = new Set(JSON.parse(document.getElementById("booked-seats").textContent));
  const hidden = document.getElementById("id_seats");
  const grid = document.getElementById("seat-grid");
  const ROWS = ["A", "B", "C", "D", "E"];   // 5 rows
  const COLS = 8;                            // x 8 columns
  const selected = new Set((hidden.value || "").split(",").filter(s => s && !booked.has(s)));

  function render() {
    const list = [...selected].sort((a, b) => a[0].localeCompare(b[0]) || parseInt(a.slice(1)) - parseInt(b.slice(1)));
    hidden.value = list.join(",");
    document.getElementById("sel-seats").textContent = list.length ? list.join(", ") : "—";
    document.getElementById("sel-count").textContent = list.length;
    // Display only; the server recalculates the real total.
    document.getElementById("sel-total").textContent = "₹" + (list.length * price).toLocaleString("en-IN");
    document.getElementById("pay-btn").disabled = list.length === 0;
    grid.querySelectorAll(".seat").forEach(btn => btn.classList.toggle("selected", selected.has(btn.dataset.seat)));
  }

  ROWS.forEach(r => {
    const row = document.createElement("div");
    row.className = "seat-row";
    row.innerHTML = `<span class="row-label">${r}</span>`;
    for (let c = 1; c <= COLS; c++) {
      const id = r + c;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "seat" + (c === 4 ? " aisle" : "");
      btn.dataset.seat = id;
      btn.textContent = c;
      btn.title = id;
      if (booked.has(id)) btn.disabled = true;
      btn.addEventListener("click", () => {
        if (selected.has(id)) selected.delete(id);
        else if (selected.size >= maxSeats) { alert(`You can select up to ${maxSeats} seats.`); return; }
        else selected.add(id);
        render();
      });
      row.appendChild(btn);
    }
    grid.appendChild(row);
  });
  render();
})();
