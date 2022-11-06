import React, { useState, useRef, useEffect } from "react";
import styles from "./auth-form.module.scss";
import { useRecoilState } from "recoil";
import {
  userLogInAtom,
  showLoginModalAtom,
  csrfTokenAtom,
} from "../../utilities/atoms.js";
import axios from "axios";
import gsap from "gsap";
import InputValidationStatus from "./input-validation-status";
import FormInput from "./form-input";
import Router from "next/router";
import SnackBar from "../snack-bar/snack-bar";
import { useCookies } from "react-cookie";
import AuthFooter from "./auth-footer";

export default function AuthForm() {
  const [cookies, setCookie] = useCookies(["loggedIn"]);

  const [authTypeIsLogin, setAuthTypeIsLogin] = useState(true);
  const [authLoading, setAuthLoading] = useState(false);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [userIsAuthenticated, setUserIsAuthenticated] =
    useRecoilState(userLogInAtom);
  const [showLoginModal, setShowLoginModal] =
    useRecoilState(showLoginModalAtom);
  const [csrfTokenState, setCsrfTokenState] = useRecoilState(csrfTokenAtom);

  const [snackBarState, setSnackBarState] = useState("closed");
  const [snackBarType, setSnackBarType] = useState("error");

  // useEffect(() => {
  //   const tl = gsap.timeline();
  //   tl.to("." + styles["loading"], {
  //     duration: 0.5,
  //     backgroundColor: "blue",
  //   });
  // }, [authLoading]);

  const login = () => {
    setAuthLoading(true);

    const data = {
      email: email,
      password: password,
    };

    axios
      .get("https://api.kachrobotics.com/api/user/set_csrf_cookie/", {
        withCredentials: true,
      })

      .then((res) => {
        // console.log("csrf : ", res.data);

        setCsrfTokenState(res.data["csrfmiddlewaretoken"]);

        let formData = new FormData();
        formData.append("csrfmiddlewaretoken", res.data["csrfmiddlewaretoken"]);
        formData.append("email", data.email);
        formData.append("password", data.password);

        axios({
          method: "post",
          url: "https://api.kachrobotics.com/api/user/login/",
          data: formData,
          headers: { "Content-Type": "multipart/form-data" },
          withCredentials: true,
        }).then((loginRes) => {
          if (loginRes.status === 200) {
            // console.log("login: ", loginRes.data);

            // console.log("refresh:", response.data);

            setAuthLoading(false);

            setUserIsAuthenticated(true);
            setShowLoginModal(false);

            setCookie("loggedIn", true, { path: "/" });

            Router.push("/dashboard");
          }
        })
          .catch((err) => {
            // If CSRF check hasn’t been passed:
            // HTTP_403_FORBIDDEN
            setError("Error logging in... Please try again.");
            setSnackBarState("open");
            setAuthLoading(false);
          });
      })
      .catch((err) => {
        // If CSRF check hasn’t been passed:
        // HTTP_403_FORBIDDEN
        setError("Error logging in... Please try again.");
        setSnackBarState("open");
        setAuthLoading(false);
      });
  };

  const signup = () => {
    setAuthLoading(true);

    const data = {
      firstName: firstName,
      lastName: lastName,
      userName: username,
      email: email,
      password: password,
    };

    //   // console.log(response.status);
    //   // console.log(response.statusText);// console.log(response.headers);
    //   // console.log(response.config);

    const res = axios
      .get("https://api.kachrobotics.com/api/user/set_csrf_cookie/", {
        withCredentials: true,
      })
      .then((res) => {
        console.log("token", res.data);
        setCsrfTokenState(res.data["csrfmiddlewaretoken"]);
        let formData = new FormData();
        formData.append("csrfmiddlewaretoken", res.data["csrfmiddlewaretoken"]);
        formData.append("email", data.email);
        formData.append("password", data.password);
        formData.append("first_name", data.firstName);
        formData.append("last_name", data.lastName);
        formData.append("user_name", data.userName);
        const registerRes = axios({
          method: "post",
          url: "https://api.kachrobotics.com/api/user/register/",
          data: formData,
          headers: { "Content-Type": "multipart/form-data" },
          withCredentials: true,
        }).then((response) => {
          // console.log("register: ", response);
          // localStorage.setItem("csrfmiddlewaretoken",
          // response.data['csrfmiddlewaretoken'])
          setAuthLoading(false);
          setError("The activation link has been sent to your email.");
          setSnackBarType("info");
          setSnackBarState("open");

        }).catch((err) => {
          setAuthLoading(false);
          setError("Error registering... Please try again.");
          // TODO - set snackbar color before every open
          setSnackBarState("open");
        });
        // });
      });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (authTypeIsLogin) {
      login();
    } else {
      signup();
    }
  };

  const changeAuthType = ({ setToLogin }) => {
    // TODO - check auth type to prevent re animating
    let tl = gsap.timeline();
    tl.to("." + styles["auth-form-container"], {
      duration: 0.3,
      opacity: 0,
      onComplete: () => {
        setAuthTypeIsLogin(setToLogin);
      },
    }).to("." + styles["auth-form-container"], {
      duration: 0.3,
      opacity: 1,
    });
  };

  return (
    <div
      className={showLoginModal ? styles["auth-form"] : "d-none"}
    //   onClick={() => {
    //     setShowLoginModal(false);
    //   }}
    >

      <div className={styles["auth-form-container"]}>
        {/* Exit Icon */}
        <div className={styles["exit"]}>
          <i
            className={`${styles["material-icons"]} material-icons`}
            onClick={() => {
              setShowLoginModal(false);
            }}
          >
            close
          </i>
        </div>
        {/* Auth type */}
        <div className={styles["auth-type"]}>
          <span
            className={`mr-4 ${authTypeIsLogin ? styles["active"] : ""}`}
            onClick={() => {
              changeAuthType({ setToLogin: true });
            }}
          >
            Login
          </span>{" "}
          /{" "}
          <span
            className={`ml-4 ${!authTypeIsLogin ? styles["active"] : ""}`}
            onClick={() => {
              changeAuthType({ setToLogin: false });
            }}
          >
            Sign up
          </span>
        </div>

        {/* Auth header title */}
        <h1 className={styles["auth-form-header"]}>
          {authTypeIsLogin ? (
            <>
              <span className={styles["title"]}>Login</span>
            </>
          ) : (
            "Sign Up"
          )}
        </h1>

        {/* Auth body */}
        <form className={styles["auth-form-body"]}>

          {/* Sign-up fields */}
          {!authTypeIsLogin ? (
            <>
              {/* TODO - Add validation visualizations with clear errors - use the saved article  */}
              <div className={`${styles["sign-up-names-input"]}`}>
                {/* First Name */}
                <label>
                  First Name:
                  <FormInput
                    type="text"
                    name="first-name"
                    value={firstName}
                    setValue={setFirstName}
                    validation={(firstName) => {
                      if (firstName.length > 1 && firstName.split(" ").length === 1) {
                        return {
                          hasError: false,
                          // text: "first name valid",
                        }
                      }
                      return {
                        hasError: true,
                        text: "first name not valid",
                      }
                    }}
                  />
                </label>
                {/* Last Name */}
                <label>
                  Last Name:
                  <FormInput
                    type="text"
                    name="last-name"
                    value={lastName}
                    setValue={setLastName}
                    validation={(lastName) => {
                      if (lastName.length > 1 && lastName.split(" ").length === 1) {
                        return {
                          hasError: false,
                          // text: "last name valid",
                        }
                      }
                      return {
                        hasError: true,
                        text: "last name not valid",
                      }
                    }}
                  />
                </label>
              </div>
              {/* Username field */}
              <label className={styles["auth-field"]}>
                Username:
                <FormInput
                  type="text"
                  name="username"
                  value={username}
                  setValue={setUsername}
                  validation={(username) => {
                    // username validation regex
                    let re =
                      /^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$/;
                    // └─────┬────┘└───┬──┘└─────┬─────┘└─────┬─────┘ └───┬───┘
                    //       │         │         │            │           no _ or . at the end
                    //       │         │         │            │
                    //       │         │         │            allowed characters
                    //       │         │         │
                    //       │         │         no __ or _. or ._ or .. inside
                    //       │         │
                    //       │         no _ or . at the beginning
                    //       │
                    //       username is 8-20 characters long
                    if (re.test(String(username).toLowerCase())) {
                      return {
                        hasError: false,
                        // text: "username valid"
                      }
                    }
                    return {
                      hasError: true,
                      text: "Username must be 8-20 characters long, \nNo _ or . at the beginning, \nNo __ or _. or ._ or .. inside, \nNo _ or . at the end",
                    }

                  }}
                />
              </label>
            </>
          ) : (
            ""
          )}

          {/* Common fields */}

          {/* Email */}
          <label className={styles["auth-field"]}>
            email:
            <FormInput
              setValue={setEmail}
              value={email}
              // if this is true all the status messages are cleared
              clearStatus={authTypeIsLogin}
              validation={
                authTypeIsLogin
                  ? () => true
                  : async (email) => {
                    // TODO - show loading spinner
                    let re =
                      /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

                    // Check if email exists
                    let formData = new FormData();
                    formData.append("field", "email");
                    formData.append("content", email);
                    let existence = await axios({
                      method: "post",
                      url: "https://api.kachrobotics.com/api/user/check_existence/",
                      data: formData,
                      headers: { "Content-Type": "multipart/form-data" },
                      withCredentials: true,
                    })
                      .catch((error) => {
                        // if (error.response.status === 306) {
                        return {
                          hasError: true,
                          text: "Email already exists",
                        }
                        // }
                      });

                    if (existence.hasError === true) return existence

                    return re.test(String(email).toLowerCase())
                      ? {
                        hasError: false,
                        // text: "email valid",
                      }
                      : {
                        hasError: true,
                        text: "email not valid",
                      };
                  }
              }
              name="email"
              type="text"
            />
          </label>
          {/* Password */}
          <label className={styles["auth-field"]}>
            Password:
            <FormInput
              setValue={setPassword}
              value={password}
              clearStatus={authTypeIsLogin}
              validation={
                !authTypeIsLogin
                  ? (password) => {
                    let re =
                      // this regex checks for a minimum of 8 characters, at least one uppercase letter,
                      //  one lowercase letter, and one number or special character
                      //  (regex source: https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a)
                      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
                    return re.test(String(password))
                      ? {
                        hasError: false,
                        // text: "password valid",
                      }
                      : {
                        hasError: true,
                        text: "Password must contain at least 8 characters, \nAt least one uppercase letter, \nAt least one lowercase letter, \nAt least one number or special character",
                      };
                  }
                  : () => {
                    return { hasError: false, text: "" };
                  }
              }
              name="password"
              type="password"
            />
          </label>

          {/* Submit */}
          <button
            type="submit"
            className={`${styles["auth-form-body-button"]}`}
            onClick={handleSubmit}
          >
            {authLoading ? (
              <div className={styles["loading"]}></div>
            ) : (
              <>Submit</>
            )}
          </button>
        </form>
      </div>

      <AuthFooter onClick={() => {
        setShowLoginModal(false);
        Router.push("/");
      }} />

      <SnackBar
        text={error}
        type={snackBarType}
        snackBarState={snackBarState}
        setSnackBarState={setSnackBarState}
      />
    </div>
  );
}
