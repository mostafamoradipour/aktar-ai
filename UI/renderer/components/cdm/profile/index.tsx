import styles from "./styles.module.scss";
import { Dispatch, SetStateAction, useRef } from "react";
import CDMImage from "@/components/cdm/image";

interface ProfileInterface {
  face: string;
  body: string;
  id: number;
}
interface Props {
  profile: ProfileInterface | null;
  setProfile: Dispatch<SetStateAction<null>>;
  //   TODO - Fix this type by changing cdm.js to tsx
}
export default function Profile({ profile, setProfile }: Props) {
  const overlayRef = useRef(null);
  return profile === null ? null : (
    <>
      <div
        ref={overlayRef}
        className={styles["overlay"]}
        onClick={(e) => {
          e.stopPropagation();
          if (e.target === overlayRef.current) setProfile(null);
        }}
      >
        <div className={styles["content"]}>
          <CDMImage base64={profile.face} alt="" />
          <CDMImage base64={profile.face} alt="" />
          <div className="name">This is person {profile.id}</div>
          <div className="metrics"></div>
        </div>
      </div>
    </>
  );
}
