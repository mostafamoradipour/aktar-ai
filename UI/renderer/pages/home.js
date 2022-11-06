import Head from "next/head";
import Layout from "@/components/general/layout";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";
import { useRecoilState } from "recoil";
// import { useState, useEffect } from "react";
// import axios from "axios";
// import { useRecoilState } from "recoil";
// import {
//   csrfTokenAtom,
//   userLogInAtom,
//   showLoginModalAtom,
// } from "../components/utilities/atoms";
// import { setRecoil } from "recoil-nexus";

export default function Home() {
  // { csrfToken } in input
  // const [userIsAuthenticated, setUserIsAuthenticated] =
  //   useRecoilState(userLogInAtom);
  // const [showLoginModal, setShowLoginModal] =
  //   useRecoilState(showLoginModalAtom);
  // const [csrfToken, setCsrfToken] = useRecoilState(csrfTokenAtom);

  // useEffect(() => {
  //   setCsrfTokenState(csrfToken);
  // }, [csrfToken]);

  const [servicesItems] = useRecoilState(servicesItemsAtom);

  const navBarOptions = [
    {
      name: "Our Services",
      icon: "donut_large",
      menuItems: servicesItems
    },
    // {
    //   name: "Your Dashboard",
    //   icon: "dashboard",
    //   needsLogin: true,
    //   path: "/dashboard",
    // },
  ];

  return (
    <div
    // className="home"
    >
      <Head>
        <title>Lea Mech</title>
      </Head>
      <Layout type="home" navBarOptions={navBarOptions} elevatedNavBar={true}>
        <video
          className="home-video"
          autoPlay
          loop
          muted
        // playsInline
        >
          <source
            src="/videos/home-human-model-walk.mp4"
            type="video/mp4"
          />
        </video>
      </Layout>
    </div>
  );
}
// TODO- test this functionality
// export async function getServerSideProps({
//   params,
//   req,
//   res,
//   query,
//   preview,
//   previewData,
//   resolvedUrl,
//   locale,
//   locales,
//   defaultLocale,
// }) {
//   let csrfToken = {};
//   await axios
//     .get("http://localhost:8000/api/user/set_csrf_cookie/", {
//       withCredentials: true,
//     })
//     .then((response) => {
//       csrfToken = response.data;
//     });
//   // TODO - save CSRF token in a safer place (the way we save api keys maybe?)
//   return { props: { csrfToken } };
// }
