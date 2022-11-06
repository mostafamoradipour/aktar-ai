
import Layout from "@/components/general/layout";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";
import { useRecoilState } from "recoil";
import Content from '@/components/download-app/content';

export default function DownloadApp() {
  const [servicesItems] = useRecoilState(servicesItemsAtom);

  const navBarOptions = [
    {
      name: "Our Services",
      icon: "donut_large",
      menuItems: servicesItems
    },
  ];

  return (
    <>
      <Layout footerAudio={false} navBarOptions={navBarOptions}>
        <Content />
      </Layout>
    </>
  );
}


