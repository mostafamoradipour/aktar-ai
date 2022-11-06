import { v4 as uuidv4 } from "uuid";
import RemoveIcon from "@mui/icons-material/Remove";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import styles from "./styles.module.scss";

export default function Input({ id, inputs, setInputs }) {
  const removeInput = (id: string) => {
    const t = inputs.filter((item: { id: string }) => item.id !== id);
    setInputs(t);
  };
  return (
    <div className={styles["input-container"]}>
      {/* <input type="text" className={styles["input"]} size={24} /> */}
      <TextField
        id="outlined-basic"
        label="RTSP URL"
        variant="outlined"
        size="small"
        margin="dense"
        color="info"
      />
      <IconButton onClick={() => removeInput(id)}>
        <RemoveIcon fontSize="medium" htmlColor={"#000"} />
      </IconButton>
    </div>
  );
}
