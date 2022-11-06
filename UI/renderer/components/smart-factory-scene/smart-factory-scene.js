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
import { showLoadingAtom, csrfTokenAtom } from "../utilities/atoms";
import { useRecoilState } from "recoil";
import gsap from "gsap";
import axios from "axios";

export default function SmartFactoryScenes() {
  const [showLoading, setShowLoading] = useRecoilState(showLoadingAtom);

  const canvasRef = useRef();

  // smart store
  const forgingLineModel = "/models/forging-line.glb";

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
      // console.log('end');
    };

    applyEnvMap([
      "/texture/cubic/christmas-studio/px.png",
      "/texture/cubic/christmas-studio/nx.png",
      "/texture/cubic/christmas-studio/py.png",
      "/texture/cubic/christmas-studio/ny.png",
      "/texture/cubic/christmas-studio/pz.png",
      "/texture/cubic/christmas-studio/nz.png",
    ]);
    applyAllModels([
      {
        modelURL: forgingLineModel,
        count: 1,
        // TODO - make intensity change in additionalObjectActions
        envMapIntensity: 1,
        additionalObjectActions(obj) {
          // obj.scale.set(0.8, 1, 0.8);
          // obj.position.x = 1;
          // obj.position.z = 2;
          // obj.name = "human";
          // obj.traverse((child) => {
          //   if (child.isMesh) {
          //     child.castShadow = true;
          //   }
          // });
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
    ]);
    // addPlane({
    //   width: 3,
    //   height: 4.6,
    //   direction: "horizontal",
    //   position: { x: 1.5, y: 0, z: 4.6 / 2 },
    // });
    // addPlane({
    //   width: 4.6,
    //   height: 3,
    //   direction: "vertical",
    //   rotation: { y: 90 },
    //   position: {
    //     y: 3 / 2,
    //     z: 4.6 / 2,
    //   },
    // });
    // addPlane({
    //   width: 3,
    //   height: 3,
    //   direction: "vertical",
    //   position: {
    //     x: 1.5,
    //     y: 3 / 2,
    //     z: 4.6,
    //   },
    // });
    // addPlane({
    //   width: 1.5,
    //   height: 1.5,
    //   direction: "horizontal",
    //   position: {
    //     x: 3 + 1.5 / 2,
    //     z: 4.6 - 1.5 / 2,
    //   },
    // });

    applyLights({ type: "custom" });
    applyAnimations({ type: "factory" });
    applyDomInteractions();
    // debugTHREE();

    animate();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // useEffect(() => {
  //   axios
  //     .get("https://api.kachrobotics.com/api/user/set_csrf_cookie/", {
  //       withCredentials: true,
  //     })
  //     .then((res) => {
  //       // console.log("csrf : ", res.data["csrfmiddlewaretoken"]);
  //       let bodyFormData = new FormData();
  //       bodyFormData.append(
  //         "csrfmiddlewaretoken",
  //         res.data["csrfmiddlewaretoken"]
  //       );
  //       axios({
  //         method: "post",
  //         url: "https://api.kachrobotics.com/api/user/get_uuid/",
  //         data: bodyFormData,
  //         headers: { "Content-Type": "multipart/form-data" },
  //         withCredentials: true,
  //       }).then((response) => {
  //         // console.log(response.data);
  //         if (response.status === 200) {
  //           const url =
  //             "wss://api.kachrobotics.com/ws/user/?uuid=" + response.data["uuid"];
  //           // console.log(url);
  //           const socket = new WebSocket(url);
  //           // Connection opened
  //           socket.addEventListener("open", function (event) {
  //             console.log("opened");
  //             // socket.send(JSON.stringify({ stat: "ok" }));
  //           });
  //           // Connection opened
  //           socket.addEventListener("message", function (event) {
  //             let message = JSON.parse(event.data).message;
  //             // console.log(message.length !== 0);
  //             console.log(message);

  //             const x = () => {
  //               if (message.length !== 0) {
  //                 console.log("x", message[0].x0 / 100);
  //                 return message[0].x0 / 100;
  //               }
  //             };
  //             const z = () => {
  //               if (message.length !== 0) {
  //                 console.log("z", message[0].d0 / 100);
  //                 return message[0].d0 / 100;
  //               }
  //             };
  //             if (main.humanModelObj && message.length !== 0) {
  //               let tl = gsap.timeline();
  //               tl.to(main.humanModelObj.position, {
  //                 x: x(),
  //                 duration: 0.5,
  //                 ease: "power1",
  //               }).to(
  //                 main.humanModelObj.position,
  //                 {
  //                   z: z(),
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
  //           });
  //         }
  //       });
  //     });
  // }, []);

  return (
    <>
      <canvas id="main-scene" ref={canvasRef}>
        {" "}
      </canvas>
    </>
  );
}
