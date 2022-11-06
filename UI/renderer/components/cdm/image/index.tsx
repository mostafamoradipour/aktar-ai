import { useEffect, useRef } from "react";
import Image from "next/image";
export default function CDMImage({ base64 }) {
  return (
    <Image
      src={"data:image/jpg;base64," + base64}
      alt="cdm-img"
      height={112*2}
      width={112*2}
    />
  );
}
