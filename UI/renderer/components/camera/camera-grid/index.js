import styles from './styles.module.scss'
import Content from "@/components/camera/content";
import StreamPlayer from "@/components/camera/stream/index";

export default function CameraGrid({ cameras }) {
    // grid for device sizes
    // {
    //     xs: 12,
    //     sm: 6,
    //     md: 4,
    //     lg: 3,
    //     xl: 2,
    // }
    return (
        <div className={`${styles["grid"]} ${styles["grid-" + (cameras.length > 4 ? 'large' : cameras.length)]}`}>
            {cameras.map((camera, index) => {
                return (
                    <GridItem key={index} cameraCount={cameras.length}>
                        {/* <Content> */}
                            <StreamPlayer port={camera.port} id={camera.uuid} />
                        {/* </Content> */}
                    </GridItem>
                );
            })}
        </div>
    )
}

function GridItem({ children, cameraCount }) {
    return (
        <div className={`${styles["grid-item"]} ${styles['flx-base-' + (cameraCount < 4 ? cameraCount : 4)]}`}>{children}</div>
    )
}
