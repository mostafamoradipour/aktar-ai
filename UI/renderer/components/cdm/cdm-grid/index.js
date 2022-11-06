import styles from './styles.module.scss'

export default function CDMGrid({ children }) {
    // grid for device sizes
    // {
    //     xs: 12,
    //     sm: 6,
    //     md: 4,
    //     lg: 3,
    //     xl: 2,
    // }
    return (
        <div id={styles["grid"]}>{children}</div>
    )
}

export function GridItem({ children, onClick }) {
    return (
        <div className={styles["grid-item"]} onClick={onClick}>{children}</div>
    )
}
