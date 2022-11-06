import styles from "./snack-bar.module.scss";

export default function SnackBar({
  text,
  type,
  snackBarState,
  setSnackBarState,
}) {
  return (
    <div
      className={`${styles["snack-bar"]} ${styles[type]} ${styles[snackBarState]}`}
    >
      {text}
      <div
        className={styles["action"]}
        onClick={() => setSnackBarState("closed")}
      >
        Close
      </div>
    </div>
  );
}
