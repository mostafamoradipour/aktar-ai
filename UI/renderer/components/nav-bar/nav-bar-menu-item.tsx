import styles from "./nav-bar-menu-item.module.scss";
import gsap from "gsap";
import { useRef, useState } from "react";
import Link from "next/link";

interface Props {
  to?: string;
  description: string;
  icon: string;
  name?: string;
  onClick: React.MouseEventHandler<HTMLElement>;
  comingSoon?: boolean;
  deactivated?: boolean;
  type?: string;
}

export default function NavBarMenuItem({
  to,
  description,
  icon,
  name,
  onClick,
  comingSoon,
  deactivated,
  type,
}: Props) {
  const ref = useRef();
  const [iconIsVisibile, setIconIsVisibile] = useState(true);
  const [textIsVisibile, setTextIsVisibile] = useState(false);
  const [bubbleHasOpacity, setBubbleHasOpacity] = useState(false);

  return (
    // TODO check if the link is good enough and indicate if it is clicked or not. can use a usual link instead for better UX
    <Link href="#">
      <a
        ref={ref}
        className={`${styles[type]} ${name || ""} ${
          to === "no-link" ? "no-link" : ""
        } ${styles["menu-item"]} ${comingSoon ? styles["coming-soon"] : ""} ${
          deactivated ? styles["deactivated"] : ""
        }`}
        onClick={(e) => {
          if (typeof onClick !== "undefined") {
            onClick(e);
          }
          else if (typeof to !== "undefined" && to.length) {
            window.open(
              to,
              "_blank",
              "top=500,left=500,contextIsolation=no,nodeIntegration=yes"
            );
          }
        }}
      >
        <span
          className={`${styles["material-icons"]} material-icons ${
            iconIsVisibile ? "" : styles["hidden-icon"]
          }`}
        >
          {" "}
          {icon}{" "}
        </span>
        <div
          className={`${styles["description"]} ${
            textIsVisibile ? styles["visible-text"] : ""
          }`}
        >
          {description}
        </div>
        {/* coming soon */}
        {comingSoon ? (
          <>
            {/* <div
              className={`${styles["coming-soon-indicator"]} ${
                bubbleHasOpacity ? styles["opacity-0"] : styles["opacity-1"]
              }`}
            ></div> */}
            <div
              className={`${styles["coming-soon-text-bubble"]} ${
                // bubbleHasOpacity ? styles["opacity-1"] : styles["opacity-0"]
                styles["opacity-0"]
              }`}
            >
              Coming&nbsp;Soon!
            </div>
          </>
        ) : (
          ""
        )}
      </a>
    </Link>
  );
}
