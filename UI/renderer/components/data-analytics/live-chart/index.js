import React, { useEffect, useRef, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJs } from "chart.js/auto";
// import { Chart, registerables } from "chart.js";
import axios from "axios";

function LiveChart() {
  const [chartWidth, setChartWidth] = useState(100);
  const [chartHeight, setChartHeight] = useState(100);

  const chartRef = useRef();
  const [chartData, setChartData] = useState([]);

  const data = {
    labels: Array(0)
      .fill()
      .map((_, i) => i + 1 + "s"),
    datasets: [
      {
        label: "Human Count",
        fill: "stack",
        backgroundColor: (context) => {
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
        data: chartData,
      },
    ],
  };

  // if (registerables) {
  //   Chart.register(...registerables);
  // }

  useEffect(() => {
    const url = "wss://api.kachrobotics.com/ws2/graph/";
    // console.log(url);
    const socket = new WebSocket(url);

    window.addEventListener("unload", () => {
      socket.close();
    });

    // Connection opened
    socket.addEventListener("open", function (event) {
      // console.log("opened");
      // socket.send(JSON.stringify({ stat: "ok" }));
    });
    socket.addEventListener("message", function (event) {
      let value = JSON.parse(event.data).value || 0;
      let t = chartData;
      t.push(value);
      setChartData(t);
      if (chartRef.current?.config?.data?.labels) {
        chartRef.current.config.data.labels = Array(chartData.length)
          .fill()
          .map((_, i) => i + 1 + "s");
      }
      chartRef.current?.update();
    });

    return () => {
      socket.close();
    }
  }, []);

  useEffect(() => {
    window ? setChartHeight(window.innerHeight) : "";
  }, []);

  return (
    <div className="chart-container">
      <Line
        // height={chartHeight}
        ref={chartRef}
        datasetIdKey="id"
        data={data}
        options={{
          // TODO - Wrap a container around this and make it the size reference
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            yAxis: {
              display: false,
              // min: 0,
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
          // animation: false
        }}
      />
    </div>
  );
}

export default React.memo(LiveChart);
