import styles from "./styles.module.scss";
import { useRecoilState } from "recoil";
import AddIcon from "@mui/icons-material/Add";
import IconButton from "@mui/material/IconButton";
import Button from "@mui/material/Button";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { useState, useEffect, useRef, FormEvent } from "react";
import Input from "@/components/camera/add-camera/input";
import { showAddCameraAtom, camerasAtom } from "@/components/utilities/atoms";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";

const theme = createTheme({
  palette: {
    primary: {
      main: "#29b6f6",
      contrastText: "#fff",
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          fontSize: "17px",
          marginTop: "40px",
          marginBottom: "-16px",
          fontFamily: "inherit",
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          marginTop: "-4px",
          fontSize: "17px",
        },
      },
    },
  },
});

declare module "@mui/material/styles" {
  interface Palette {
    primary: Palette["primary"];
  }

  // allow configuration using `createTheme`
  interface PaletteOptions {
    primary?: PaletteOptions["primary"];
  }
}

// Update the Button's color prop options
declare module "@mui/material/Button" {
  interface ButtonPropsColorOverrides {
    primary: true;
  }
}

export default function AddCameraModal() {
  const [showAddCamera, setShowAddCamera] = useRecoilState(showAddCameraAtom);
  const [cameras, setCameras] = useRecoilState(camerasAtom);

  const overlayRef = useRef(null);
  const formRef = useRef(null);

  const [inputs, setInputs] = useState<{ id: string }[]>([{ id: uuidv4() }]);
  const addInput = () => {
    if (inputs.length === 0) {
      setInputs([{ id: uuidv4() }]);
      return;
    }

    const t: HTMLFormControlsCollection = formRef.current.elements;
    const nt: string[] = Array.from(t)
      .filter((i: HTMLInputElement) => i.localName === "input")
      .map((i: HTMLInputElement) => i.value);
    if (nt[nt.length - 1].trim() === "") return;

    setInputs([...inputs, { id: uuidv4() }]);
  };

  const [loading, setLoading] = useState(false);

  return (
    <div
      ref={overlayRef}
      className={styles["overlay"]}
      onClick={function removeModal(e) {
        e.stopPropagation();
        if (e.target === overlayRef.current) setShowAddCamera(false);
      }}
    >
      <div className={styles["content"]}>
        {/* Title */}
        <h3 className={styles["title"]}>Add Camera</h3>
        <form
          className={styles["inputs-container"]}
          ref={formRef}
          onSubmit={(e: FormEvent<HTMLFormElement>) => e.preventDefault()}
        >
          {inputs.map((item) => (
            <Input
              key={item.id}
              id={item.id}
              inputs={inputs}
              setInputs={setInputs}
            />
          ))}
        </form>
        {/* Add input btn */}
        <ThemeProvider theme={theme}>
          <IconButton onClick={addInput}>
            <AddIcon fontSize="medium" htmlColor={"#000"} />
          </IconButton>
          {/* Submit btn */}
          <Button
            onClick={async () => {
              setLoading(true);
              const t: HTMLFormControlsCollection = formRef.current.elements;
              const urls: string[] = Array.from(t)
                .filter((i: HTMLInputElement) => i.localName === "input")
                .map((i: HTMLInputElement) => i.value.trim())
                .filter(
                  (i: string) =>
                    i.length &&
                    (i.startsWith("rtsp://") || i.startsWith("http://"))
                );
              const cameraList = urls.map((url) => {
                return {
                  name: "camera-" + uuidv4(),
                  url: url,
                  play: true,
                };
              });
              if (urls.length) {
                try {
                  let res = await axios.post("http://localhost:5000/add", {
                    cameras: cameraList,
                  });
                  setCameras([...cameras, ...cameraList]);
                  setShowAddCamera(false);
                } catch (e) {
                  console.log("error occured while setting cameras");
                }
              }
              setLoading(false);
            }}
            size="large"
            disabled={false}
          >
            {loading ? "Loading" : "Submit"}
          </Button>
        </ThemeProvider>
      </div>
    </div>
  );
}
