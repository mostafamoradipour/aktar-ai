import { Pane } from "tweakpane";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry";
import gsap from "gsap";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import THREEInit from "./THREE-init";
import * as THREE from "three";
import { sceneUtilsAtom, activeSceneOptionsAtom } from "./atoms";
import { getRecoil, setRecoil } from "recoil-nexus";
// TODO - call main properties once from every function
//  and use a secondary variable
export const main = {
  baseObjects: {
    THREE: {},
    scene: {},
    camera: {},
    renderer: {},
    controls: {},
    orthoCamera: {},
    orthoControls: {},
    loader: {},
  },
  activeCamera: {},
  activeControls: {},
  progress: {
    loadedAssets: [],
    endCondition: () => false,
    loadingState: {},
    updateLoadingState() {
      // TODO - optimize to use updateProgress only
      if (this.endCondition()) {
        this.loadingState.setShowLoading(false);
        return;
      }
      this.loadingState.setShowLoading(true);
    },
    onEnd: () => { },
    updateProgress(asset) {
      if (this.loadedAssets.includes(asset)) {
        return;
      }
      this.loadedAssets.push(asset);
      if (this.endCondition()) {
        this.updateLoadingState();
        this.onEnd();
      }
    },
  },
  envMapPath: "",
  canvasRef: {},
  lights: {
    spots: [],
  },
};

export function basicSetup(
  // TODO - add default options to other functions as well
  options = {
    controlLimits: true,
    controls: true,
  }
) {
  main.baseObjects = THREEInit(main.canvasRef, options);
  // console.log(main);
  main.baseObjects.scene.background = new THREE.Color(0xffffff);

  main.baseObjects.camera.position.set(0, 10, 0);

  if (options.controls) {
    if (!options.controlLimits) {
      main.activeControls = main.baseObjects.controls;
    } else {
      main.baseObjects.controls.enableDamping = true;
      main.baseObjects.controls.enablePan = false;
      main.baseObjects.controls.maxPolarAngle = THREE.MathUtils.degToRad(60);
      main.baseObjects.controls.minPolarAngle = THREE.MathUtils.degToRad(40);

      main.baseObjects.orthoControls.enableDamping = true;
      main.baseObjects.orthoControls.enablePan = true;
      main.baseObjects.orthoControls.maxPolarAngle =
        THREE.MathUtils.degToRad(0);
      main.baseObjects.orthoControls.minPolarAngle =
        THREE.MathUtils.degToRad(0);
      main.baseObjects.orthoControls.maxAzimuthAngle =
        THREE.MathUtils.degToRad(0);
      main.baseObjects.orthoControls.minAzimuthAngle =
        THREE.MathUtils.degToRad(0);
      main.activeControls = main.baseObjects.controls;
    }
  }
  main.activeCamera = main.baseObjects.camera;
}

// this has to keep loading assets and adding them on-the-fly
// so the loading is only shown at first
// the rest will keep going

// setShowLoading(true);
// applyDynamicAssetLoading();
// setShowLoading(false);

// Functions

export function applyEnvMap(mapPath) {
  main.envMapPath = mapPath;
  const cubeTextureLoader = new THREE.CubeTextureLoader();
  cubeTextureLoader.load(mapPath, (texture) => {
    main.baseObjects.scene.environment = texture;
    main.progress.updateProgress("envMap");
    // main.baseObjects.scene.background = texture;
  });
}

export function applyAllModels(models) {
  // Models = [{modelURL, count}]
  models.forEach((model) => {
    loadModel(
      model.modelURL,
      model.count,
      model.additionalObjectActions,
      model.additionalCloneActions,
      model.envMapIntensity
    );
  });
}

export function loadModel(
  modelURL,
  count,
  additionalObjectActions,
  additionalCloneActions,
  envMapIntensity
) {
  // scale,rotation,position
  main.baseObjects.loader.load(modelURL, (gltf) => {
    gltf.scene.rotateY(Math.PI / 2);
    additionalObjectActions(gltf.scene);
    count = count === 0 ? 0 : count || 1;
    if (count > 1) {
    const clones = new THREE.Group();
    clones.name = gltf.scene.name;
    for (let i = -(count / 2 - 0.5); i <= count / 2 - 0.5; i++) {
      const clone = gltf.scene.clone();
      if (additionalCloneActions) {
        additionalCloneActions(clone, i);
      } else {
        clone.position.x = i * 10;
      }
      clone.traverse((child) => {
        if (child.isMesh) {
          child.material.envMapIntensity = envMapIntensity || 6;
        }
      });
      clones.add(clone);
    }

    main.baseObjects.scene.add(clones);
    }
    main.baseObjects.scene.add(gltf.scene);
    main.progress.updateProgress(modelURL);
  });
  // console.log(main);
}

