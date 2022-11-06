import { useState, useEffect } from "react";
import Head from "next/head";
import Layout from "@/components/general/layout";
import { useRecoilState } from "recoil";
import { sceneUtilsAtom, userLogInAtom, uuidAtom } from "@/components/utilities/atoms";
import Scene3d from "@/components/dashboard/scene-3d";
import axios from "axios";
import { useCookies } from "react-cookie";
import Router from "next/router";
import Loading from "@/components/general/loading";

export default function Dashboard() {
  const [sceneUtils, setSceneUtils] = useRecoilState(sceneUtilsAtom);
  const [userIsAuthenticated, setUserIsAuthenticated] =
    useRecoilState(userLogInAtom);
  const [uuid, setUuid] = useRecoilState(uuidAtom);

  const [cookies, setCookie] = useCookies(["loggedIn"]);

  const [userName, setUserName] = useState("");

  useEffect(() => {
    axios
      .get("https://api.kachrobotics.com/api/user/set_csrf_cookie/", {
        withCredentials: true,
      })
      .then((res) => {
        let bodyFormData = new FormData();
        bodyFormData.append(
          "csrfmiddlewaretoken",
          res.data["csrfmiddlewaretoken"]
        );
        return bodyFormData;

      })
      .then((bodyFormData) => {
        axios({
          method: "post",
          url: "https://api.kachrobotics.com/api/user/get_uuid/",
          data: bodyFormData,
          headers: { "Content-Type": "multipart/form-data" },
          withCredentials: true,
        })
          .then((response) => {
            console.log(response.data);
            if (response.status === 200) {
              axios({
                method: "get",
                url: "https://api.kachrobotics.com/api/user/get_vspace_data/",
                data: bodyFormData,
                headers: { "Content-Type": "multipart/form-data" },
                withCredentials: true,
              })
                .then((response) => {
                  setUserName(response.data.username)
                })
                .catch((error) => {
                  console.log('error', error.response.status);
                })
            }
          })
          .catch((error) => {
            // console.log("not logged in");
          });
      });

  }, [])

  const navBarOptions = [
    {
      name: userName || Loading({ size: "small" }),
      icon: "fingerprint",
      needsLogin: true,
      menuItems: [
        {
          href: "/camera",
          icon: "videocam",
          description: "Camera",
        },
        {
          href: "/data-analytics?uuid=" + uuid,
          icon: "stacked_bar_chart",
          description: "Data Analysis",
        },
        {
          // TODO - needs fix in navbar
          // href: "/",
          icon: userIsAuthenticated ? "logout" : "login",
          description: userIsAuthenticated ? "Log Out" : "Log in",
          onClick: async () => {
            let csrf = await axios.get(
              "https://api.kachrobotics.com/api/user/set_csrf_cookie/",
              {
                withCredentials: true,
              }
            );
            const formData = new FormData();
            formData.append(
              "csrfmiddlewaretoken",
              csrf.data.csrfmiddlewaretoken
            );
            const res = await axios({
              method: "post",
              url: "https://api.kachrobotics.com/api/user/logout/",
              data: formData,
              headers: { "Content-Type": "multipart/form-data" },
              withCredentials: true,
            });
            // console.log(res);
            if (res.status === 200) {
              // TODO - Write recoil selector to automatically set cookies with this action
              setCookie("loggedIn", false, { path: "/" });
              setUserIsAuthenticated(false);

              Router.push("/");
            }
          },
        },
      ],
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

      ],
    },
  ];

  return (
    <>
      <Layout type="3d-scene" navBarOptions={navBarOptions}>
        <Scene3d type="custom" />
      </Layout>
    </>
  );
}
