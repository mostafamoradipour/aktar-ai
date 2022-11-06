import { Pane } from "tweakpane";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry";
import gsap from "gsap";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import THREEInit from "./THREE-init";
import { sceneUtilsAtom, activeSceneOptionsAtom } from "./atoms";
import { getRecoil, setRecoil } from "recoil-nexus";

export default function storeSceneSetup({
  canvasRef,
  models,
  envMapPath,
  showLoading,
  setShowLoading,
  humanCounter = false
}) {
  const {
    THREE,
    scene,
    camera,
    renderer,
    controls,
    orthoCamera,
    orthoControls,
    loader,
  } = THREEInit(canvasRef);

  let activeCamera;
  let activeControls;
  // Basic THREE.js setups
  function basicSetups() {
    scene.background = new THREE.Color(0xffffff);

    camera.position.set(0, 10, 0);

    controls.enableDamping = true;
    controls.enablePan = false;
    controls.maxPolarAngle = THREE.MathUtils.degToRad(60);
    controls.minPolarAngle = THREE.MathUtils.degToRad(40);

    orthoControls.enableDamping = true;
    orthoControls.enablePan = true;
    orthoControls.maxPolarAngle = THREE.MathUtils.degToRad(0);
    orthoControls.minPolarAngle = THREE.MathUtils.degToRad(0);
    orthoControls.maxAzimuthAngle = THREE.MathUtils.degToRad(0);
    orthoControls.minAzimuthAngle = THREE.MathUtils.degToRad(0);

    activeCamera = camera;
    activeControls = controls;
  }
  basicSetups();
  // Progress Object for tracking scene loading
  const progress = {
    loadedAssets: [],
    endCondition: () => false,
    onEnd: () => { },
    updateProgress(asset) {
      if (this.loadedAssets.includes(asset)) {
        return;
      }
      this.loadedAssets.push(asset);
      if (this.endCondition()) {
        this.onEnd();
      }
    },
  };

  // Core Process
  setShowLoading(true);
  const onLoad = () => setShowLoading(false);
  addPlane({ width: 60, height: 15, position: { x: -2, z: -30, y: 7.5 } })
  addPlane({ width: 80, height: 15, position: { x: 28, y: 7.5, z: 10 }, rotation: { y: 90 } })
  addPlane({ width: 60, height: 80, direction: "horizontal", position: { x: -2, z: 10 } })
  loadAssets(progress, onLoad, models, envMapPath);
  applyAnimations();
  applyDomInteractions();
  animate();
  humanCounter && addHumanCounter();
  // Functions

  function loadAssets(progress, onLoad, models, envMapPath) {
    progress.endCondition = () => {
      return progress.loadedAssets.length === 3;
    };
    progress.onEnd = onLoad;
    applyEnvMap(envMapPath);
    applyAllModels(models);
    applyLights();
  }

  function applyEnvMap(mapPath) {
    const cubeTextureLoader = new THREE.CubeTextureLoader();
    cubeTextureLoader.load(mapPath, (texture) => {
      scene.environment = texture;
      progress.updateProgress("envMap");
    });
    // scene.background = environmentMap;
  }

  function applyAllModels(models) {
    // Models = [{modelURL, count}]
    models.forEach((model) => {
      loadModel(
        model.modelURL,
        model.count,
        model.additionalObjectActions,
        model.additionalCloneActions
      );
    });
  }

  function loadModel(
    modelURL,
    count,
    additionalObjectActions,
    additionalCloneActions
  ) {
    // scale,rotation,position
    loader.load(modelURL, (gltf) => {
      gltf.scene.rotateY(Math.PI / 2);
      additionalObjectActions(gltf.scene);
      count = count || 1;
      const clones = new THREE.Group();
      for (let i = -(count / 2 - 0.5); i <= count / 2 - 0.5; i++) {
        const clone = gltf.scene.clone();
        if (additionalCloneActions) {
          additionalCloneActions(clone);
        } else {
          clone.position.x = i * 10;
        }
        clones.add(clone);
      }
      clones.traverse((child) => {
        if (child.isMesh) {
          child.material.envMapIntensity = 4;
        }
      });

      scene.add(clones);
      progress.updateProgress(modelURL);
    });
  }

  function applyLights() {
    const spotLight = new THREE.SpotLight(0xffffff, 3, 1000, 2.8, 1);
    spotLight.position.set(0, 130.4, 65.2);
    spotLight.castShadow = true;

    //Set up shadow properties for the light
    spotLight.shadow.mapSize.width = 2048; // default
    spotLight.shadow.mapSize.height = 2048; // default
    spotLight.shadow.camera.near = 0.1; // default
    spotLight.shadow.camera.far = 1000; // default
    spotLight.shadow.focus = 1; // default

    const spotLight2 = new THREE.SpotLight(0xffffff, 4);
    spotLight2.position.set(20, 20, 50);
    spotLight2.castShadow = true;

    //Set up shadow properties for the light
    spotLight2.shadow.mapSize.width = 2048; // default
    spotLight2.shadow.mapSize.height = 2048; // default
    spotLight2.shadow.camera.near = 0.1; // default
    spotLight2.shadow.camera.far = 1000; // default
    spotLight2.shadow.focus = 1; // default

    let hemiLight = new THREE.HemisphereLight(0xf5f5f5, 0xffffff, 1);

    // const ambientLight = new THREE.AmbientLight(0xffffff);
    // ambientLight.position.set(0, 20, 0);
    scene.add(
      hemiLight,
      spotLight
      // spotLight2
      //  ambientLight
    );
  }

  function applyAnimations() {
    const lookTarget = new THREE.Vector3(0, 0, 0);
    const tl = gsap.timeline();
    tl.to(camera.position, {
      duration: 2,
      z: 40,
      delay: 1,
      ease: "power3.inOut",
    })
      .to(
        lookTarget,
        {
          duration: 2,
          z: 10,
          ease: "power3.inOut",
          onUpdate: () => {
            camera.lookAt(lookTarget);
          },
        },
        "-=1.5"
      )
      .to(
        camera.position,
        {
          duration: 1,
          x: -20,
          ease: "power3.inOut",
        },
        "-=1"
      );
    // .to(lookTarget, {
    //   duration: 2,
    //   z: 0,
    //   ease: "power3.inOut",
    //   onUpdate: () => {;
    //     camera.lookAt(lookTarget);
    //   },
    // }).to(lookTarget, {
    //   duration: 2,
    //   x: 0,
    //   ease: "power3.inOut",
    //   onUpdate: () => {
    //     camera.lookAt(lookTarget);
    //   },
    // },"-=2");
  }

  function applyDomInteractions() {
    const interactions = {
      topView: () => {
        if (activeCamera === camera) {
          activeCamera = orthoCamera;
          activeControls = orthoControls;
          orthoCamera.position.set(0, 10, 0);
          scene.traverse((child) => {
            if (child.isMesh) {
              child.material.envMapIntensity = 2;
            }
          });
        } else {
          activeCamera = camera;
          activeControls = controls;
          camera.position.set(35, 10, 40);
          scene.traverse((child) => {
            if (child.isMesh) {
              child.material.envMapIntensity = 5;
            }
          });
        }
      },
      filteredView: () => {
        if (!getRecoil(activeSceneOptionsAtom).filteredView) {
          scene.traverse((child) => {
            if (child.isMesh && child.name !== "human") {
              child.visible = false;
            }
          });
        } else {
          scene.traverse((child) => {
            child.visible = true;
          });
        }
        setRecoil(activeSceneOptionsAtom, {
          ...getRecoil(activeSceneOptionsAtom),
          filteredView: !getRecoil(activeSceneOptionsAtom).filteredView,
        });
      },
      toggleCamera: () => {
        if (activeCamera === camera) {
          setActiveCamera(orthoCamera);
          setActiveControls(orthoControls);
        } else {
          setActiveCamera(camera);
          setActiveControls(controls);
        }
      },
      toggleScene: () => {
        if (scene.visible) {
          scene.visible = false;
        } else {
          scene.visible = true;
        }
      },
      toggleLights: () => {
        if (scene.children[0].visible) {
          scene.children[0].visible = false;
        } else {
          scene.children[0].visible = true;
        }
      },
      toggleEnvMap: () => {
        if (scene.environment) {
          scene.environment.dispose();
          scene.environment = null;
        } else {
          applyEnvMap(envMapPath);
        }
      },
    };
    // setSceneUtils( interactions);
    setRecoil(sceneUtilsAtom, interactions);
    // Object.keys(interactions).forEach((key) => {
    //   document.getElementById(key).addEventListener("click", interactions[key]);
    // });
  }

  // THREE objects
  function addPlane({ width, height, direction, position, rotation }) {
    const defaultOptions = {
      width: 100,
      height: 100,
      direction: "vertical",
      position: {
        x: 0,
        y: 0,
        z: 0,
      },
      rotation: {
        x: 0,
        y: 0,
        z: 0,
      },
    };

    const planeGeometry = new THREE.BoxBufferGeometry(width, height, 0.1);


    const cubeTextureLoader = new THREE.CubeTextureLoader();
    const envMap = cubeTextureLoader.load(envMapPath)

    const planeMaterial = new THREE.MeshPhysicalMaterial({
      color: 0xffffff,
      side: THREE.DoubleSide,
      envMapIntensity: 1.9,
      envMap: envMap,
      reflectivity: 0,
      metalness: 0.3,
    });
    const plane = new THREE.Mesh(planeGeometry, planeMaterial);
    plane.receiveShadow = true;
    // plane.position.x = 500;

    // direction
    direction == "horizontal" ? plane.rotateX(THREE.MathUtils.degToRad(90)) : "";

    // position
    position
      ? plane.position.set(position.x || 0, position.y || 0, position.z || 0)
      : "";

    // rotation
    if (rotation) {
      plane.rotateX(THREE.MathUtils.degToRad(rotation.x || 0));
      plane.rotateY(THREE.MathUtils.degToRad(rotation.y || 0));
      plane.rotateZ(THREE.MathUtils.degToRad(rotation.z || 0));
    }
    scene.add(plane);
  }

  function addHumanCounter() {
    let count = 0;
    setTimeout(() => {
      scene.traverse((child) => {
        // if (child.isMesh && child.name === "human") {
        // count++
        console.log(child.uuid);
        // }
      });
      console.log(scene)
      // console.log(count);
    }
      , 1000);

  }

  // Debug
  function debugTHREE() {
    // Helper Setup
    const lightHelper = new THREE.SpotLightHelper(spotLight);
    const gridHelper = new THREE.GridHelper(200, 50);
    scene.add(lightHelper, gridHelper, new THREE.AxesHelper(500));
    const pane = new Pane();
    const cameraPane = pane.addFolder({
      title: "camera",
      expanded: true,
    });
    cameraPane.addInput(camera.position, "x", {
      min: -1000,
      max: 1000,
      step: 0.1,
    });
    const spotLightPane = pane.addFolder({
      title: "spotLight",
    });
    spotLightPane.addInput(spotLight.position, "x", {
      min: -1000,
      max: 1000,
      step: 0.1,
    });
  }
  function animate() {
    requestAnimationFrame(animate);
    activeControls.update();
    renderer.render(scene, activeCamera);
  }
  // animate();
}
