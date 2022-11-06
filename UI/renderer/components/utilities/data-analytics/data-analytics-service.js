import { sceneHumanData } from '../atoms'
import { getRecoil, setRecoil } from "recoil-nexus";


export default function updateAnalytics(main) {
    const data = getRecoil(sceneHumanData)
    const count = main.humans.length
    console.log([...data, { count, time: Date.now() }])
    setRecoil(sceneHumanData, [...data, { count, time: Date.now() }])
}