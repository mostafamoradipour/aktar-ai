import Head from "next/head";
import Layout from "@/components/general/layout";
import { useRecoilState } from "recoil";
import {
  sceneUtilsAtom,
  userLogInAtom,
} from "@/components/utilities/atoms";
import VectorSpaceScene from "@/components/vector-space-scene/vector-space-scene";
import axios from "axios";
import { useCookies } from "react-cookie";
import Router from "next/router";

export default function VectorSpace() {
  const [sceneUtils, setSceneUtils] = useRecoilState(sceneUtilsAtom);

  return (
    <>
      <Layout
        type="3d-scene"
        navBarOptions={[
          {
            name: "Our Services",
            icon: "donut_large",
            menuItems: [
              {
                href: "/services/vector-space",
                icon: "workspaces",
                description: "Vector Space",
              },
              {
                href: "/data-analytics",
                icon: "stacked_bar_chart",
                description: "Data Analytics",
              },
              {
                href: "",
                icon: "widgets",
                description: "Download App",
              },
              {
                href: "/contact-human",
                icon: "support_agent",
                description: "Contact Human",
              },
            ],
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
                href: "/data-analytics",
                icon: "stacked_bar_chart",
                description: "Data Analysis",
              },
            ],
          },
        ]}
      >
        <VectorSpaceScene />
      </Layout>
    </>
  );
}
