document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("explore-search");
  const rows = Array.from(document.querySelectorAll(".part-card"));
  const emptyState = document.getElementById("explore-empty");
  const countNode = document.getElementById("visible-count");
  const searchFieldInputs = Array.from(document.querySelectorAll(".search-field-chip__input"));
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

  const selectedFields = () => {
    const checked = searchFieldInputs
      .filter((input) => input.checked)
      .map((input) => input.value);
    if (checked.length > 0) {
      return checked;
    }
    return searchFieldInputs
      .filter((input) => input.dataset.defaultChecked === "true")
      .map((input) => input.value);
  };

  const applyFilter = () => {
    const query = searchInput.value.trim().toLowerCase();
    const activeFields = selectedFields();
    let visibleTotal = 0;

    rows.forEach((row) => {
      const searchText = activeFields
        .map((fieldName) => row.getAttribute(`data-search-${fieldName.replace(/_/g, "-")}`) || "")
        .join(" ");
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
  searchFieldInputs.forEach((input) => input.addEventListener("change", applyFilter));
  applyFilter();
});
