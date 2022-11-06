import React from "react";
import styles from "./styles.module.scss";

export default function ContactTable() {
  return (
    <>
      {/* <div className={styles["page-title"]}>Contact Us</div> */}
      <main className={styles["main-content"]}>
        <div className={styles["contacts-table"]}>
          <ul className={styles["responsive-table"]}>
            <li className={styles["table-header"]}>
              <div className={`${styles["col"]} ${styles["col-1"]}`}>
                Contact ID
              </div>
              <div className={`${styles["col"]} ${styles["col-2"]}`}>
                Contact Name
              </div>
              <div className={`${styles["col"]} ${styles["col-3"]}`}>
                Number
              </div>
            </li>
            <li className={styles["table-row"]}>
              <div
                className={`${styles["col"]} ${styles["col-1"]}`}
                data-label="ID"
              >
                01
              </div>
              <div
                className={`${styles["col"]} ${styles["col-2"]}`}
                data-label="Contact Name"
              >
                Test Name
              </div>
              <div
                className={`${styles["col"]} ${styles["col-3"]}`}
                data-label="Number"
              >
                +1-000-000-0000
              </div>
            </li>
          </ul>
        </div>
      </main>
    </>
  );
}
