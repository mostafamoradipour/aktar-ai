import { useEffect, useRef, useState } from "react";
import storeSceneSetup from "../utilities/THREE-scene-setup-store";
import { showLoadingAtom, csrfTokenAtom } from "../utilities/atoms";
import { useRecoilState } from "recoil";
import gsap from "gsap";
import axios from "axios";
import styles from "./styles.module.scss";
import Modal from "./modal";
import THREEInit from "@/components/utilities/THREE-init";
import { GLTF } from "three/examples/jsm/loaders/GLTFLoader";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import * as THREE from "three";

export default function DigitalTwin({ planeModel, setPlaneModel, reset }) {
  const [loader, setLoader] = useState(null);
  const [scene, setScene] = useState<THREE.Scene>(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    let {
      THREE,
      scene,
      renderer,
      camera,
      controls,
      orthoCamera,
      orthoControls,
      loader,
    } = THREEInit(canvasRef);
    setLoader(loader);
    setScene(scene);
    const cubeTextureLoader = new THREE.CubeTextureLoader();
    cubeTextureLoader.load(
      [
        "/texture/cubic/px.png",
        "/texture/cubic/nx.png",
        "/texture/cubic/py.png",
        "/texture/cubic/ny.png",
        "/texture/cubic/pz.png",
        "/texture/cubic/nz.png",
      ],
      (texture) => {
        scene.environment = texture;
      }
    );
    scene.background = new THREE.Color(0xffffff);
    let hemiLight = new THREE.HemisphereLight(0xf5f5f5, 0xffffff, 1);
    scene.add(hemiLight);

    camera.position.set(0, 10, 20);

    // let controls = new OrbitControls(camera, renderer.domElement);

    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      // mixer.update(clock.getDelta());
      renderer.render(scene, camera);
    }
    animate();
  }, []);

  useEffect(() => {
    if (scene !== null) {
      // scene?.traverse(function (child) {
      //   if ((child as any).isAdded === true) {
      //     scene.remove(child);
      //   }
      // });
      // TODO - Find a better way to reset the scene
      location.reload();
    }
  }, [reset]);

  useEffect(() => {
    if (planeModel.length !== 0 && loader !== null && scene !== null) {
      console.log(planeModel);
      loader.load(planeModel, (gltf: GLTF) => {
        // console.log(renderer);
        Object.defineProperty(gltf.scene, "isAdded", {
          value: true,
        });
        scene.add(gltf.scene);
        console.log(gltf.scene);
        console.log(scene);
      });
    }
  }, [planeModel, loader, scene]);

  return (
    <>
      {planeModel.length === 0 && <Modal setPlaneModel={setPlaneModel} />}
      <canvas ref={canvasRef}></canvas>
    </>
  );
}
