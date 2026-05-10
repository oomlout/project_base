document.addEventListener("submit", (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) {
    return;
  }

  const message = form.dataset.confirmMessage;
  if (!message) {
    return;
  }

  if (!window.confirm(message)) {
    event.preventDefault();
  }
});

document.addEventListener("dblclick", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  const selectableTarget =
    target.closest("[data-selectable-path='true']") ||
    target.closest("[data-selectable-breadcrumb='true']");
  if (!(selectableTarget instanceof HTMLElement)) {
    return;
  }

  const selection = window.getSelection();
  if (!selection) {
    return;
  }

  const range = document.createRange();
  range.selectNodeContents(selectableTarget);
  selection.removeAllRanges();
  selection.addRange(range);
});