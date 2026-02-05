import * as THREE from "https://unpkg.com/three@0.164.0/build/three.module.js";
import { GLTFLoader } from "https://unpkg.com/three@0.164.0/examples/jsm/loaders/GLTFLoader.js";

let atomScene;
let atomCamera;
let atomRenderer;
let atomAvatar = null;
const atomClock = new THREE.Clock();

function animateAvatar() {
  requestAnimationFrame(animateAvatar);
  const t = atomClock.getElapsedTime();

  if (atomAvatar) {
    atomAvatar.position.y = -1.2 + 0.05 * Math.sin(t * 1.2);
    atomAvatar.rotation.y = 0.08 * Math.sin(t * 0.6);
  }

  if (atomScene && atomCamera && atomRenderer) {
    atomScene.traverse((obj) => {
      if (obj.isMesh && obj.material && obj.material.emissive) {
        obj.material.emissiveIntensity = 0.6 + Math.sin(Date.now() * 0.0015) * 0.35;
      }
    });
    atomRenderer.render(atomScene, atomCamera);
  }
}

export function initAtomAvatar(containerId = "atom-avatar") {
  const container = document.getElementById(containerId);
  if (!container) {
    console.warn("ATOM avatar container not found");
    return;
  }

  atomScene = new THREE.Scene();
  atomCamera = new THREE.PerspectiveCamera(
    75,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
  );
  atomCamera.position.set(0, 1.2, 3);

  atomRenderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  atomRenderer.setSize(container.clientWidth, container.clientHeight);
  container.innerHTML = "";
  container.appendChild(atomRenderer.domElement);

  const ambient = new THREE.AmbientLight(0x222222);
  const directional = new THREE.DirectionalLight(0x00ffff, 1.2);
  directional.position.set(1, 3, 2);
  atomScene.add(ambient);
  atomScene.add(directional);

  const loader = new GLTFLoader();
  loader.load(
    "/static/models/atom_avatar.glb",
    (gltf) => {
      atomAvatar = gltf.scene;
      atomAvatar.scale.set(2.2, 2.2, 2.2);
      atomAvatar.position.y = -1.2;
      atomScene.add(atomAvatar);
      if (!atomClock.running) atomClock.start();
    },
    undefined,
    (error) => {
      console.error("ATOM Avatar Load Error:", error);
    }
  );

  if (!atomClock.running) {
    atomClock.start();
  }
  animateAvatar();

  window.atomSpeak = function (text) {
    if (!window.speechSynthesis) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.pitch = 1.1;
    utterance.rate = 0.95;
    const voices = speechSynthesis.getVoices();
    utterance.voice =
      voices.find((v) => v.name && v.name.includes("David")) ||
      voices.find((v) => v.default) ||
      null;
    speechSynthesis.speak(utterance);
  };

  window.atomPulse = function (colorHex = 0x00ffff) {
    if (!atomAvatar) return;
    atomAvatar.traverse((obj) => {
      if (obj.isMesh && obj.material && obj.material.emissive) {
        const original = obj.material.emissiveIntensity;
        obj.material.emissive.setHex(colorHex);
        obj.material.emissiveIntensity = 4;
        setTimeout(() => {
          obj.material.emissiveIntensity = original ?? 1;
        }, 300);
      }
    });
  };

  window.triggerAtomResponse = function (msg) {
    atomPulse(0xff00ff);
    if (msg) {
      atomSpeak(msg);
    }
  };

  window.atomFocus = function (x = 0, y = 1.2) {
    if (atomCamera) {
      atomCamera.lookAt(x, y, 0);
    }
    if (atomAvatar) {
      const head = atomAvatar.getObjectByName("Head");
      if (head) {
        const originalRot = head.rotation.x;
        head.rotation.x += 0.2;
        setTimeout(() => {
          head.rotation.x = originalRot;
        }, 250);
      }
    }
  };

  const doctrineGeometry = new THREE.RingGeometry(1.5, 1.6, 32);
  const doctrineMaterial = new THREE.MeshBasicMaterial({ color: 0xff00ff, side: THREE.DoubleSide });
  const doctrineRing = new THREE.Mesh(doctrineGeometry, doctrineMaterial);
  doctrineRing.rotation.x = Math.PI / 2;
  doctrineRing.position.y = 2.5;
  atomScene.add(doctrineRing);

  setInterval(() => {
    if (atomScene) {
      atomScene.rotation.y += 0.0015;
    }
  }, 16);
}

window.initAtomAvatar = initAtomAvatar;
