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
import axios from "axios";
import { useCookies } from "react-cookie";
import styles from './styles.module.scss'

export default function Scene3d({ type }) {
  const [showWelcomeMessage, setShowWelcomeMessage] = useState(false)
  const [cookies, setCookie] = useCookies(["loggedIn"]);
  const [showLoading, setShowLoading] = useRecoilState(showLoadingAtom);
  const [uuid, setUuid] = useRecoilState(uuidAtom);

  const canvasRef = useRef();

  const humanModel = "/models/rp_dennis_posed_004_30k.glb";

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
        modelURL: humanModel,
        count: 1,
        // TODO - make intensity change in additionalObjectActions
        envMapIntensity: 1,
        additionalObjectActions(obj) {
          obj.scale.set(0.8, 1, 0.8);
          obj.position.x = 1;
          obj.position.z = 2;
          obj.name = "human";

          obj.traverse((child) => {
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
    ]);


    applyLights({ type: "custom" });
    applyAnimations({ type: "custom" });
    applyDomInteractions();
    // debugTHREE();

    animate();

    axios
      .get("https://api.kachrobotics.com/api/user/set_csrf_cookie/", {
        withCredentials: true,
      })
      .then((res) => {
        // console.log("csrf : ", res.data["csrfmiddlewaretoken"]);
        let bodyFormData = new FormData();
        bodyFormData.append(
          "csrfmiddlewaretoken",
          res.data["csrfmiddlewaretoken"]
        );
        return bodyFormData;
      })
      .then((bodyFormData) => {
        axios({
          method: "get",
          url: "https://api.kachrobotics.com/api/user/get_vspace_data/",
          data: bodyFormData,
          headers: { "Content-Type": "multipart/form-data" },
          withCredentials: true,
        })
          .then((response) => {

            setUuid(response.data.uuid);

            // console.log(response.data.vector_space_data);
            if (response.data.vector_space_data.length === 0) setShowWelcomeMessage(true)
            response.data.vector_space_data.forEach((element) => {
              addPlane(element)
            })

            if (response.status === 200) {
              const url =
                "wss://api.kachrobotics.com/ws/user/?uuid=" + response.data["uuid"];
              // console.log(url);
              const socket = new WebSocket(url);

              window.addEventListener('unload', () => {
                socket.close()
              })

              // Connection opened
              socket.addEventListener("open", function (event) {
                // console.log("opened");
                // socket.send(JSON.stringify({ stat: "ok" }));
              });
              main.humans = [];
              socket.addEventListener("message", function (event) {
                let message = JSON.parse(event.data).message;

                if (message.sender === "gpu") {
                  // console.log("message", message);
                  let poses = message.poses;
                  const x = (i) => {
                    if (poses.length !== 0) {
                      // console.log("x", message[0].x0 / 100);
                      return poses[i].x / 100;
                    }
                  };
                  const z = (i) => {
                    if (poses.length !== 0) {
                      // console.log("z", message[0].d0 / 100);
                      return poses[i].z / 100;
                    }
                  };

                  if (main.humanModelObj && poses.length !== 0) {
                    // see the items in poses
                    poses.forEach((m, i) => {
                      // console.log("m", m);

                      let has = false;
                      //  if the item exists in the scene, then update the position
                      for (let index = 0; index < main.humans.length; index++) {
                        let humans = main.humans;
                        if (m.id === humans[index].id) {
                          let tl = gsap.timeline();
                          tl.to(humans[index].human.position, {
                            x: x(index),
                            duration: 0.5,
                            ease: "power1",
                          }).to(
                            humans[index].human.position,
                            {
                              z: z(index),
                              duration: 0.5,
                              ease: "power1",
                            },
                            "-=0.5"
                          );
                          has = true;
                        }
                      }
                      //  if the item does not exist in the scene, then add it
                      if (has === false) {
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
                        tl.to(
                          main.humans[main.humans.length - 1].human.position,
                          {
                            x: x(i),
                            duration: 0.5,
                            ease: "power1",
                          }
                        ).to(
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
                  }
                }
              });
            }
          })
          .catch((error) => {
            if (error.response.status === 401) {
              setCookie("loggedIn", false);
              console.log("deleting cookies and retry");
            }
          });
      });

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <canvas id="main-scene" ref={canvasRef}></canvas>
      {showWelcomeMessage ? (
        <div className={styles["welcome-message-container"]}>
          <div className={styles["welcome-message"]}>
            We help you to empower your business with AI and Cloud Computing
          </div>
        </div>
      ) : (<></>)}
    </>
  );
}