export function applyLights({ type }) {
  if (type === "custom") {
    const spotLight = new THREE.PointLight(0xfdf3c6, 10, 10);
    const target = new THREE.Object3D();
    spotLight.position.set(1, 3, 2.3);
    target.position.set(1, 0, 0);
    main.baseObjects.scene.add(target);
    spotLight.target = target;
    main.baseObjects.scene.add(spotLight.target);

    // spotLight.target.position.set(400, 130, 0);
    // main.baseObjects.scene.add(spotLight.target);
    // main.baseObjects.scene.add(spotLight);

    spotLight.position.y = 3;
    spotLight.castShadow = true;

    //Set up shadow properties for the light
    spotLight.shadow.mapSize.width = 1024;
    spotLight.shadow.mapSize.height = 1024;
    spotLight.shadow.camera.near = 1;
    spotLight.shadow.camera.far = 1000;
    spotLight.shadow.focus = 1;

    main.lights.spots.push(spotLight);

    main.baseObjects.scene.add(spotLight);

    // const spotLight2 = new THREE.SpotLight(0xffffff, 4);
    // spotLight2.position.set(20, 20, 50);
    // spotLight2.castShadow = true;

    // //Set up shadow properties for the light
    // spotLight2.shadow.mapSize.width = 2048; // default
    // spotLight2.shadow.mapSize.height = 2048; // default
    // spotLight2.shadow.camera.near = 0.1; // default
    // spotLight2.shadow.camera.far = 1000; // default
    // spotLight2.shadow.focus = 1; // default

    let hemiLight = new THREE.HemisphereLight(0xf5f5f5, 0xffffff, 1);

    const ambientLight = new THREE.AmbientLight(0xffffff);
    ambientLight.position.set(0, 20, 0);
    main.baseObjects.scene.add(
      hemiLight,
      //   spotLight
      //   // spotLight2
      ambientLight
    );
  }
  else if (type === "vector-space") {
    // const spotLight = new THREE.PointLight(0xfdf3c6, 100, 20);
    // const target = new THREE.Object3D();
    // spotLight.position.set(1 * 10, 15, 1 * 10);
    // target.position.set(250, 0, 300);
    // main.baseObjects.scene.add(target);
    // spotLight.target = target;
    // main.baseObjects.scene.add(spotLight.target);

    // // spotLight.target.position.set(400, 130, 0);
    // // main.baseObjects.scene.add(spotLight.target);
    // // main.baseObjects.scene.add(spotLight);

    // spotLight.castShadow = true;

    // //Set up shadow properties for the light
    // spotLight.shadow.mapSize.width = 1024;
    // spotLight.shadow.mapSize.height = 1024;
    // spotLight.shadow.camera.near = 1;
    // spotLight.shadow.camera.far = 1000;
    // spotLight.shadow.focus = 1;

    // main.lights.spots.push(spotLight);
    // main.baseObjects.scene.add(spotLight);

    // for (let i = 0; i < 300; i += 10) {
    //   for (let j = 0; j < 500; j += 10) {
    //     let spotLightClone = spotLight.clone()
    //     spotLightClone.position.set(j, 15, i)
    //     main.lights.spots.push(spotLightClone);
    //     main.baseObjects.scene.add(spotLightClone);
    //   }

    // }



    // const spotLight2 = new THREE.SpotLight(0xffffff, 4);
    // spotLight2.position.set(20, 20, 50);
    // spotLight2.castShadow = true;

    // //Set up shadow properties for the light
    // spotLight2.shadow.mapSize.width = 2048; // default
    // spotLight2.shadow.mapSize.height = 2048; // default
    // spotLight2.shadow.camera.near = 0.1; // default
    // spotLight2.shadow.camera.far = 1000; // default
    // spotLight2.shadow.focus = 1; // default

    let hemiLight = new THREE.HemisphereLight(0xf5f5f5, 0xffffff, 1);

    const ambientLight = new THREE.AmbientLight(0xffffff);
    ambientLight.position.set(0, 20, 0);
    main.baseObjects.scene.add(
      hemiLight,
      ambientLight
    );
  }
  else {
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
    main.baseObjects.scene.add(
      hemiLight,
      spotLight
      // spotLight2
      //  ambientLight
    );
  }
}

