import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { DRACOLoader } from "three/examples/jsm/loaders/DRACOLoader";
import { sceneInitializedAtom } from "./atoms";
import { getRecoil, setRecoil } from "recoil-nexus";


const mainObjects = {
  renderer: null,
  scene: null,
  camera: null,
  controls: null,
  loader: null,
}

// functions to be executed server-side

export function setLoader() {

  // Loder setup
  // TODO - use ThreeJS loader manager
  const loader = new GLTFLoader();
  const dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath("/");
  loader.setDRACOLoader(dracoLoader);
  mainObjects.loader = loader;
}

export function setScene() {
  // Scene
  const scene = new THREE.Scene();
  mainObjects.scene = scene;
  console.log('added scene to mainObjects', mainObjects.scene);

}

// functions to be executed client-side

function setRendererDomElement(canvasRef) {
  const canvas = canvasRef.current;
  mainObjects.renderer.setSize(window.innerWidth, canvas.clientHeight);
  mainObjects.renderer.setPixelRatio(window.devicePixelRatio);
}

function setRenderer() {
  // Renderer setup
  const renderer = new THREE.WebGL1Renderer({
    // canvas: canvas,
    antialias: true,
  });
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.physicallyCorrectLights = true;
  mainObjects.renderer = renderer;
  console.log('added renderer to mainObjects', mainObjects.renderer);

}

function setCamera() {
  // Camera setup
  const camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );


  const orthoCamera = new THREE.OrthographicCamera(50, -50, 50, -50, 1, 1000);

  mainObjects.camera = { camera, orthoCamera };
}

function setControls(camera, options) {
  // Controls
  if (!options || options.controls !== false) {
    const controls = new OrbitControls(camera, mainObjects.renderer.domElement);
    const orthoControls = new OrbitControls(orthoCamera, mainObjects.renderer.domElement);
    mainObjects.controls = { controls, orthoControls };
  }
}

function onWindowResize() {
  mainObjects.camera.camera.aspect = window.innerWidth / window.innerHeight;
  mainObjects.camera.camera.updateProjectionMatrix();
  mainObjects.renderer.setSize(window.innerWidth, window.innerHeight);
  mainObjects.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  window.addEventListener("resize", onWindowResize, false);
}


export const scene = mainObjects.scene;


  // function handleFullScreen() {
  //   window.addEventListener("dblclick", () => {
  //     const fullscreenElement =
  //       document.fullscreenElement || document.webkitFullscreenElement;
  //     if (!fullscreenElement) {
  //       if (canvas.requestFullscreen) {
  //         canvas.requestFullscreen();
  //       } else if (canvas.webkitRequestFullscreen) {
  //         canvas.webkitRequestFullscreen();
  //       }
  //     } else {
  //       if (document.exitFullscreen) {
  //         document.exitFullscreen();
  //       } else if (document.webkitExitFullscreen) {
  //         canvas.webkitExitFullscreen();
  //       }
  //     }
  //   });
  // }
  // handleFullScreen();

