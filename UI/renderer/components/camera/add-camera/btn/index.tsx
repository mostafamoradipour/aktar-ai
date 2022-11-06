import styles from "./styles.module.scss";
import { showAddCameraAtom } from "@/components/utilities/atoms";
import { useRecoilState } from "recoil";

export default function AddCameraBtn() {
  const [showAddCamera, setShowAddCamera] = useRecoilState(showAddCameraAtom);

  return (
    <div>
      <button
        className={styles["button"]}
        onClick={(e) => {
          setShowAddCamera(true);
        }}
      >
        Add Camera
      </button>
    </div>
  );
}
