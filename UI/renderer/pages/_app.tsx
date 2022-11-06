import "../styles/global.scss";
// import "video.js/dist/video-js.css";
import { RecoilRoot } from "recoil";
import RecoilNexus from "recoil-nexus";
import { CookiesProvider } from "react-cookie";
import Head from "next/head";

export default function App({ Component, pageProps }) {

  return (
    <>
      <Head>
        <meta name="theme-color" content="#fff" />
        <meta name="viewport" content="initial-scale=1, width=device-width" />
      </Head>
      <CookiesProvider>
        <RecoilRoot>
          <RecoilNexus />
          <Component {...pageProps} />
        </RecoilRoot>
      </CookiesProvider>
    </>
  );
}
