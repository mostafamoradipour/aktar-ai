import styles from './styles.module.scss'
import Router from 'next/router'

export default function Status({ passed, emailExists }) {

    const template = passed === true ? (
        <div className={styles["passed"]}>
            <div className={styles["activation-text"]}>
                ACTIVATION<br />
                SUCCESSFUL
            </div>
            <div className={styles["return-container"]}>
                <div className={styles["return-text"]}>
                    Return to
                </div>
                <button className={styles["return-button"]} onClick={() => {
                    Router.push("/")
                }}>HOME</button>
            </div>
        </div>
    ) : (
        <div className={styles["failed"]}>
            <div className={styles["activation-text"]}>
                ACTIVATION<br />
                FAILED
            </div>
            {emailExists === true ? (
                <div className={styles["return-container"]}>
                    <div className={styles["return-text"]}>
                        Email address already activated
                    </div>
                    <button className={styles["return-button"]} onClick={() => {
                        Router.push("/")
                    }}>HOME</button>
                </div>
            ) : (
                <div className={styles["resend-container"]}>
                    <div className={styles["resend-text"]}>
                        Please re-enter your email address:
                    </div>
                    <div className={styles["resend-input-container"]}>
                        <input placeholder="Your email" className={styles["resend-input"]} />
                        <button className={styles["resend-button"]}>&gt;</button>
                    </div>
                </div>

            )}
        </div>
    )
    return template
}
