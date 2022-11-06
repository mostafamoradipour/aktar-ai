import React from "react";
import Layout from "@/components/general/layout";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";
import { useRecoilState } from "recoil";
import Container from "@/components/search/container";

export default function Search() {

    const [servicesItems] = useRecoilState(servicesItemsAtom);

    const navBarOptions = [
        {
            name: "Our Services",
            icon: "donut_large",
            menuItems: servicesItems
        },
        {
            name: "Tools",
            icon: "settings",
            menuItems: [
              {
                href: "#",
                icon: "movie_filter",
                description: "Import Video",
                deactivated: true
                // comingSoon: true,
              },
              {
                href: "#",
                icon: "image_search",
                description: "Image Search",
                deactivated: true
              },
              {
                href: "#",
                icon: "attribution",
                description: "Human Search",
                deactivated: true
              },
              {
                href: "#",
                icon: "filter_tilt_shift",
                description: "Weapon Search",
                deactivated: true
              },
              {
                href: "#",
                icon: "water_drop",
                description: "Wet Surface Search",
                deactivated: true
              },
            //   {
            //     href: "#",
            //     icon: "",
            //     description: "",
            //     deactivated: true
            //   },
              {
                href: "#",
                icon: "tune",
                description: "Customized Search",
                deactivated: true
              },
            ],
          },
    ];

    return (
        <>
            <Layout footerAudio={true} navBarOptions={navBarOptions}>
                <Container />
            </Layout>
        </>
    );
}
