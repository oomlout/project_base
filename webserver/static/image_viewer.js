document.addEventListener("DOMContentLoaded", () => {
  const dialog = document.getElementById("image-viewer");
  const dataNode = document.getElementById("image-viewer-data");
  if (!dialog || !dataNode) {
    return;
  }

  let payload = null;
  try {
    payload = JSON.parse(dataNode.textContent || "{}");
  } catch (error) {
    payload = null;
  }
  if (!payload || !payload.parts) {
    return;
  }

  const imageNode = document.getElementById("image-viewer-image");
  const titleNode = document.getElementById("image-viewer-title");
  const pathNode = document.getElementById("image-viewer-path");
  const countNode = document.getElementById("image-viewer-count");
  const previousButton = document.getElementById("image-viewer-prev");
  const nextButton = document.getElementById("image-viewer-next");
  const closeButton = document.getElementById("image-viewer-close");
  const originalLink = document.getElementById("image-viewer-original");

  if (!imageNode || !titleNode || !pathNode || !countNode || !previousButton || !nextButton || !closeButton || !originalLink) {
    return;
  }

  let activePartId = "";
  let activeIndex = 0;
  let activeTrigger = null;

  const getActivePart = () => payload.parts[activePartId] || null;

  const preloadNeighbors = () => {
    const part = getActivePart();
    if (!part || !Array.isArray(part.images) || part.images.length < 2) {
      return;
    }
    const previous = part.images[(activeIndex - 1 + part.images.length) % part.images.length];
    const next = part.images[(activeIndex + 1) % part.images.length];
    [previous, next].forEach((image) => {
      const preloader = new Image();
      preloader.src = image.modalUrl;
    });
  };

  const render = () => {
    const part = getActivePart();
    if (!part || !Array.isArray(part.images) || part.images.length === 0) {
      dialog.close();
      return;
    }

    if (activeIndex < 0) {
      activeIndex = part.images.length - 1;
    }
    if (activeIndex >= part.images.length) {
      activeIndex = 0;
    }

    const image = part.images[activeIndex];
    imageNode.src = image.modalUrl;
    imageNode.alt = `${part.partName} - ${image.relativePath}`;
    if (image.width && image.height) {
      imageNode.width = image.width;
      imageNode.height = image.height;
    } else {
      imageNode.removeAttribute("width");
      imageNode.removeAttribute("height");
    }

    titleNode.textContent = part.partName;
    pathNode.textContent = image.relativePath;
    countNode.textContent = `${activeIndex + 1} of ${part.images.length}`;
    originalLink.href = image.originalUrl;

    const multipleImages = part.images.length > 1;
    previousButton.disabled = !multipleImages;
    nextButton.disabled = !multipleImages;

    preloadNeighbors();
  };

  const openViewer = (partId, index, trigger) => {
    const part = payload.parts[partId];
    if (!part || !Array.isArray(part.images) || part.images.length === 0) {
      return;
    }
    activePartId = partId;
    activeIndex = Number.isFinite(index) ? index : 0;
    activeTrigger = trigger || null;
    render();
    if (!dialog.open) {
      dialog.showModal();
    }
    closeButton.focus();
  };

  document.querySelectorAll("[data-image-viewer-trigger='true']").forEach((trigger) => {
    trigger.addEventListener("click", (event) => {
      const partId = trigger.getAttribute("data-part-id") || "";
      const index = Number.parseInt(trigger.getAttribute("data-image-index") || "0", 10);
      if (!payload.parts[partId]) {
        return;
      }
      event.preventDefault();
      openViewer(partId, Number.isFinite(index) ? index : 0, trigger);
    });
  });

  previousButton.addEventListener("click", () => {
    activeIndex -= 1;
    render();
  });

  nextButton.addEventListener("click", () => {
    activeIndex += 1;
    render();
  });

  closeButton.addEventListener("click", () => {
    dialog.close();
  });

  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      dialog.close();
    }
  });

  dialog.addEventListener("close", () => {
    imageNode.removeAttribute("src");
    if (activeTrigger && typeof activeTrigger.focus === "function") {
      activeTrigger.focus();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (!dialog.open) {
      return;
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      activeIndex -= 1;
      render();
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      activeIndex += 1;
      render();
    }
  });
});
