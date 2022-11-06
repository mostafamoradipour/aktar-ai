import React from "react";
import styles from "./scene-options.module.scss";

export default function SceneOptions() {
  return (
    <div className={styles["options"]}>
      <div className={styles["option"]}>
        <input
          type="checkbox"
          name="filtered-view"
          id={styles["filtered-view"]}
        />
        <label htmlFor="filtered-view">Filtered view</label>
      </div>
      <div className={styles["option"]}>
        <input type="checkbox" name="top-view" id={styles["top-view"]} />
        <label htmlFor="top-view">Top view</label>
      </div>
    </div>
  );
}
