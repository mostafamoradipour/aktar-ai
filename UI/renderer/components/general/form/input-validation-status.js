import React from "react";
import styles from "./input-validation-status.module.scss";

export default function InputValidationStatus({ hasError, text }) {
  return (
    <pre
      className={`${styles["validation-result"]} ${
        hasError ? styles["error"] : styles["no-error"]
      }`}
    >
      {text}
    </pre>
  );
}
