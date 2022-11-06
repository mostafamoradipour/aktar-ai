import Head from "next/head";
import Layout from "@/components/general/layout";
import { servicesItemsAtom } from "@/components/utilities/data/nav-bar-options";
import { useRecoilState } from "recoil";
import LiveChart from "@/components/data-analytics/live-chart";

export default function DataAnalytics() {
  const [servicesItems] = useRecoilState(servicesItemsAtom);

  const navBarOptions = [
    {
      name: "Our Services",
      icon: "donut_large",
      menuItems: servicesItems
    },
    {
      name: "Tools",
      icon: "settings",
      menuItems: [
        {
          href: "#",
          icon: "schedule",
          description: "minute",
          deactivated: true
          // comingSoon: true,
        },
        {
          href: "#",
          icon: "schedule",
          description: "hour",
          deactivated: true
        },
        {
          href: "#",
          icon: "schedule",
          description: "day",
          deactivated: true
        },
        {
          href: "#",
          icon: "schedule",
          description: "week",
          deactivated: true
        },
        {
          href: "#",
          icon: "schedule",
          description: "month",
          deactivated: true
        },
        {
          href: "#",
          icon: "schedule",
          description: "year",
          deactivated: true
        },
      ],
    },
  ];

  return (
    <div className="data-analytics">
      <Head>
        <title>Lea Mech Data Analytics system</title>
      </Head>

      <Layout type="home" navBarOptions={navBarOptions} elevatedNavBar>
        <LiveChart />
      </Layout>
    </div>
  );
}
