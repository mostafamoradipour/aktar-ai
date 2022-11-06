import { useEffect, useState } from "react";
import styles from "./auth-form.module.scss";
import styles2 from "./form-input.module.scss";
import InputValidationStatus from "./input-validation-status";

export default function FormInput({
  setValue,
  value,
  validation,
  name,
  type,
  clearStatus,
}) {
  const [hasError, setHasError] = useState(false);
  const [text, setText] = useState("");

  useEffect(() => {
    if (clearStatus) {
      setHasError(false);
      setText("");
    }
  }, [clearStatus]);

  return (
    <>
      <InputValidationStatus hasError={hasError} text={text} />

      <input
        type={type}
        name={name}
        className={styles["auth-form-body-input"]}
        onChange={(e) => {
          setValue(e.target.value);
        }}
        value={value}
        onBlur={async (e) => {
          let status = await validation(e.target.value);
          status.hasError ? setHasError(true) : setHasError(false);
          setText(status.text);
          // console.log(status);
        }}
      />
    </>
  );
}
