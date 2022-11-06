import dynamic from "next/dynamic";
const NonSSRWrapper = ({ children }: { children: JSX.Element }) => (
  <>{children}</>
);
export default dynamic(() => Promise.resolve(NonSSRWrapper), {
  ssr: false,
});
