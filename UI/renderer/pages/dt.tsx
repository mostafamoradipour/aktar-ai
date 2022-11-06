import SmartStoreScene from "@/components/smart-store-scene/smart-store-scene";
import DigitalTwin from "@/components/digital-twin";
import Layout from "@/components/general/layout";
import { useRecoilState } from "recoil";
import { sceneUtilsAtom, userLogInAtom } from "@/components/utilities/atoms";
import { useCookies } from "react-cookie";
import Router from "next/router";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";
import { useRef, useState } from "react";
export default function DT() {
  const [sceneUtils] = useRecoilState<any>(sceneUtilsAtom);
  const [planeModel, setPlaneModel] = useState<string>("");
  const [reset, setReset] = useState(false);

  // TODO - more damping for the controls

  const [servicesItems] = useRecoilState(servicesItemsAtom);

  const navBarOptions = [
    {
      name: "Our Services",
      icon: "donut_large",
      menuItems: servicesItems,
    },
    {
      name: "Tools",
      icon: "settings",
      menuItems: [
        {
          href: "#",
          icon: "navigation",
          description: "Top View",
          type: "scene-option",
          action: "topView",
          onClick: sceneUtils.topView,
        },
        {
          href: "#",
          icon: "filter_alt",
          description: "Display Human",
          type: "scene-option",
          action: "filteredView",
          onClick: sceneUtils.filteredView,
        },
        {
          href: "/services/data-analytics",
          icon: "stacked_bar_chart",
          description: "Data Analysis",
        },
        {
          href: "#",
          icon: "file_upload",
          description: "Upload Plane Model",
          type: "scene-option",
          action: "upload",
          onClick: () => {
            setPlaneModel("");
          },
        },
        {
          href: "#",
          icon: "restart_alt",
          description: "Reset Scene",
          type: "scene-option",
          action: "reset",
          onClick: () => {
            // setPlaneModel("");
            setReset(!reset);
          },
        },
      ],
    },
  ];

  return (
    <>
      <Layout navBarOptions={navBarOptions}>
        <DigitalTwin
          planeModel={planeModel}
          setPlaneModel={setPlaneModel}
          reset={reset}
        />
      </Layout>
    </>
  );
}