export function applyAnimations(options) {
  if (!options || options.type === "store") {
    const lookTarget = new THREE.Vector3(0, 0, 0);
    const tl = gsap.timeline();
    tl.to(main.baseObjects.camera.position, {
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
            main.baseObjects.camera.lookAt(lookTarget);
          },
        },
        "-=1.5"
      )
      .to(
        main.baseObjects.camera.position,
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
  } else if (options.type === "custom") {
    const tl = gsap.timeline();
    main.baseObjects.camera.position.set(6, 2, -3);
    const lookTarget = new THREE.Vector3(-1, 0.7, 4.6);
    main.baseObjects.controls.target = lookTarget;
    // main.baseObjects.camera.lookAt(lookTarget);
    // tl.to(main.baseObjects.camera.position, {
    //   duration: 2,
    //   z: 6.4,
    //   delay: 1,
    //   ease: "power3.inOut",
    // })
    //   .to(
    //     lookTarget,
    //     {
    //       duration: 2,
    //       z: 3,
    //       ease: "power3.inOut",
    //       onUpdate: () => {
    //         main.baseObjects.controls.target = lookTarget;
    //       },
    //     },
    //     "-=2"
    //   )
    //   .to(
    //     lookTarget,
    //     {
    //       duration: 2,
    //       y: 1.5,
    //       ease: "power3.inOut",
    //       onUpdate: () => {
    //         main.baseObjects.controls.target = lookTarget;
    //       },
    //     },
    //     "-=2"
    //   )
    //   .to(main.baseObjects.camera.position, {
    //     duration: 1,
    //     x: 5.8,
    //     ease: "power3.in",
    //   })
    //   .to(
    //     main.baseObjects.camera.position,
    //     {
    //       duration: 1,
    //       y: 5.1,
    //       ease: "power3",
    //     },
    //     "-=1"
    //   );
  } else if (options.type === "factory") {
    const lookTarget = new THREE.Vector3(0, 0, 0);
    const tl = gsap.timeline();
    tl.to(main.baseObjects.camera.position, {
      duration: 2,
      z: -20,
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
            main.baseObjects.camera.lookAt(lookTarget);
          },
        },
        "-=1.5"
      )
      .to(
        main.baseObjects.camera.position,
        {
          duration: 1,
          x: 20,
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
}

export function applyDomInteractions() {
  const interactions = {
    topView: () => {
      if (main.activeCamera === main.baseObjects.camera) {
        main.baseObjects.orthoCamera.left = 10;
        main.baseObjects.orthoCamera.right = -10;
        main.baseObjects.orthoCamera.top = 10;
        main.baseObjects.orthoCamera.bottom = -10;
        main.baseObjects.orthoCamera.position.set(0, 5, 0);
        main.baseObjects.orthoCamera.lookAt(new THREE.Vector3(0, 0, 0));
        main.activeCamera = main.baseObjects.orthoCamera;

        main.baseObjects.orthoControls.enableDamping = true;
        main.baseObjects.orthoControls.enablePan = true;
        main.baseObjects.orthoControls.maxPolarAngle =
          THREE.MathUtils.degToRad(0);
        main.baseObjects.orthoControls.minPolarAngle =
          THREE.MathUtils.degToRad(0);
        main.baseObjects.orthoControls.maxAzimuthAngle =
          THREE.MathUtils.degToRad(0);
        main.baseObjects.orthoControls.minAzimuthAngle =
          THREE.MathUtils.degToRad(0);

        main.activeControls = main.baseObjects.orthoControls;

        main.baseObjects.scene.traverse((child) => {
          if (child.isMesh) {
            child.material.envMapIntensity = 2;
          }
        });
      } else {
        main.baseObjects.camera.position.set(15, 10, -10);
        main.baseObjects.scene.traverse((child) => {
          if (child.isMesh) {
            child.material.envMapIntensity = 3;
          }
        });
        main.activeCamera = main.baseObjects.camera;
        main.activeControls = main.baseObjects.controls;
      }
    },
    filteredView: () => {
      if (!getRecoil(activeSceneOptionsAtom).filteredView) {
        main.baseObjects.scene.traverse((child) => {
          if (child.isMesh && child.name !== "human") {
            child.visible = false;
          }
        });
      } else {
        main.baseObjects.scene.traverse((child) => {
          child.visible = true;
        });
      }
      setRecoil(activeSceneOptionsAtom, {
        ...getRecoil(activeSceneOptionsAtom),
        filteredView: !getRecoil(activeSceneOptionsAtom).filteredView,
      });
    },
    toggleCamera: () => {
      if (main.activeCamera === main.baseObjects.camera) {
        setActiveCamera(main.baseObjects.orthoCamera);
        setActiveControls(main.baseObjects.orthoControls);
      } else {
        setActiveCamera(main.baseObjects.camera);
        setActiveControls(main.baseObjects.controls);
      }
    },
    toggleScene: () => {
      if (main.baseObjects.scene.visible) {
        main.baseObjects.scene.visible = false;
      } else {
        main.baseObjects.scene.visible = true;
      }
    },
    toggleLights: () => {
      if (main.baseObjects.scene.children[0].visible) {
        main.baseObjects.scene.children[0].visible = false;
      } else {
        main.baseObjects.scene.children[0].visible = true;
      }
    },
    toggleEnvMap: () => {
      if (main.baseObjects.scene.environment) {
        main.baseObjects.scene.environment.dispose();
        main.baseObjects.scene.environment = null;
      } else {
        applyEnvMap(main.envMapPath);
      }
    },
  };
  // setSceneUtils( interactions);
  setRecoil(sceneUtilsAtom, interactions);
  // Object.keys(interactions).forEach((key) => {
  //   document.getElementById(key).addEventListener("click", interactions[key]);
  // });
}

export function animate() {
  requestAnimationFrame(animate);
  if (main.baseObjects.controls) {
    main.baseObjects.controls.update();
  }
  // console.log(main.lights);
  // main.lights.spotHelper ? main.lights.spotHelper.update() : null;
  main.baseObjects.renderer.render(main.baseObjects.scene, main.activeCamera);
}

// THREE objects
export function addPlane({ width, height, direction, position, rotation }) {
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
  const planeMaterial = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    side: THREE.DoubleSide,
    envMapIntensity: 1,
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

  main.baseObjects.scene.add(plane);
}

// Debug
export function debugTHREE() {
  // Helper Setup
  const lightHelper = new THREE.PointLightHelper(main.lights.spots[0], 10, 0xf35753);
  main.lights.pointHelper = lightHelper;
  // const helper = new THREE.CameraHelper(spotLight.shadow.camera);
  // main.baseObjects.scene.add(helper);
  main.baseObjects.scene.add(
    lightHelper,
    // new THREE.AxesHelper(500)
  );
  // const pane = new Pane();
  // const cameraPane = pane.addFolder({
  //   title: "camera",
  //   expanded: true,
  // });
  // cameraPane.addInput(main.baseObjects.camera.position, "x", {
  //   min: -10,
  //   max: 10,
  //   step: 0.1,
  // });
  // cameraPane.addInput(main.baseObjects.camera.position, "y", {
  //   min: -10,
  //   max: 10,
  //   step: 0.1,
  // });
  // cameraPane.addInput(main.baseObjects.camera.position, "z", {
  //   min: -10,
  //   max: 10,
  //   step: 0.1,
  // });
  // const spotLightPane = pane.addFolder({
  //   title: "spotLight",
  // });
  // spotLightPane.addInput(spotLight.position, "x", {
  //   min: -1000,
  //   max: 1000,
  //   step: 0.1,
  // });
}

export function addGrid(w, h) {
  const gridHelper = new THREE.GridHelper(w, h);
  main.baseObjects.scene.add(
    gridHelper
  );
}

export function addAxisHelper(size) {
  main.baseObjects.scene.add(
    new THREE.AxesHelper(size)
  );
}
