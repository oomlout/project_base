document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("explore-search");
  const rows = Array.from(document.querySelectorAll(".part-card"));
  const emptyState = document.getElementById("explore-empty");
  const countNode = document.getElementById("visible-count");
  const taxonomyToggle = document.getElementById("taxonomy-toggle");
  const taxonomyPanel = document.getElementById("taxonomy-panel-body");

  if (taxonomyToggle && taxonomyPanel) {
    taxonomyToggle.addEventListener("click", () => {
      const expanded = taxonomyToggle.getAttribute("aria-expanded") === "true";
      taxonomyToggle.setAttribute("aria-expanded", expanded ? "false" : "true");
      taxonomyPanel.classList.toggle("is-collapsed", expanded);
      const stateNode = taxonomyToggle.querySelector(".taxonomy-toggle__state");
      if (stateNode) {
        stateNode.textContent = expanded ? "Collapsed" : "Open";
      }
    });
  }

  if (!searchInput || !rows.length || !emptyState) {
    return;
  }

  const applyFilter = () => {
    const query = searchInput.value.trim().toLowerCase();
    let visibleTotal = 0;

    rows.forEach((row) => {
      const searchText = row.dataset.search || "";
      const matches = query === "" || searchText.includes(query);
      row.classList.toggle("is-hidden", !matches);
      if (matches) {
        visibleTotal += 1;
      }
    });

    emptyState.classList.toggle("is-hidden", visibleTotal > 0);
    if (countNode) {
      countNode.textContent = String(visibleTotal);
    }
  };

  searchInput.addEventListener("input", applyFilter);
  applyFilter();
});
