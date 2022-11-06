import styles from "./styles.module.scss"
import dynamic from 'next/dynamic'
// No-SSR loading because the loadedMetaData doesn't fire on the first render
const VideoPlayer = dynamic(import("../video-player"), {
    ssr: false
})

export default function Container() {
    return (
        <div className={styles["search-container"]}>
            <VideoPlayer />
        </div>
    )
}
