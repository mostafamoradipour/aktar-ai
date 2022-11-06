import { useEffect, useRef, useState } from "react";
import storeSceneSetup from "../utilities/THREE-scene-setup-store";
import {
  main,
  basicSetup,
  applyEnvMap,
  applyAllModels,
  addPlane,
  applyLights,
  applyAnimations,
  applyDomInteractions,
  animate,
  debugTHREE,
} from "../utilities/THREE-scene-setup-custom";
import { showLoadingAtom, csrfTokenAtom } from "../utilities/atoms";
import { useRecoilState } from "recoil";
import gsap from "gsap";
import axios from "axios";
import styles from "./styles.module.scss";

export default function SmartStoreScene({ type }) {
  const [showLoading, setShowLoading] = useRecoilState(showLoadingAtom);

  const [humanCounter, setHumanCounter] = useState(0);

  const canvasRef = useRef();

  // smart store
  const shelfModel = "/models/store-shelf.glb";
  const counterModel = "/models/counter-high-res-final.glb";
  // const shelfModelV2 = "/models/shelf-v2.glb";
  // const counterModelV2 = "/models/counter-v2.glb";
  // const humanModel = "/models/rp_dennis_posed_004_30k.glb";
  const humanModel = "/models/human.glb";


  useEffect(() => {
    storeSceneSetup({
      canvasRef,
      models: [
        {
          modelURL: shelfModel,
          count: 5,
          additionalObjectActions(obj) {
            obj.scale.set(10, 5, 5);
          },
        },
        {
          modelURL: counterModel,
          count: 3,
          additionalObjectActions(obj) {
            obj.scale.set(0.6, 0.6, 0.6);
            obj.position.z = 35;
          },
        },
        {
          modelURL: humanModel,
          count: 1,
          additionalObjectActions(obj) {
            // obj.scale.set(2.2, 2.2, 2.2);
            obj.position.x = 15;
            obj.position.z = 50;
            obj.position.y = 2
            obj.name = "human";
            console.log(obj);
            obj.children.forEach((child) => {
              child.name = "human";
            })
          },
          additionalCloneActions(clone) {
            // clone.position.x = Math.random() * 40 - 20;
            // clone.position.z = Math.random() * 40 - 20;
            clone.rotateY(Math.PI / 2);
            const tl = gsap.timeline({
              repeat: -1,
              yoyo: true,
            });
            tl.to(clone.position, {
              keyframes: [
                {
                  onStart: () => {
                    clone.visible = true
                  },
                  delay: 0.5,
                  duration: 15,
                  // repeat: Math.random() * 10 - 1,
                  z: -20,
                  // yoyo: true,
                  ease: "sine.inOut",
                  // onComplete: () => {
                  //   clone.rotateY(Math.random() * Math.PI * 2);
                  // },

                },
                {
                  duration: 5,
                  x: 12,
                  // yoyo: true,
                  ease: "sine.inOut",
                  delay: -5,
                },

              ]
            })
              .to(
                clone.rotation,
                {
                  duration: 1,
                  y: -Math.PI / 2,
                  ease: "sine.inOut",
                },
                "-=1"
              )
              .to(
                clone.position,
                {
                  duration: 5,
                  x: 5,
                  ease: "sine.inOut",
                }
              )
              .to(
                clone.rotation,
                {
                  duration: 1,
                  y: (-Math.PI / 2) * 2,
                  ease: "sine.inOut",
                },
                "-=1"
              )
              .to(clone.position, {
                duration: 15,
                z: 50,
                ease: "sine.inOut",
                onComplete: () => {
                  clone.visible = false
                }
              }, "-=1")
          },
        },
        {
          modelURL: humanModel,
          count: 1,
          additionalObjectActions(obj) {
            // obj.scale.set(2.2, 2.2, 2.2);
            obj.position.x = 5;
            obj.position.z = 30;
            obj.position.y = 2
            obj.name = "human";
            obj.children.forEach((child) => {
              child.name = "human";
            })
          },
          additionalCloneActions(clone) {
            clone.rotateY(Math.PI / 2);
            const tl = gsap.timeline({ repeat: -1, yoyo: true });
            tl.to(clone.position, {
              keyframes: [
                {
                  onStart: () => {
                    clone.visible = true

                  },
                  delay: 2,
                  duration: 10,
                  z: -15,
                  ease: "sine.inOut",
                },
                {
                  duration: 5,
                  x: 2,
                  ease: "sine.inOut",
                  delay: -5,
                },
              ]
            })
              .to(
                clone.rotation,
                {
                  duration: 1,
                  y: -Math.PI,
                  ease: "sine.inOut",
                },
                "-=1"
              )
              .to(
                clone.position,
                {
                  duration: 5,
                  x: 5,
                  ease: "sine.inOut",
                }
              )
              .to(clone.position, {
                duration: 15,
                z: 50,
                ease: "sine.inOut",
                onComplete: () => {
                  clone.visible = false
                }
              }, "-=5")
          },
        },
        {
          modelURL: humanModel,
          count: 1,
          additionalObjectActions(obj) {
            // obj.scale.set(2.2, 2.2, 2.2);
            obj.position.x = -17;
            obj.position.z = -10;
            obj.position.y = 2
            obj.name = "human";
            obj.children.forEach((child) => {
              child.name = "human";
            })
          },
          additionalCloneActions(clone) {
            clone.rotateY(Math.PI);
            console.log(clone.rotation)
            const tl = gsap.timeline({ repeat: -1, yoyo: true });
            tl.to(
              clone.rotation,
              {
                onStart: () => {
                  clone.visible = true
                },
                delay: 5,
                duration: 1,
                y: 0,
                ease: "sine.inOut",
              },
              "-=1"
            )
              .to(clone.position, {
                duration: 15,
                z: 50,
                ease: "sine.inOut",
                onComplete: () => {
                  clone.visible = false
                }
              }, "-=5")
          },
        },
        {
          modelURL: humanModel,
          count: 1,
          additionalObjectActions(obj) {
            // obj.scale.set(2.2, 2.2, 2.2);
            obj.position.x = -12;
            obj.position.z = -8;
            obj.position.y = 2
            obj.name = "human";
            obj.children.forEach((child) => {
              child.name = "human";
            })
          },
          additionalCloneActions(clone) {
            const tl = gsap.timeline({ repeat: -1, yoyo: true });
            tl.to(clone.position, {
              keyframes: [
                {
                  onStart: () => {
                    clone.visible = true
                  },
                  delay: 2,
                  duration: 8,
                  z: -20,
                  ease: "sine.inOut",
                },
                {
                  duration: 5,
                  x: -8,
                  ease: "sine.inOut",
                  delay: -2,
                },
              ]
            })
              .to(
                clone.rotation,
                {
                  duration: 1,
                  y: 0,
                  ease: "sine.inOut",
                },
                "-=1"
              )
              .to(clone.position, {
                duration: 15,
                x: -3,
                ease: "sine.inOut",
              }, "-=1")

              .to(clone.position, {
                duration: 15,
                z: 50,
                ease: "sine.inOut",
                onComplete: () => {
                  clone.visible = false
                }

              }, "-=15")
          },
        }
      ],
      envMapPath: [
        "/texture/cubic/px.png",
        "/texture/cubic/nx.png",
        "/texture/cubic/py.png",
        "/texture/cubic/ny.png",
        "/texture/cubic/pz.png",
        "/texture/cubic/nz.png",
      ],
      showLoading,
      setShowLoading,
      humanCounter: true
    });

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <canvas id="main-scene" ref={canvasRef}></canvas>
      {/* <div className={styles["counter"]}>
        {humanCounter}
      </div> */}
    </>
  );
}
