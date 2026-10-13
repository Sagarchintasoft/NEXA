(function () {
  const form = document.getElementById("filter-form");
  const results = document.getElementById("results");
  if (!form || !results) return;

  let timer = null, controller = null;

  async function run() {
    const params = new URLSearchParams(new FormData(form));
    [...params.keys()].forEach(k => { if (!params.get(k)) params.delete(k); });
    const qs = params.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname);
    if (controller) controller.abort();
    controller = new AbortController();
    try {
      const res = await fetch("?" + qs, { headers: { "X-Requested-With": "XMLHttpRequest" }, signal: controller.signal });
      results.innerHTML = await res.text();
    } catch (e) { if (e.name !== "AbortError") console.error(e); }
  }

  form.addEventListener("submit", e => { e.preventDefault(); run(); });
  form.querySelector("input[name=q]").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(run, 250); });
  form.querySelectorAll("select").forEach(s => s.addEventListener("change", run));
})();
