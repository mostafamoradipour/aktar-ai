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
                <div className="home-title-container">
                    <h1 className="home-title">LeaMech&apos;s mission<br />is to generate the digital twin of physical spaces<br />with respect to humanity and nature.</h1>
                    {/* <button className="learn-more">
            <Link href="/services/vector-space">
              <a>Learn More</a>
            </Link>
          </button> */}
                </div>
                <ContactTable />
            </Layout>
        </>
    );
}
