import { setScene, setLoader, scene } from './THREE-new-core'
import * as THREE from 'three'
import { sceneInitializedAtom } from "./atoms";
import { getRecoil, setRecoil } from "recoil-nexus";



export function setup3dEngine() {
    if (getRecoil(sceneInitializedAtom)) return;
    setScene()
    setLoader()
    setRecoil(sceneInitializedAtom, true)
}

function checkSceneInitialized() {
    console.log('sceneInit', getRecoil(sceneInitializedAtom))
    return getRecoil(sceneInitializedAtom) ? true : false;
}

export function addPlane({ width, height, direction, position, rotation }) {
    if (!checkSceneInitialized) return
    console.log('scene', scene)
    const planeGeometry = new THREE.BoxBufferGeometry(width, height, 0.1);
    const planeMaterial = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        side: THREE.DoubleSide,
        envMapIntensity: 1,
    });
    const plane = new THREE.Mesh(planeGeometry, planeMaterial);
    plane.receiveShadow = true;
    // plane.position.x = 500;

    // direction
    direction == "horizontal" ? plane.rotateX(THREE.MathUtils.degToRad(90)) : "";

    // position
    position
        ? plane.position.set(position.x || 0, position.y || 0, position.z || 0)
        : "";

    // rotation
    if (rotation) {
        plane.rotateX(THREE.MathUtils.degToRad(rotation.x || 0));
        plane.rotateY(THREE.MathUtils.degToRad(rotation.y || 0));
        plane.rotateZ(THREE.MathUtils.degToRad(rotation.z || 0));
    }

    // scene.add(plane);
    console.log('added plane')
}

