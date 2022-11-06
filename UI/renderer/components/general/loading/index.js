import styles from "./loading.module.scss";

export default function Loading({ size = "small" }) {

  return <>Loading...</>

  switch (size) {
    case "small":
      return (
        <div className={styles["loadingio-spinner-spinner-5dnhr28eat2"]}><div className={styles["ldio-53fz0lrw47f"]}>
          <div></div><div></div><div></div>
        </div></div>
      );
    case "medium":
      return (
        <div className={styles["loadingio-spinner-spinner-8vfig2z3vf"]}><div className={styles["ldio-w7mnwgpb5e"]}>
          <div></div><div></div><div></div>
        </div></div>
      );
    case "large":
      break;
    default:
      return (
        <div className={styles["loadingio-spinner-spinner-8vfig2z3vf"]}><div className={styles["ldio-w7mnwgpb5e"]}>
          <div></div><div></div><div></div>
        </div></div>
      );
  }
}
