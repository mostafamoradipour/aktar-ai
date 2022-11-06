import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { DRACOLoader } from "three/examples/jsm/loaders/DRACOLoader";

export default function THREEInit(canvasRef, options) {
  const canvas = canvasRef.current;
  // const canvas = document.getElementById("main-scene");

  // Scene
  const scene = new THREE.Scene();

  // Camera setup
  const camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );

  const orthoCamera = new THREE.OrthographicCamera(50, -50, 50, -50, 1, 1000);

  // Renderer setup
  const renderer = new THREE.WebGL1Renderer({
    canvas: canvas,
    antialias: true,
  });
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, canvas.clientHeight);
  renderer.physicallyCorrectLights = true;

  // Controls
  let controls, orthoControls
  if (!options || options.controls !== false) {
    controls = new OrbitControls(camera, renderer.domElement);
    orthoControls = new OrbitControls(orthoCamera, renderer.domElement);
  }
  function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    window.addEventListener("resize", onWindowResize, false);
  }
  onWindowResize();

  // Loder setup
  // TODO - use ThreeJS loader manager
  const dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath("/");
  dracoLoader.setCrossOrigin('use-credentials');
  dracoLoader.setWithCredentials(true);
  const loader = new GLTFLoader();
  loader.setCrossOrigin('use-credentials');
  loader.setWithCredentials(true);
  loader.setDRACOLoader(dracoLoader);

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

  return {
    THREE,
    scene,
    renderer,
    camera,
    controls,
    orthoCamera,
    orthoControls,
    loader,
  };
}
