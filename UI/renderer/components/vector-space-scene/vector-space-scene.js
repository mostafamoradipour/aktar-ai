import { useEffect, useRef, useState } from "react";
import * as THREE from 'three'
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
  addGrid,
  addAxisHelper
} from "./vector-space-engine";
import { showLoadingAtom, csrfTokenAtom } from "../utilities/atoms";
import { useRecoilState } from "recoil";
import gsap from "gsap";
import axios from "axios";

export default function VectorSpaceScene() {
  const [showLoading, setShowLoading] = useRecoilState(showLoadingAtom);

  const canvasRef = useRef();

  const humanModel = "/models/rp_dennis_posed_004_30k.glb";
  const shelfModel = "/models/store-shelf.glb";


  useEffect(() => {
    main.canvasRef = canvasRef;
    basicSetup({ controlLimits: false });
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
        additionalObjectActions(obj) {
          var box = new THREE.Box3().setFromObject(obj);
          obj.scale.z = 1.37 / (box.max.z - box.min.z)
          obj.scale.y = 5.90 / (box.max.y - box.min.y)
          obj.scale.x = 1.2 / (box.max.x - box.min.x)
          // console.log(5.90 / (box.max.y - box.min.y));
          obj.position.x = 2;
          obj.position.z = 2;
          obj.name = "human";

          obj.traverse((child) => {
            if (child.isMesh) {
              child.castShadow = true;
            }
          });

          // Scenario

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
        count: 1,
        additionalObjectActions(obj) {
          obj.position.set(100,0,20) 
          obj.scale.set(10, 5, 5);
        },
      },
    ]);
    addPlane({
      width: 500,
      height: 600,
      direction: "horizontal",
      position: { x: 250, y: -0.05, z: 300 },
    });
    addPlane({
      width: 600,
      height: 16.4042,
      direction: "vertical",
      rotation: { y: 90 },
      position: {
        x: -0.05,
        y: 16.4042 / 2,
        z: 300,
      },
    });
    addPlane({
      width: 500,
      height: 16.4042,
      direction: "vertical",
      position: {
        x: 250,
        y: 16.4042 / 2,
        z: 600,
      },
    });
    applyEnvMap([
      "/texture/cubic/christmas-studio/px.png",
      "/texture/cubic/christmas-studio/nx.png",
      "/texture/cubic/christmas-studio/py.png",
      "/texture/cubic/christmas-studio/ny.png",
      "/texture/cubic/christmas-studio/pz.png",
      "/texture/cubic/christmas-studio/nz.png",
    ]);
    applyLights({ type: "vector-space" });
    applyAnimations({ type: "custom" });
    applyDomInteractions();
    // addGrid(500, 600)
    // addAxisHelper(1000)
    console.log(main)
    // debugTHREE()
    main.baseObjects.camera.position.set(490, 150, -10)
    main.baseObjects.controls.target.x = 200
    main.baseObjects.controls.target.z = 300
    main.baseObjects.controls.target.y = 5

    animate();

    // axios
    //   .get("https://api.kachrobotics.com/api/user/set_csrf_cookie/", {
    //     withCredentials: true,
    //   })
    //   .then((res) => {
    //     // console.log("csrf : ", res.data["csrfmiddlewaretoken"]);
    //     let bodyFormData = new FormData();
    //     bodyFormData.append(
    //       "csrfmiddlewaretoken",
    //       res.data["csrfmiddlewaretoken"]
    //     );
    //     axios({
    //       method: "post",
    //       url: "https://api.kachrobotics.com/api/user/get_uuid/",
    //       data: bodyFormData,
    //       headers: { "Content-Type": "multipart/form-data" },
    //       withCredentials: true,
    //     }).then((response) => {
    //       // console.log(response.data);
    //       if (response.status === 200) {
    //         const url =
    //           "wss://api.kachrobotics.com/ws/user/?uuid=" +
    //           response.data["uuid"];
    //         // console.log(url);
    //         const socket = new WebSocket(url);
    //         // Connection opened
    //         socket.addEventListener("open", function (event) {
    //           console.log("opened");
    //           // socket.send(JSON.stringify({ stat: "ok" }));
    //         });

    //         main.humans = [];
    //         socket.addEventListener("message", function (event) {
    //           let message = JSON.parse(event.data).message;

    //           if (message.sender === "gpu") {
    //             console.log("message", message);
    //             let poses = message.poses;
    //             const x = (i) => {
    //               if (poses.length !== 0) {
    //                 // console.log("x", message[0].x0 / 100);
    //                 return poses[i].x0 / 100;
    //               }
    //             };
    //             const z = (i) => {
    //               if (poses.length !== 0) {
    //                 // console.log("z", message[0].d0 / 100);
    //                 return poses[i].d0 / 100;
    //               }
    //             };
    //             if (main.humanModelObj && poses.length !== 0) {
    //               // see the items in poses
    //               // poses.forEach((m, i) => {
    //               //   console.log("m", m);
    //               //   let has = false;
    //               //   //  if the item exists in the scene, then update the position
    //               //   for (let index = 0; index < main.humans.length; index++) {
    //               //     //  if m.id in main.humans => main.humans[m.id].position.set(x(i), 0, z(i));
    //               //     if(m.id === main.humans[index].id){
    //               //       main.humans[index].human.position.set(x(i), 0, z(i));
    //               //       has = true;
    //               //     }
    //               //   }
    //               //   //  if the item does not exist in the scene, then add it
    //               //   if(has === false){
    //               //     main.humans.push({
    //               //       id: m.id,
    //               //       human: main.humanModelObj.clone(),
    //               //     });
    //               //     main.scene.add(main.humans[main.humans.length - 1].human);
    //               //     main.humans[main.humans.length - 1].human.position.set(x(i), 0, z(i));
    //               //   }
    //               //   //  else => main.humans.push(a clone)
    //               // });

    //               let tl = gsap.timeline();
    //               tl.to(main.humanModelObj.position, {
    //                 x: x(0),
    //                 duration: 0.5,
    //                 ease: "power1",
    //               }).to(
    //                 main.humanModelObj.position,
    //                 {
    //                   z: z(0),
    //                   duration: 0.5,
    //                   ease: "power1",
    //                 },
    //                 "-=0.5"
    //               );
    //               // .to(
    //               //   humanModelObj.rotation,
    //               //   {
    //               //     y: JSON.parse(event.data).message.angle,
    //               //   },
    //               //   "-=0.5"
    //               // );
    //             }
    //           }
    //         });
    //       }
    //     });
    //   });

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <canvas id="main-scene" ref={canvasRef}>
        {" "}
      </canvas>
    </>
  );
}
