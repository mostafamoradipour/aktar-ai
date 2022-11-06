import React, { useRef, useState } from "react";
import { useEffect } from "react";
import styles from "./footer.module.scss";
import Link from "next/link";

export default function Footer({ hasAudioPlayer = false }) {
  const [soundIcon, setSoundIcon] = useState("volume_mute");
  const [soundIsVisible, setSoundIsVisible] = useState(false);
  const audio = useRef();
  useEffect(() => {
    audio.current.volume = 0.2;
    audio.current.loop = true;
    audio.current.currentTime = 2;
    audio.current.addEventListener("canplay", function () {
      if (!soundIsVisible) {
        setSoundIsVisible(true);
      }
    });
  }, []);
  return (
    <div className={styles["footer"]}>
      <div
        className={
          styles["sound-container"] + " " + (hasAudioPlayer ? "" : "d-none")
        }
      >
        <audio preload="auto" ref={audio}>
          <source
            src="/ES-Terminal-Shutdown-Joseph-Beg-cmprsd.mp3"
            type="audio/mpeg"
          />

          {/* <!-- TODO - fallback for browsers that don't support mp3 --> */}

          {/* <!-- fallback for browsers that don't support audio tag --> */}
          <a href="/ES_Terminal-Shutdown-Joseph-Beg.mp3">download audio</a>
        </audio>
        <button
          className={styles["sound"] + soundIsVisible ? styles["visible"] : ""}
          id={styles["sound"]}
          onClick={() => {
            audio.current.paused ? audio.current.play() : audio.current.pause();
            setSoundIcon(audio.current.paused ? "volume_mute" : "volume_up");
          }}
        >
          <span className="material-icons" id={styles["sound-icon"]}>
            {soundIcon}
          </span>
        </button>
      </div>

      <div className={styles["footer-logo-container"]}>
        {/* <!-- <img src="/assets/logo.png" className="icon logo" alt="" /> --> */}
        <Link href={"/home"}>
          {/* <a className={styles["text"]}>LEA MECH</a> */}
          <a className={styles["text"]}>Aktar 0.1.2</a>
        </Link>
      </div>
    </div>
  );
}
