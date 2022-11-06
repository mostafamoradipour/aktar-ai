import React, { useRef, useState } from "react";
import NavBarMenuItem from "./nav-bar-menu-item";
import styles from "./nav-bar.module.scss";
import gsap from "gsap";
import { useRecoilState } from "recoil";
import { userLogInAtom, showLoginModalAtom } from "../utilities/atoms.js";
import Router from "next/router";

export interface Option {
  icon: string;
  name: string;
  path?: string;
  menuItems?: MenuItem[];
  needsLogin?: boolean;
}
interface MenuItem {
  href: string;
  icon: string;
  description: string;
  comingSoon?: boolean;
  deactivated?: boolean;
  onClick?: React.MouseEventHandler<HTMLElement>;
}
interface Props {
  options?: Option[];
  elevated: boolean;
}
export default function NavBar({ options, elevated }: Props) {
  const [userIsAuthenticated, setUserIsAuthenticated] =
    useRecoilState(userLogInAtom);

  const [showLoginModal, setShowLoginModal] =
    useRecoilState(showLoginModalAtom);

  const [menuIsActive, setMenuIsActive] = useState([false, false]);
  const [menuIsVisible, setMenuIsVisible] = useState([false, false]);

  const menuBackgroundJSX = (option: Option, index: number) =>
    option.menuItems && (
      <div
        className={`${styles["menu-background"]}   ${
          // some different styles for the menu on the right
          index === 1 ? styles["d-right"] : ""
        } ${!menuIsActive[index] ? "d-none" : ""}
    ${
      // if the menu is active, show the menu
      menuIsVisible[index] ? styles["opacity-1"] : ""
    }`}
      ></div>
    );

  const navbarLoginBtnJSX = (
    <div
      className={`${styles["option"]}`}
      onClick={() => {
        setShowLoginModal(true);
      }}
    >
      <button className={`${styles["sign-in-btn"]}`}>Sign up/Sign in</button>
    </div>
  );

  const optionIconJSX = (option: Option, index: number) => (
    <>
      <span
        className={`${styles["material-icons"]} material-icons ${
          "option-icon" + index
        }`}
      >
        {option.icon}
      </span>
      {/* Icon Text */}
      <div className={`${styles["icon-text"]} ${"option-icon-text" + index}`}>
        {/* If the option needs login and the user is not logged in,
     just shows signup/in text. else, it shows the actual name */}
        {option.needsLogin && !userIsAuthenticated
          ? "Sign up/Sign in"
          : option.name}
      </div>
    </>
  );

  const handleOptionMouseEnter = (option: Option, index: number) => {
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
  };

  const handleOptionClick = (
    option: Option,
    index: number
  ): React.MouseEventHandler<HTMLElement> => {
    if (menuIsActive[index]) {
      return (e: React.MouseEvent<HTMLElement, MouseEvent>) => {
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
          let arr = [...menuIsActive];
          arr[index] = false;
          setMenuIsActive(arr);
        });
        let arr = [...menuIsVisible];
        arr[index] = false;
        setMenuIsVisible(arr);
      };
    } else if (!option.menuItems) {
      return () => {
        Router.push(option.path);
      };
    } else {
      return () => {
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
      };
    }
  };

  const menuItemJSX = (option: Option) => {
    const handleItemClick = (onClick: React.MouseEventHandler<HTMLElement>) => {
      return userIsAuthenticated || !option.needsLogin
        ? onClick
        : () => {
            setShowLoginModal(true);
          };
    };

    const handleLastItemClick =
      userIsAuthenticated || !option.needsLogin
        ? undefined
        : () => {
            setShowLoginModal(true);
          };

    const to = (href: string) =>
      userIsAuthenticated || !option.needsLogin ? href : "#";

    return option.menuItems.map((item: MenuItem, itemIndex: number) => {
      // only displayes up to 8 menu items
      if (itemIndex < 8)
        return (
          <NavBarMenuItem
            comingSoon={item.comingSoon}
            icon={item.icon}
            description={item.description}
            key={itemIndex}
            deactivated={item.deactivated}
            // The link to which the menu item will redirect to
            to={to(item.href)}
            onClick={handleItemClick(item.onClick)}
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
            to={to(item.href)}
            onClick={handleLastItemClick}
          />
        );
      else return;
    });
  };

  // const menuCloseJSX = (index: number) => {
  //   const handleCloseClick: React.MouseEventHandler<HTMLElement> = (
  //     e: React.MouseEvent<HTMLElement, MouseEvent>
  //   ) => {
  //     e.stopPropagation();
  //     let tl = gsap.timeline();
  //     tl.to(".option-icon" + index, {
  //       duration: 0.5,
  //       rotation: "-180deg",
  //     }).to(
  //       ".option-icon-text" + index,
  //       {
  //         duration: 0.5,
  //         opacity: 1,
  //       },
  //       "-=0.5"
  //     );
  //     gsap.delayedCall(0.5, () => {
  //       let arr = [...menuIsActive];
  //       arr[index] = false;
  //       setMenuIsActive(arr);
  //     });
  //     let arr = [...menuIsVisible];
  //     arr[index] = false;
  //     setMenuIsVisible(arr);
  //   };

  //   return (
  //     <NavBarMenuItem
  //       name={styles["menu-item"]}
  //       description="Close"
  //       icon="close"
  //       onClick={handleCloseClick}
  //       type={"close" + index}
  //     />
  //   );
  // };

  const menuItemsJSX = (option: Option, index: number) => {
    const items = option.menuItems || [];
    return (
      items.length !== 0 && (
        <div
          className={`${styles["menu"]} 
        ${menuIsActive[index] && styles["menu-active"]} 
        ${menuIsVisible[index] && styles["menu-visible"]} 
        ${styles[(index === 1 ? "right" : "left") + "-side"]}`}
        >
          {/* for every menuItem calls the menuItem component */}
          {menuItemJSX(option)}
        </div>
      )
    );
  };

  const navbarOptionJSX = (option: Option, index: number) => (
    <div className={styles["option-container"]}>
      <div
        className={`${styles["option"]}`}
        // apply animations and activate the menu when mouse enters
        onMouseEnter={() => handleOptionMouseEnter(option, index)}
        // apply animations and deactivate the menu when clicked (for touch devices)
        onClick={handleOptionClick(option, index)}
      >
        {/* Icon */}
        {optionIconJSX(option, index)}

        {/* **Menu**
        If the option has menu items, show the menu */}
        {menuItemsJSX(option, index)}
      </div>
    </div>
  );

  const navJSX = options && (
    <div
      className={`${styles["nav-bar"]} ${
        elevated === true ? styles["elevated"] : ""
      }`}
    >
      {
        // for each option, show a nav bar option
        options.map((option, index) => (
          <div key={index}>
            {/* A menu background for every option with menu */}
            {menuBackgroundJSX(option, index)}

            {/*  Option: if it needs login, show a login button.  else, show the intended option*/}
            {option.needsLogin && !userIsAuthenticated
              ? navbarLoginBtnJSX
              : navbarOptionJSX(option, index)}
          </div>
        ))
      }
    </div>
  );

  return navJSX;
}
