import { atom, selector, useRecoilState, useRecoilValue } from "recoil";

export const userLogInAtom = atom({
  key: "user-state", // unique ID (with respect to other atoms/selectors)
  default: false, // default value (aka initial value)
});

export const showLoginModalAtom = atom({
  key: "login-modal",
  default: false,
});

export const showLoadingAtom = atom({
  key: "loading-state",
  default: true,
});

export const activeSceneOptionsAtom = atom({
  key: "active-scene-options",
  default: {
    topView: false,
    filteredView: false,
  },
});

export const sceneUtilsAtom = atom({
  key: "scene-utils",
  default: [],
});

export const csrfTokenAtom = atom({
  key: "csrf-token",
  default: {},
});

export const uuidAtom = atom({
  key: "uuid",
  default: "",
});

export const sceneInitializedAtom = atom({
  key: "scene-initialized",
  default: false,
});

export const sceneHumanData = atom({
  key: "scene-human-count",
  default: [{ count: 0, time: Date.now() }],
});

export const showAddCameraAtom = atom({
  key: "show-add-camera",
  default: false,
});

export const camerasAtom = atom({
  key: 'cameras',
  default: null
});
