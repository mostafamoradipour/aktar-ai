import { atom } from "recoil";

export const servicesItemsAtom = atom({

    key: 'services-items',
    default: [
        // {
        //     href: "/services/smart-store",
        //     icon: "workspaces",
        //     description: "Vector Space",
        // },
        // {
        //     href: "/services/data-analytics",
        //     icon: "stacked_bar_chart",
        //     description: "Data Analytics",
        // },
        // {
        //     href: "download-app",
        //     icon: "widgets",
        //     description: "Download App",
        // },
        {
            href: "/cdm",
            icon: "widgets",
            description: "CDM",
        },
        // {
        //     href: "/services/search",
        //     icon: "search",
        //     description: "Search",
        // },
        {
            href: "/camera",
            icon: "videocam",
            description: "Camera",
        },
        {
            href: "/dt",
            icon: "workspaces",
            description: "Digital Twin",
        },
        {
            href: "/replay",
            icon: "replay",
            description: "Replay Digital Twin",
        },
        // {
        //     href: "/contact-human",
        //     icon: "support_agent",
        //     description: "Contact Human",
        // },
        {
            href: "/about-us",
            icon: "scatter_plot",
            description: "About LeaMech",
        },
    ]
})