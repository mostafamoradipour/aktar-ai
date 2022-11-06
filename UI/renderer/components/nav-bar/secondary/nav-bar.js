import React, { useRef, useState } from "react";
import NavBarMenuItem from "./nav-bar-menu-item";
import styles from "./nav-bar.module.scss";
import gsap from "gsap";
import { useRecoilState } from "recoil";
import { userLogInAtom, showLoginModalAtom } from "../utilities/atoms.js";
import Router from "next/router";

export default function NavBar({ options }) {
  const [userIsAuthenticated, setUserIsAuthenticated] =
    useRecoilState(userLogInAtom);

  const [showLoginModal, setShowLoginModal] =
    useRecoilState(showLoginModalAtom);

  const [menuIsActive, setMenuIsActive] = useState([false, false]);
  const [menuIsVisible, setMenuIsVisible] = useState([false, false]);

  return (
    <>
      {
        // If any options are specified, show the nav bar
        options ? (
          <div className={styles["nav-bar"]}>
            {
              // for each option, show a nav bar option
              options.map((option, index) => (
                <div key={index}>
                  {/* A menu background for every option with menu */}
                  <div
                    className={`${styles["menu-background"]}   ${
                      // some different styles for the menu on the right
                      index === 1 ? styles["d-right"] : ""
                    } ${
                      // if the menu is active, show the menu
                      option.menuItems && menuIsActive[index]
                        ? styles["opacity-1"]
                        : ""
                    }`}
                  ></div>
                  {/*  Option */}
                  <div
                    key={index}
                    className={`${styles["option"]}`}
                    // apply animations and activate the menu when mouse enters
                    onMouseEnter={() => {
                      let tl = gsap.timeline();
                      tl.to(".option-icon" + index, {
                        duration: 0.5,
                        rotation: "180deg",
                      }).to(
                        ".option-icon-text" + index,
                        {
                          duration: 0.5,
                          opacity: option.menuItems ? 0 : 1,
                        },
                        "-=0.5"
                      );
                      gsap.delayedCall(0.1, () => {
                        let arr = [...menuIsActive];
                        arr[index] = true;
                        setMenuIsActive(arr);
                      });
                      let arr = [...menuIsVisible];
                      arr[index] = true;
                      setMenuIsVisible(arr);
                    }}
                    // apply animations and deactivate the menu when clicked (for touch devices)
                    onClick={
                      option.needsLogin && !option.menuItems
                        ? userIsAuthenticated
                          ? () => {
                              Router.push(option.path);
                            }
                          : () => {
                              setShowLoginModal(true);
                            }
                        : () => {
                            let tl = gsap.timeline();
                            tl.to(".option-icon" + index, {
                              duration: 0.5,
                              rotation: "180deg",
                            }).to(
                              ".option-icon-text" + index,
                              {
                                duration: 0.5,
                                opacity: option.menuItems ? 0 : 1,
                              },
                              "-=0.5"
                            );
                            gsap.delayedCall(0.1, () => {
                              let arr = [...menuIsActive];
                              arr[index] = true;
                              setMenuIsActive(arr);
                            });
                            let arr = [...menuIsVisible];
                            arr[index] = true;
                            setMenuIsVisible(arr);
                          }
                    }
                  >
                    {/* Icon */}
                    <span
                      className={`${styles["material-icons"]} material-icons ${
                        "option-icon" + index
                      }`}
                    >
                      {option.icon}
                    </span>
                    {/* Icon Text */}
                    <div
                      className={`${styles["icon-text"]} ${
                        "option-icon-text" + index
                      }`}
                    >
                      {/* If the option needs login and the user is not logged in,
                       just shows signup/in text. else, it shows the actual name */}
                      {option.needsLogin && !userIsAuthenticated
                        ? "Sign up/Sign in"
                        : option.name}
                    </div>

                    {/* **Menu**
                    If the option has menu items, show the menu */}
                    {!option.menuItems ? (
                      <></>
                    ) : (
                      <div
                        className={`${styles["menu"]} 
                        ${menuIsActive[index] ? styles["menu-active"] : ""} 
                        ${menuIsVisible[index] ? styles["menu-visible"] : ""}
                        ${styles[(index === 1 ? "right" : "left") + "-side"]}`}
                      >
                        {/* for every menuItem calls the menuItem component */}
                        {option.menuItems.map((item, itemIndex) => {
                          // only displayes up to 6 menu items
                          if (itemIndex < 6)
                            return (
                              <NavBarMenuItem
                                comingSoon={item.comingSoon}
                                icon={item.icon}
                                description={item.description}
                                key={itemIndex}
                                // The link to which the menu item will redirect to
                                to={
                                  userIsAuthenticated || !option.needsLogin
                                    ? item.href
                                    : "#"
                                }
                                onClick={
                                  userIsAuthenticated || !option.needsLogin
                                    ? item.onClick
                                    : () => {
                                        setShowLoginModal(true);
                                      }
                                }
                              />
                            );
                          // the last item is a "more" item
                          else if (itemIndex === 6)
                            return (
                              <NavBarMenuItem
                                name={styles["menu-item"]}
                                description="more"
                                icon="more_horiz"
                                key={itemIndex}
                                to={
                                  userIsAuthenticated || !option.needsLogin
                                    ? item.href
                                    : "#"
                                }
                                onClick={
                                  userIsAuthenticated || !option.needsLogin
                                    ? undefined
                                    : () => {
                                        setShowLoginModal(true);
                                      }
                                }
                              />
                            );
                          else return;
                        })}
                        {/* The final item is for closing the menu */}
                        {
                          <NavBarMenuItem
                            name={styles["menu-item"]}
                            description="Close"
                            icon="close"
                            onClick={(e) => {
                              e.stopPropagation();
                              let tl = gsap.timeline();
                              tl.to(".option-icon" + index, {
                                duration: 0.5,
                                rotation: "-180deg",
                              }).to(
                                ".option-icon-text" + index,
                                {
                                  duration: 0.5,
                                  opacity: 1,
                                },
                                "-=0.5"
                              );
                              gsap.delayedCall(0.5, () => {
                                let arr = [...menuIsVisible];
                                arr[index] = false;
                                setMenuIsVisible(arr);
                              });
                              let arr = [...menuIsActive];
                              arr[index] = false;
                              setMenuIsActive(arr);
                            }}
                          />
                        }
                      </div>
                    )}
                  </div>
                </div>
              ))
            }
          </div>
        ) : (
          <div></div>
        )
      }
    </>
  );
}
