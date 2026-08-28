document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("short-names-search");
  const rows = Array.from(document.querySelectorAll(".short-name-row"));
  const emptyState = document.getElementById("short-names-empty");
  const countNode = document.getElementById("visible-count");
  const modeNode = document.getElementById("short-names-mode");

  if (!searchInput || !rows.length || !emptyState) {
    return;
  }

  const normalizeCode = (value) =>
    String(value || "")
      .toLowerCase()
      .replace(/[^0-9a-z]+/g, "");

  const normalizeWords = (value) =>
    String(value || "")
      .toLowerCase()
      .replace(/[^0-9a-z]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();

  const queryMode = (value) => (/\s/.test(String(value || "")) ? "bip39" : "md5_6");

  const applyFilter = () => {
    const rawQuery = searchInput.value;
    const mode = queryMode(rawQuery);
    let visibleTotal = 0;

    rows.forEach((row) => {
      let matches = true;
      if (mode === "bip39") {
        const tokens = normalizeWords(rawQuery).split(" ").filter(Boolean);
        const haystack = normalizeWords(row.dataset.shortBip39 || "");
        matches = tokens.length === 0 || tokens.every((token) => haystack.includes(token));
      } else {
        const needle = normalizeCode(rawQuery);
        const haystack = normalizeCode(row.dataset.shortMd5 || "");
        matches = needle === "" || haystack.includes(needle);
      }

      row.classList.toggle("is-hidden", !matches);
      if (matches) {
        visibleTotal += 1;
      }
    });

    emptyState.classList.toggle("is-hidden", visibleTotal > 0);
    if (countNode) {
      countNode.textContent = String(visibleTotal);
    }
    if (modeNode) {
      modeNode.textContent = mode;
    }
  };

  searchInput.addEventListener("input", applyFilter);
  applyFilter();
});
