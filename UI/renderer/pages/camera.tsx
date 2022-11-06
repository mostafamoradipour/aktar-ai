import CameraGrid from "@/components/camera/camera-grid";
import axios from "axios";
import { useCookies } from "react-cookie";
import Router from "next/router";
import { useState, useEffect } from "react";
import Loading from "@/components/general/loading";
import { useRouter } from "next/router";
import AddCameraBtn from "@/components/camera/add-camera/btn/index";
import PageLayout from "@/components/camera/layout/index";
import { useRecoilState } from "recoil";
import { showAddCameraAtom, camerasAtom } from "@/components/utilities/atoms";
import CameraList from "@/components/camera/camera-list";
import { CameraInterface } from "@/components/camera/cameras";
import PlayBtn from "@/components/camera/play-btn";

export default function Camera() {
  // show cameras list
  // send new camera on add
  // remove Camera on Remove
  // play on play
  const [showAddCamera, setShowAddCamera] = useRecoilState(showAddCameraAtom);

  const [cameras, setCameras] = useRecoilState<CameraInterface[] | null>(
    camerasAtom
  );

  async function getCameras() {
    if (showAddCamera) return;
    try {
      const res = await axios.get("http://localhost:5000/get");
      setCameras(res.data.cameras);
    } catch (e) {
      console.log("error fetching cameras");
    }
    // [
    //     {
    //         name: 'test',
    //         url: "rtsp://2.191.97.245:554/user=admin&password=&channel=2&stream=0.sdp?real_stream--rtp-caching=800"
    //     }
    // ]
  }
  useEffect(() => {
    getCameras();
  }, []);

  if (cameras?.length === 0) {
    return (
      <PageLayout>
        <div className="content flex-col">
          <h1 className="mb-40">No cameras found</h1>
          <AddCameraBtn></AddCameraBtn>
        </div>
      </PageLayout>
    );
  } else {
    return (
      <PageLayout>
        {cameras === null ? (
          <div className="content">
            <Loading size="medium" />
          </div>
        ) : (
          <div className="align-center">
            <CameraList></CameraList>
            <PlayBtn></PlayBtn>
          </div>
          // <CameraGrid cameras={cameras}></CameraGrid>
        )}
      </PageLayout>
    );
  }
}
