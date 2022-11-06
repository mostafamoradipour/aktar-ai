import Layout from "@/components/general/layout";
import AddCameraModal from "@/components/camera/add-camera/modal";
import { useRecoilState } from "recoil";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";
import { showAddCameraAtom } from "@/components/utilities/atoms";
import { Option as NavBarOption } from "@/components/nav-bar/nav-bar";

export default function PageLayout({ children }) {
  const [servicesItems] = useRecoilState(servicesItemsAtom);
  const [showAddCamera, setShowAddCamera] = useRecoilState(showAddCameraAtom);

  const navBarOptions: NavBarOption[] = [
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
          icon: "add",
          description: "Add Camera",
          onClick: (e) => setShowAddCamera(true),
        },
      ],
    },
  ];

  return (
    <Layout navBarOptions={navBarOptions} elevatedNavBar>
      {showAddCamera ? <AddCameraModal></AddCameraModal> : null}
      {children}
    </Layout>
  );
}
