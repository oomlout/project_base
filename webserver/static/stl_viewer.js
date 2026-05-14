import * as THREE from "three";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

function createViewer(canvas) {
  const width = canvas.clientWidth || 480;
  const height = canvas.clientHeight || 360;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(width, height, false);
  renderer.setClearColor(0xffffff);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, width / height, 0.01, 10000);
  camera.position.set(0, 0, 5);

  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
  dirLight.position.set(1, 2, 3);
  scene.add(dirLight);
  const backLight = new THREE.DirectionalLight(0xffffff, 0.4);
  backLight.position.set(-1, -1, -2);
  scene.add(backLight);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;

  let animFrameId = null;
  let resizeObserver = null;

  function loadSTL(url) {
    const loader = new STLLoader();
    loader.load(
      url,
      (geometry) => {
        geometry.computeBoundingBox();
        const box = geometry.boundingBox;
        const center = new THREE.Vector3();
        box.getCenter(center);
        geometry.translate(-center.x, -center.y, -center.z);

        const size = new THREE.Vector3();
        box.getSize(size);
        const maxDim = Math.max(size.x, size.y, size.z);
        const fovRad = (camera.fov * Math.PI) / 180;
        const dist = (maxDim / 2) / Math.tan(fovRad / 2) * 1.6;
        camera.position.set(dist * 0.6, dist * 0.4, dist);
        camera.near = dist / 100;
        camera.far = dist * 10;
        camera.updateProjectionMatrix();
        controls.target.set(0, 0, 0);
        controls.update();

        const material = new THREE.MeshLambertMaterial({
          color: 0xb2d44e,
        });
        scene.add(new THREE.Mesh(geometry, material));

        // Edge highlight overlay
        const edges = new THREE.EdgesGeometry(geometry, 20);
        const lineMat = new THREE.LineBasicMaterial({
          color: 0x7aaa18,
          transparent: true,
          opacity: 0.45,
        });
        scene.add(new THREE.LineSegments(edges, lineMat));
      },
      undefined,
      (err) => {
        console.error("STL load error", err);
      }
    );
  }

  resizeObserver = new ResizeObserver(() => {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    if (w === 0 || h === 0) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  });
  resizeObserver.observe(canvas);

  // Fire an initial resize once the canvas is actually painted
  requestAnimationFrame(() => {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    if (w > 0 && h > 0) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
  });

  function animate() {
    animFrameId = requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  return {
    loadSTL,
    resize(w, h) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    },
    dispose() {
      if (animFrameId !== null) cancelAnimationFrame(animFrameId);
      if (resizeObserver) resizeObserver.disconnect();
      controls.dispose();
      renderer.dispose();
    },
  };
}

// ── Inline page viewers (canvas[data-stl-url]) ───────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("canvas[data-stl-url]").forEach((canvas) => {
    // Popover canvases are inside display:none parents — init lazily on first visibility
    const isPopover = canvas.classList.contains("stl-viewer--popover");
    if (isPopover) {
      let viewer = null;
      const trigger = canvas.closest(".file-list__link--stl");
      if (trigger) {
        trigger.addEventListener("mouseenter", () => {
          if (viewer) return;
          viewer = createViewer(canvas);
          viewer.loadSTL(canvas.dataset.stlUrl);
        }, { once: true });
      }
    } else {
      const viewer = createViewer(canvas);
      viewer.loadSTL(canvas.dataset.stlUrl);
    }
  });
});

// ── Modal viewer API ──────────────────────────────────────────────────────────
let _modalViewer = null;

window.STLViewerModal = {
  mount(canvas, url) {
    if (_modalViewer) {
      _modalViewer.dispose();
      _modalViewer = null;
    }
    _modalViewer = createViewer(canvas);
    _modalViewer.loadSTL(url);
    // Force a resize after the browser has painted the now-visible canvas
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const w = canvas.clientWidth;
        const h = canvas.clientHeight;
        if (w > 0 && h > 0 && _modalViewer) {
          _modalViewer.resize(w, h);
        }
      });
    });
  },
  unmount() {
    if (_modalViewer) {
      _modalViewer.dispose();
      _modalViewer = null;
    }
  },
};
