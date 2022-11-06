import styles from "./styles.module.scss";
import { camerasAtom } from "@/components/utilities/atoms";
import { useRecoilState } from "recoil";
import { CameraInterface } from "../cameras";
import axios from "axios";

export default function PlayBtn() {
  const [cameras, setCameras] = useRecoilState<CameraInterface[] | null>(
    camerasAtom
  );

  return (
    <div>
      <button
        className={styles["button"]}
        onClick={async (e) => {
          const res = await axios.post("http://localhost:5000/play", {
            cameras,
          });
        }}
      >
        Play
      </button>
    </div>
  );
}
