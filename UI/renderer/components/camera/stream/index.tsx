import { useRef, useEffect, useState } from "react";
import axios from "axios";
import { useRecoilState } from "recoil";
import { showAddCameraAtom, camerasAtom } from "@/components/utilities/atoms";
import styles from "./styles.module.scss";

interface Props {
  port: number;
  id: string;
}
const StreamPlayer = ({ port, id }: Props) => {
  const [showAddCamera, setShowAddCamera] = useRecoilState(showAddCameraAtom);
  const [cameras, setCameras] = useRecoilState(camerasAtom);
  const [player, setPlayer] = useState(null);
  const [JSMpeg, setJSMpeg] = useState(require("./jsmpeg.min.js").JSMpeg);

  // const src = "rtsp://89.165.39.53:554/user=admin&password=109ms190&channel=01&stream=1.sdp";
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  // const [url, setUrl] = useState("");
  // const [activeUrl, setActiveUrl] = useState("");

  useEffect(() => {
    const reqHanlde = () => {
      // if (showAddCamera) return;
      // if (player?.destroy) player.destroy();
      // const res = await axios.post("http://localhost:3333/set_rtsp_url", {
      //   url: url,
      // });
      // console.log("set url:");
      // console.log(res);
      setPlayer(
        new JSMpeg.Player("ws://localhost:" + port, {
          canvas: streamRef.current,
        })
      );
      // console.log("player");
      // console.log(player);
    };
    reqHanlde();
  }, [port]);

  const removeStream = async (id: string) => {
    let res = await axios.post("http://localhost:3333/remove_stream", { id });
    if (player?.destroy) player.destroy();
    setCameras(res.data.cameras);
    console.log(res.data);
  };

  // const [player, setPlayer] = useState();

  // useEffect(() => {
  //     // make sure Video.js player is only initialized once
  //     if (!player) {
  //         const videoElement = videoRef.current;
  //         if (!videoElement) return;

  //         setPlayer(
  //             videojs(videoElement, {}, () => {
  //                 console.log("player is ready");
  //             })
  //         );
  //     }
  // }, [videoRef]);

  // useEffect(() => {
  //     return () => {
  //         if (player) {
  //             player.dispose();
  //         }
  //     };
  // }, [player]);

  return (
    <>
      <canvas ref={streamRef} id={styles["stream-canvas"]}></canvas>
      <span
        className={`${styles["remove-stream"]} material-icons`}
        onClick={(e) => removeStream(id)}
      >
        close
      </span>
      {/* <input value={url} onChange={(e) => setUrl(e.target.value)} /> */}
      {/* <button onClick={() => setActiveUrl(url)}>Set URL</button> */}
      {/* <Script src="./jsmpeg.min.js" id="jsmpeg"></Script> */}
      {/* <video className="video-js" ref={videoRef} controls> */}
      {/* <source src={src} type="application/x-mpegURL" /> */}
      {/* </video> */}
    </>
  );
};

export default StreamPlayer;
