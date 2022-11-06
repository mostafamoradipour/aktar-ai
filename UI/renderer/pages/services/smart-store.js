import SmartStoreScene from "@/components/smart-store-scene/smart-store-scene";
import Layout from "@/components/general/layout";
import { useRecoilState } from "recoil";
import {
  sceneUtilsAtom,
  userLogInAtom,
} from "@/components/utilities/atoms";
import { useCookies } from "react-cookie";
import Router from "next/router";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";

export default function SmartStore() {
  const [sceneUtils] = useRecoilState(sceneUtilsAtom);
  const [userIsAuthenticated, setUserIsAuthenticated] =
    useRecoilState(userLogInAtom);
  const [cookies, setCookie] = useCookies(["loggedIn"]);
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
      ],
    },
  ]
  return (
    <>
      <Layout type="3d-scene" navBarOptions={navBarOptions}>
        <SmartStoreScene />
      </Layout>
    </>
  );
}
