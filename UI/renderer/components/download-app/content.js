import styles from './styles.module.scss'
import Image from 'next/image'

export default function Content() {
    return (
        <div className={styles.pageContainer}>
            <div className={styles.container}>
                <div className={styles.text}>Download App Now</div>

                <div>
                    <Image className={styles.downloadBadges} src="/images/downloads.png" alt="download-badges" width={300} height={200} />
                </div>
            </div>
        </div>
    )
}
