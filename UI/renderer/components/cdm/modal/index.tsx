import styles from "./styles.module.scss";
import { useRecoilState } from "recoil";
import { useState, useEffect, useRef, FormEvent } from "react";
import { showAddCameraAtom, camerasAtom } from "@/components/utilities/atoms";
import axios from "axios";
import CameraList from "@/components/cdm/camera-list";
import { CameraInterface } from "@/components/camera/cameras";

export default function Modal({ selectedCams, setSelectedCams }) {
  const [cameras, setCameras] = useRecoilState<CameraInterface[] | null>(
    camerasAtom
  );

  const [loading, setLoading] = useState(false);

  async function getCameras() {
    try {
      const res = await axios.get("http://localhost:5000/get");
      setCameras(res.data.cameras);
      // setCameras([
      //   { name: "camera-01", url: "rtsp://ksdjhfjds", play: true, cdm: false },
      // ]);
    } catch (e) {
      console.log("error fetching cameras");
    }
  }
  useEffect(() => {
    getCameras();
  }, []);

  return (
    <div className={styles["overlay"]}>
      <div className={styles["content"]}>
        {cameras === null ? (
          <>Loading cameras</>
        ) : cameras.length === 0 ? (
          <>Please go to [Services &gt; Camera] and add your cameras</>
        ) : (
          <>
            {/* Camera List */}
            <CameraList />
            {/* Play btn */}
            <div>
              <button
                className={styles["button"]}
                onClick={(e) => {
                  const t = cameras.filter((el) => el.cdm === true);
                  if (t.length !== 0) setSelectedCams(t);
                }}
              >
                Play
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
