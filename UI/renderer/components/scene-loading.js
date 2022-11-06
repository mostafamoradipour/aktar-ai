import { useState, useEffect } from "react";
import styles from "./scene-loading.module.scss";
export default function sceneLoading({ state }) {
  return (
    <div className={`${styles["loading"]} ${state ? "" : styles["hide"]}`}>
      <div className={styles["loader-container"]}>
        <div className={`${styles["loader-4"]} ${styles["center"]}`}>
          <span></span>
        </div>
      </div>
    </div>
  );
}
