import styles from './styles.module.scss'

export default function Content({ children, type = "text" }) {

    if (type === "text") {
        return (
            <div className={styles["content"]}>
                {children}
            </div>
        )
    }
    else if (type === "image") {
        return (
            <div className={styles["image-content"]}>
                {children}
            </div>
        )
    }
    else if (type === "comment") {
        return (
            <div className={styles["comment-content"]}>
                {children}
            </div>
        )
    }

}
