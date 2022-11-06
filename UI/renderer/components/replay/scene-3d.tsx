import { useEffect, useRef, useState } from "react";
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
import { showLoadingAtom, uuidAtom } from "../utilities/atoms";
import { useRecoilState } from "recoil";
import gsap from "gsap";
// import axios from "axios";
import { useCookies } from "react-cookie";
import styles from "./styles.module.scss";
import PauseRounded from "@mui/icons-material/PauseRounded";
import PlayArrowRounded from "@mui/icons-material/PlayArrowRounded";
import IconButton from "@mui/material/IconButton";
import { Group } from "three";

interface Pose {
  id: number;
  z: number;
  x: number;
}
let isPlaying = false;
export default function Scene3d({ type }) {
  const [playing, setPlaying] = useState(false);
  const [showWelcomeMessage, setShowWelcomeMessage] = useState(false);
  const [showLoading, setShowLoading] = useRecoilState(showLoadingAtom);

  const canvasRef = useRef();

  const counterModel = "/models/counter-high-res-final.glb";
  const humanModel = "/models/human.glb";
  const shelfModel = "/models/store-shelf.glb";
  const wsUrl = "ws://localhost:8765";
  const [socket, setSocket] = useState(new WebSocket(wsUrl));

  function fetchSpaceData() {
    // applyAllModels([
    //   {
    //     modelURL: data.files[0],
    //     count: 1,
    //     // TODO - make intensity change in additionalObjectActions
    //     envMapIntensity: 1,
    //     additionalObjectActions(obj) {},
    //   },
    // ]);
    // console.log(url);
    // const socket = new WebSocket(url);
    main.humans = [];

    window.addEventListener("unload", () => {
      socket.close();
    });
    // Connection opened
    socket.addEventListener("open", function (event) {
      socket.send("play");
      console.log("opened");
      // socket.send(JSON.stringify({ stat: "ok" }));
    });
    socket.onmessage = (event) => {
      let poses: Pose[] = JSON.parse(event.data);
      console.log(poses);

      const x = (i: number) => {
        if (poses.length !== 0) {
          // console.log("x", message[0].x0 / 100);
          return poses[i].x;
        }
      };
      const z = (i: number) => {
        if (poses.length !== 0) {
          // console.log("z", message[0].d0 / 100);
          return poses[i].z;
        }
      };
      if (main.humanModelObj && poses.length !== 0) {
        // for every item, pick the human with the same id, animate it with new pose, remove it if it doesn't exist
        poses.forEach((m, i) => {
          // console.log("humans", main.humans);
          let currHuman = main.humans.find(
            (h: { id: number; human: Group }) => h.id === m.id
          );
          if (currHuman) {
            let tl = gsap.timeline();
            tl.to(currHuman.human.position, {
              x: m.x,
              duration: 0.5,
              ease: "power1",
            }).to(
              currHuman.human.position,
              {
                z: m.z,
                duration: 0.5,
                ease: "power1",
              },
              "-=0.5"
            );
          } else {
            main.humans.push({
              id: m.id,
              human: main.humanModelObj.clone(),
            });
            main.humans[main.humans.length - 1].human.visible = true;
            // console.log("added clone");
            main.baseObjects.scene.add(
              main.humans[main.humans.length - 1].human
            );
            let tl = gsap.timeline();
            tl.to(main.humans[main.humans.length - 1].human.position, {
              x: x(i),
              duration: 0.5,
              ease: "power1",
            }).to(
              main.humans[main.humans.length - 1].human.position,
              {
                z: z(i),
                duration: 0.5,
                ease: "power1",
              },
              "-=0.5"
            );
          }
        });

        // let tl = gsap.timeline();
        // tl.to(main.humanModelObj.position, {
        //   x: x(0),
        //   duration: 0.5,
        //   ease: "power1",
        // }).to(
        //   main.humanModelObj.position,
        //   {
        //     z: z(0),
        //     duration: 0.5,
        //     ease: "power1",
        //   },
        //   "-=0.5"
        // );
        // .to(
        //   humanModelObj.rotation,
        //   {
        //     y: JSON.parse(event.data).message.angle,
        //   },
        //   "-=0.5"
        // );
        // let removedHuman =

        main.humans.forEach((h: { id: number; human: Group }, i: number) => {
          let rmv = poses.find((p) => p.id === h.id);
          if (typeof rmv === "undefined") {
            main.humans[i].human.visible = false;
          }
          // console.log("rmv:");
          // console.log(rmv);
          // h.id === m.id;
        });
      }
      isPlaying ? socket.send("play") : socket.send("pause");
    };
  }

  useEffect(() => {
    main.canvasRef = canvasRef;
    basicSetup({ controlLimits: false, controls: true });
    main.activeCamera.position.set(0, 10, 0);
    setShowLoading(true);

    main.progress.endCondition = () => {
      return main.progress.loadedAssets.length === 2;
    };
    main.progress.loadingState = { showLoading, setShowLoading };
    main.progress.updateLoadingState();

    main.progress.onEnd = () => {
      main.baseObjects.scene.traverse((child) => {
        if (child.name === "human") {
          // console.log("human");
          // console.log(child);
          main.humanModelObj = child;
          // console.log(main.humanModelObj);
        }
      });
    };

    applyAllModels([
      {
        modelURL: humanModel,
        count: 1,
        // TODO - make intensity change in additionalObjectActions
        envMapIntensity: 1,
        additionalObjectActions(obj: THREE.Object3D) {
          obj.scale.set(0.8, 1, 0.8);
          obj.position.set(1, 2, 2);
          obj.rotateY(Math.PI / 2);
          obj.name = "human";

          obj.traverse((child) => {
            //@ts-ignore
            if (child.isMesh) {
              child.castShadow = true;
            }
          });
          obj.visible = false;
        },
        additionalCloneActions(clone) {
          // clone.position.x = Math.random() * 40 - 20;
          // clone.position.z = Math.random() * 40 - 20;
          // clone.rotateY(Math.random() * Math.PI * 2);
          // const tl = gsap.timeline();
          // tl.to(clone.position, {
          //   delay: Math.random() * 2,
          //   duration: Math.random() * 10 + 10,
          //   repeat: Math.random() * 10 - 1,
          //   x: Math.random() * 40 - 20,
          //   yoyo: true,
          //   ease: "sine.inOut",
          //   onComplete: () => {
          //     clone.rotateY(Math.random() * Math.PI * 2);
          //   },
          // }).to(
          //   clone.position,
          //   {
          //     duration: Math.random() * 10 + 10,
          //     repeat: Math.random() * 10 - 1,
          //     z: Math.random() * 40 - 20,
          //     yoyo: true,
          //     ease: "sine.inOut",
          //   },
          //   "-=5"
          // );
        },
      },
      {
        modelURL: shelfModel,
        count: 5,
        envMapIntensity: 1,
        additionalObjectActions(obj) {
          obj.scale.set(10, 5, 5);
        },
      },
      {
        modelURL: counterModel,
        count: 3,
        envMapIntensity: 1,
        additionalObjectActions(obj) {
          obj.scale.set(0.6, 0.6, 0.6);
          obj.position.z = 35;
        },
      },
    ]);
    // addPlane({ width: 60, height: 15, position: { x: -2, z: -30, y: 7.5 } });
    // addPlane({
    //   width: 80,
    //   height: 15,
    //   position: { x: 28, y: 7.5, z: 10 },
    //   rotation: { y: 90 },
    // });
    // addPlane({
    //   width: 60,
    //   height: 80,
    //   direction: "horizontal",
    //   position: { x: -2, z: 10 },
    // });

    applyLights({ type: "custom" });
    applyEnvMap([
      "/texture/cubic/christmas-studio/px.png",
      "/texture/cubic/christmas-studio/nx.png",
      "/texture/cubic/christmas-studio/py.png",
      "/texture/cubic/christmas-studio/ny.png",
      "/texture/cubic/christmas-studio/pz.png",
      "/texture/cubic/christmas-studio/nz.png",
    ]);
    applyAnimations({ type: "custom" });
    applyDomInteractions();
    // debugTHREE();

    animate();

    fetchSpaceData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    isPlaying = playing;
    socket.readyState === 1
      ? isPlaying
        ? socket.send("play")
        : socket.send("pause")
      : null;
  }, [playing]);

  return (
    <>
      <canvas id="main-scene" ref={canvasRef}></canvas>
      <div className={styles["playback-box"]}>
        <div className="flex-center">
          <IconButton
            aria-label={playing ? "pause" : "play"}
            onClick={() => setPlaying(!playing)}
          >
            {!playing ? (
              <PlayArrowRounded sx={{ fontSize: "3rem" }} htmlColor={"#000"} />
            ) : (
              <PauseRounded sx={{ fontSize: "3rem" }} htmlColor={"#000"} />
            )}
          </IconButton>
        </div>
      </div>
    </>
  );
}
