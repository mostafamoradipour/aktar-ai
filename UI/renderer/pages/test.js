import { useEffect, useRef, useState } from "react";
import {
    main,
    basicSetup,
    applyEnvMap,
    applyAllModels,
    applyLights,
    applyAnimations,
    applyDomInteractions,
    animate,
    debugTHREE,
} from "@/components/utilities/THREE-scene-setup-custom";

import { setup3dEngine, addPlane } from "@/components/utilities/THREE-engine";

import { showLoadingAtom, csrfTokenAtom } from "@/components/utilities/atoms";
import { useRecoilState } from "recoil";
import gsap from "gsap";
import axios from "axios";

export default function Test() {
    const canvasRef = useRef(null);

    setup3dEngine()
    // addPlane(100, 100)
    // addGrid()



    // useEffect(() => {
    //     // attachSceneToDom()
    // })

    return (
        <>
            <canvas id="main-scene" ref={canvasRef}></canvas>
        </>
    );
}
