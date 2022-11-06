import styles from "./styles.module.scss";
import Link from "next/link";

export default function Card({ title, icon, href }) {
  return (
    <Link href={href}>
      <a className={styles["card"]}>
        <div className={styles["icon"]}>
          <span className={`${styles["material-icons"]} material-icons`}>
            {icon}
          </span>
        </div>
        <div className={styles["title"]}>{title}</div>
      </a>
    </Link>
  );
}
