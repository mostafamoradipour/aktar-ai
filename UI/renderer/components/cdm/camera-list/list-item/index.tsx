import styles from "./styles.module.scss";
import axios from "axios";
import { useRecoilState } from "recoil";
import { camerasAtom } from "@/components/utilities/atoms";
import { CameraInterface } from "../../../camera/cameras";
import Checkbox from "@mui/material/Checkbox";
import { useState, useEffect } from "react";

export default function ListItem({ camera, index }) {
  const [CDM, setCDM] = useState(false);

  const [cameras, setCameras] = useRecoilState<CameraInterface[] | null>(
    camerasAtom
  );

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCameras(
      cameras.map((el) => {
        let t = { ...el };
        if (t.name === camera.name) {
          t.cdm = event.target.checked;
        } else if (typeof t.cdm === "undefined") {
          t.cdm = false;
        }
        return t;
      })
    );
    setCDM(event.target.checked);
  };

  return (
    <>
      <div>camera-{index}</div>
      <div id="status">
        <Checkbox checked={CDM} onChange={handleChange} />
      </div>
      <div className={styles["camera-id"]}>
        {camera.name.substring(camera.name.indexOf("-") + 1)}
      </div>
    </>
  );
}
