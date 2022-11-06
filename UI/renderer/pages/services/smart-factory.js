import Layout from "@/components/general/layout";
import { useRecoilState } from "recoil";
import { sceneUtilsAtom } from "@/components/utilities/atoms";
import SmartFactoryScene from "@/components/smart-factory-scene/smart-factory-scene";

export default function SmartStore() {
  const [sceneUtils, setSceneUtils] = useRecoilState(sceneUtilsAtom);
  return (
    <>
      <Layout
        type="3d-scene"
        navBarOptions={[
          {
            name: "Options",
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
                description: "Filtered View",
                type: "scene-option",
                action: "filteredView",
                onClick: sceneUtils.filteredView,
              },
            ],
          },
        ]}
      >
        <SmartFactoryScene />
      </Layout>
    </>
  );
}
