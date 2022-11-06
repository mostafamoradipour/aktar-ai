import Reactm, { useEffect, useRef, useState } from "react";
import Head from "next/head";
import Layout from "@/components/general/layout";
import { Line } from "react-chartjs-2";
// import { Chart, registerables } from "chart.js";
import { Chart as ChartJs } from "chart.js/auto";
import { userLogInAtom } from "@/components/utilities/atoms";
import { useRecoilState } from "recoil";
import { useRouter } from 'next/router'
import axios from "axios";
import gsap from "gsap";
import { useCookies } from "react-cookie";


export default function DataAnalytics() {
  const [chartWidth, setChartWidth] = useState(100);
  const [chartHeight, setChartHeight] = useState(100);
  const [chartData, setChartData] = useState([]);
  const [cookies, setCookie] = useCookies(["loggedIn"]);
  const [showChart, setShowChart] = useState(false);

  const [userIsAuthenticated, setUserIsAuthenticated] =
    useRecoilState(userLogInAtom);

  const chartRef = useRef();
  const router = useRouter()
  // const { uuid } = router.query

  const chartDatasets = {

    labels: Array(33).fill().map((_, i) => i + 1 + "s"),
    datasets: [
      {
        label: "Human Count",
        fill: "stack",
        backgroundColor(context) {
          // console.log(chartRef?.current?.height);
          let grad = context.chart.ctx.createLinearGradient(
            0,
            0,
            0,
            chartRef?.current?.height || 0
          );

          grad.addColorStop(0, "rgba(255, 203, 82, 1)");
          grad.addColorStop(1, "rgba(238, 191, 130, 0)");

          return grad;
        },
        borderCapStyle: "round",
        // stepped:true,
        borderColor: "rgba(255, 203, 82, 0.5)",
        // borderCapStyle: "butt",
        // borderDash: [],
        // borderDashOffset: 0.0,
        // borderJoinStyle: "miter",
        // pointBorderColor: "rgba(75,192,192,1)",
        // pointBackgroundColor: "#fff",
        // pointBorderWidth: 1,
        // pointHoverRadius: 5,
        // pointHoverBackgroundColor: "rgba(75,192,192,1)",
        // pointHoverBorderColor: "rgba(220,220,220,1)",
        // pointHoverBorderWidth: 2,
        // line tension
        tension: 0.15,
        pointRadius: 0,
        pointHitRadius: 10,
        data: chartData
      },
    ],
  };

  useEffect(() => {
    window ? setChartHeight(window.innerHeight) : "";
  }, []);

  useEffect(() => {
    async function fetchChartData() {

      let res = await axios
        .get("https://api.kachrobotics.com/api/user/set_csrf_cookie/", {
          withCredentials: true,
        })
      const bodyFormData = new FormData();
      bodyFormData.append(
        "csrfmiddlewaretoken",
        res.data["csrfmiddlewaretoken"]
      );

      try {
        let response = await axios({
          method: "get",
          url: "https://api.kachrobotics.com/api/user/get_analytics_data/",
          data: bodyFormData,
          headers: { "Content-Type": "multipart/form-data" },
          withCredentials: true,
        })
        console.log("chart:", response.data);
        if (response.data.data === "no_data") {
          setChartData([]);
        }
        else {
          const data = response.data.data.map((item) => item.count)
          setChartData(data);
          chartRef.current.update();
        }
      }
      catch (error) {
      };
    }
    fetchChartData();
  }, []);

  console.log('component')

  // if (registerables) {
  //   Chart.register(...registerables);
  // }

  const navBarOptions = [
    {
      name: "Account",
      icon: "fingerprint",
      needsLogin: true,
      menuItems: [
        {
          icon: "dashboard",
          description: "dashboard",
          onClick: () => {
            router.push("/dashboard");
          },
        },
        {
          href: "/camera",
          icon: "videocam",
          description: "Camera",
        },
        {
          icon: userIsAuthenticated ? "logout" : "login",
          description: userIsAuthenticated ? "Log Out" : "Log in",
          onClick: async () => {
            let csrf = await axios.get(
              "https://api.kachrobotics.com/api/user/set_csrf_cookie/",
              {
                withCredentials: true,
              }
            );
            const formData = new FormData();
            formData.append(
              "csrfmiddlewaretoken",
              csrf.data.csrfmiddlewaretoken
            );
            const res = await axios({
              method: "post",
              url: "https://api.kachrobotics.com/api/user/logout/",
              data: formData,
              headers: { "Content-Type": "multipart/form-data" },
              withCredentials: true,
            });
            // console.log(res);
            if (res.status === 200) {
              // TODO - Write recoil selector to automatically set cookies with this action
              setCookie("loggedIn", false, { path: "/" });
              setUserIsAuthenticated(false);

              router.push("/");
            }
          },
        },
      ],
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



  // useEffect(() => {
  //   if (chartData.length === 0) {
  //     console.log('data 0', chartData);
  //     setChart``
  //   }
  //   else {

  //     chartRef?.current?.update();
  //   }
  //   console.log('chart Changed', chartData);
  // }, [chartData]);

  return (
    <div className="data-analytics">
      <Head>
        <title>Lea Mech Data Analytics system</title >
      </Head >

      <Layout type="home" navBarOptions={navBarOptions} elevatedNavBar>
        {showChart ? ((<h1 className="content">No data is associated with your account</h1>)) :
          (
            <div className='chart-container'>
              <Line
                // height={chartHeight}
                ref={chartRef}
                datasetIdKey="id"
                data={chartDatasets}
                options={{
                  // TODO - Wrap a container around this and make it the size reference
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    yAxis: {
                      display: false,
                      min: 0,
                      // max: 7,
                    },
                    xAxis: {
                      display: false,
                    },
                  },
                  plugins: {
                    legend: {
                      display: false,
                    },
                  },
                  interaction: {
                    // mode: "nearest",
                    intersect: false,
                    // mode: "x",
                    mode: "nearest",
                    axis: "x",
                  },
                }}
              />
            </div>
          )
        } /
      </Layout >
    </div >
  )
}