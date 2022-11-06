import CDMGrid, { GridItem } from "@/components/cdm/cdm-grid"
import Content from "@/components/cdm/content"
import Layout from '@/components/general/layout'
import { useRecoilState } from "recoil";
import { sceneUtilsAtom, userLogInAtom, uuidAtom, camerasAtom } from "@/components/utilities/atoms";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";
import axios from "axios";
import { useCookies } from "react-cookie";
import Router from "next/router";
import { useState } from "react";
import CDMImage from '@/components/cdm/image'
import Profile from '@/components/cdm/profile'
import { useEffect } from 'react'
import Modal from '@/components/cdm/modal'
// TODO - convert to tsx
export default function CDM() {
    const [sceneUtils, setSceneUtils] = useRecoilState(sceneUtilsAtom);
    const [userIsAuthenticated, setUserIsAuthenticated] =
        useRecoilState(userLogInAtom);
    const [uuid, setUuid] = useRecoilState(uuidAtom);

    const [cookies, setCookie] = useCookies(["loggedIn"]);

    const [servicesItems] = useRecoilState(servicesItemsAtom);

    const [detectedAssets, setDetectedAssets] = useState([]);
    const [profile, setProfile] = useState(null)
    const [cameras, setCameras] = useRecoilState(camerasAtom);
    const [selectedCams, setSelectedCams] = useState(null)
    const [WS, setWS] = useState(null)

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
                    icon: "restart_alt",
                    description: "Reset Cameras",
                    onClick() {
                        setSelectedCams(null)
                    }
                },
            ],
        },

    ]

    useEffect(() => {
        setWS(new WebSocket("ws://localhost:5001"))
        const timedReq = setInterval(async () => {
            try {
                const response = await axios.get("http://localhost:5000/cdm")
                setDetectedAssets(response.data.persons)
            } catch (e) {
                console.log('error');
            }
            // setDetectedAssets([{ id: 0, face: "" }])
        }, 1000)

        // setDetectedAssets([{ face: "kjhkjhj", id: 6 }])
        return (() => { clearInterval(timedReq) })

    }, [])

    useEffect(() => {
        if (selectedCams !== null && selectedCams.length !== 0 && typeof WS !== null) {
            WS.send(JSON.stringify({ command: "stop" }))
            WS.send(JSON.stringify({ command: "start", cameras: selectedCams }))
        }
    }, [selectedCams])

    const modalProps = {
        selectedCams,
        setSelectedCams,
    }


    // Show a modal and ask which cameras you want to be processed 
    // Start CDM
    // Have a restart button
    return (
        <Layout navBarOptions={navBarOptions} elevatedNavBar={true}>
            {
                selectedCams === null ? <Modal {...modalProps}></Modal> :
                    (<>
                        <CDMGrid >
                            {detectedAssets.map((asset, index) => {
                                return (
                                    <GridItem key={index} onClick={e => setProfile(asset)}>
                                        <Content type="image">
                                            {/* When using layout='fill', the parent element must have position: relative
                                                    When using layout='responsive', the parent element must have display: block*/}
                                            <CDMImage base64={asset.face} alt="" />
                                        </Content>
                                        <Content type="comment">
                                            {asset.id}
                                        </Content>
                                    </GridItem>
                                )
                            }
                            )}
                        </CDMGrid>
                        <Profile profile={profile} setProfile={setProfile} />
                    </>)
            }
        </Layout>
    )
}
