import React from "react";
import ContactTable from "@/components/contact-table/contact-table";
import Layout from "@/components/general/layout";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";
import { useRecoilState } from "recoil";

export default function ContactHuman() {

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
        <ContactTable />
      </Layout>
    </>
  );
}
