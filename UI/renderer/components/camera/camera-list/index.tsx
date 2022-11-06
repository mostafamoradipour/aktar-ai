import styles from "./styles.module.scss";
import Content from "@/components/camera/content";
import StreamPlayer from "@/components/camera/stream/index";
import { CameraInterface } from "../cameras";
import RemoveIcon from "@mui/icons-material/Remove";
import IconButton from "@mui/material/IconButton";
import { SetterOrUpdater } from "recoil";
import { useRecoilState } from "recoil";
import { camerasAtom } from "@/components/utilities/atoms";
import ListItem from "./list-item";

export default function CameraList() {
  const [cameras, setCameras] = useRecoilState<CameraInterface[] | null>(
    camerasAtom
  );

  return (
    <div className={styles["camera-list-container"]}>
      <h2>Camera List</h2>
      <div className={styles["headers"]}>
        <div>name</div>
        <div>status</div>
        <div>ID</div>
      </div>
      {cameras.map((camera, index: number) => {
        return (
          <div key={camera.name} className={styles["list_item"]}>
            <ListItem camera={camera} index={index} />
          </div>
        );
      })}
    </div>
  );
}
