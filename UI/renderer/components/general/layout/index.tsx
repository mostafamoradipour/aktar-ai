import Head from "next/head";
import Image from "next/image";
import Link from "next/link";
import Footer from "@/components/general/footer";
import NavBar from "../../nav-bar/nav-bar";
import AuthForm from "../form/auth-form";
import SceneLoading from "../../scene-loading";
import { useState, useEffect } from "react";
import { showLoadingAtom, userLogInAtom } from "../../utilities/atoms";
import { useRecoilState } from "recoil";
import { useCookies } from "react-cookie";
import { Option as NavBarOption } from "@/components/nav-bar/nav-bar";

interface Props {
  children: JSX.Element;
  type?: string;
  navBarOptions: NavBarOption[];
  footerAudio: boolean;
  elevatedNavBar: boolean;
}
export default function Layout({
  children,
  type = "",
  navBarOptions,
  footerAudio = true,
  elevatedNavBar = false,
}) {
  const [cookies, setCookie] = useCookies(["loggedIn"]);
  const [loggedIn, setLoggedIn] = useRecoilState(userLogInAtom);

  useEffect(() => {
    if (cookies.loggedIn === "true") {
      setLoggedIn(true);
    } else {
      setLoggedIn(false);
    }
    // console.log("cookie", cookies.loggedIn);
    // console.log(loggedIn);
  }, [cookies.loggedIn, loggedIn]);

  const [showLoading, setShowLoading] = useRecoilState(showLoadingAtom);
  function typeSpecificRendering() {
    switch (type) {
      case "3d-scene":
        return <SceneLoading state={showLoading} />;
        break;
    }
  }

  return (
    <div id="app">
      {typeSpecificRendering()}
      <AuthForm />
      <NavBar options={navBarOptions} elevated={elevatedNavBar} />
      {children}
      <Footer hasAudioPlayer={footerAudio} />
    </div>
  );
}
