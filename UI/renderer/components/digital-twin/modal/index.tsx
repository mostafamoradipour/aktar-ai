import styles from "./styles.module.scss";
import { useRecoilState } from "recoil";
import {
  useState,
  useEffect,
  useRef,
  FormEvent,
  Dispatch,
  SetStateAction,
} from "react";
import { showAddCameraAtom, camerasAtom } from "@/components/utilities/atoms";
import axios from "axios";
import CameraList from "@/components/cdm/camera-list";
import { CameraInterface } from "@/components/camera/cameras";
import { ipcRenderer } from "electron";
import path from "path";

interface Props {
  setPlaneModel: Dispatch<SetStateAction<string>>;
}
export default function Modal({ setPlaneModel }: Props) {
  const modelInputRef = useRef(null);
  const [modelPath, setModelPath] = useState("");
  const [modelURL, setModelURL] = useState("");

  useEffect(() => {
    ipcRenderer.on("file", (event, file) => {
      // console.log("obtained file from main process: " + file);
      const fileURL = URL.createObjectURL(new Blob([file]));
      // if (typeof file === "string") {
      //   console.log(path.relative(__dirname, file));
      setPlaneModel(fileURL);
      // }
    });
  }, []);

  return (
    <div className={styles["overlay"]}>
      <div className={styles["content"]}>
        {/* <input
          type="file"
          className="d-none"
          id="model-input"
          ref={modelInputRef}
          onChange={function (e) {
            setModelPath(modelInputRef.current.files[0].path);
            setPlaneModel(URL.createObjectURL(modelInputRef.current.files[0]));
          }}
          accept=".glb,.gltf"
        /> */}
        {modelURL.length === 0 ? (
          <label
            htmlFor="model-input"
            onClick={(e) => {
              ipcRenderer.send("file-request");
            }}
          >
            <div className={styles["title"]}>
              Upload your Digital Twin to start an awesome journey!
            </div>

            <div className={styles["model-upload"]}>
              <span className={`material-icons ${styles["material-icons"]}`}>
                file_upload
              </span>
            </div>
          </label>
        ) : (
          <></>
        )}
      </div>
    </div>
  );
}
