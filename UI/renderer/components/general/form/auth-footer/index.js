import styles from "./styles.module.scss";
import Link from "next/link";

export default function AuthFooter({ onClick }) {


  return (
    <div className={styles["footer"]} onClick={onClick}>

      <div className={styles["footer-logo-container"]}>
        {/* <!-- <img src="/assets/logo.png" className="icon logo" alt="" /> --> */}
        <Link href={"/"}>
          {/* <a className={styles["text"]}>LEA MECH</a> */}
          <a className={styles["text"]}>LeaMech</a>
        </Link>
      </div>
    </div>
  );
}
