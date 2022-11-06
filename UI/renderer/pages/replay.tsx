import { useState, useEffect } from "react";
import Head from "next/head";
import Layout from "@/components/general/layout";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";
import { useRecoilState } from "recoil";
import { sceneUtilsAtom } from "@/components/utilities/atoms";
import Scene3d from "@/components/replay/scene-3d";
import axios from "axios";
import NonSSRWrapper from "@/components/general/no-ssr-wrapper";

export default function Replay() {
  const [sceneUtils, setSceneUtils] = useRecoilState(sceneUtilsAtom);

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
          onClick: sceneUtils["topView"],
        },
        {
          href: "#",
          icon: "filter_alt",
          description: "Display Human",
          type: "scene-option",
          action: "filteredView",
          onClick: sceneUtils["filteredView"],
        },
      ],
    },
  ];

  return (
    <>
      <Layout type="3d-scene" navBarOptions={navBarOptions}>
        <NonSSRWrapper>
          <Scene3d type="custom" />
        </NonSSRWrapper>
      </Layout>
    </>
  );
}
