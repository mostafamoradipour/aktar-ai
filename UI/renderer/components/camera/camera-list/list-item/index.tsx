import styles from "./styles.module.scss";
import axios from "axios";
import { useRecoilState } from "recoil";
import { camerasAtom } from "@/components/utilities/atoms";
import { CameraInterface } from "../../cameras";
import Checkbox from "@mui/material/Checkbox";
import { useState, useEffect } from "react";

export default function ListItem({ camera, index }) {
  const [play, setPlay] = useState(camera.play);

  const [cameras, setCameras] = useRecoilState<CameraInterface[] | null>(
    camerasAtom
  );
  const removeCamera = async (name: string) => {
    let res = await axios.post("http://localhost:5000/remove", { name });
    setCameras(cameras.filter((el) => el.name !== name));
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCameras(
      cameras.map((el) => {
        let t = { ...el };
        if (t.name === camera.name) {
          t.play = event.target.checked;
        }
        return t;
      })
    );
    setPlay(event.target.checked);
  };

  return (
    <>
      <div className={styles["remove-row"]}>
        <button onClick={() => removeCamera(camera.name)}>remove</button>
      </div>

      <div>camera-{index}</div>
      <div id="status">
        <Checkbox checked={play} onChange={handleChange} />
      </div>
      <div className={styles["camera-id"]}>
        {camera.name.substring(camera.name.indexOf("-") + 1)}
      </div>
    </>
  );
}
