/* global d3 */

const DEMO = Boolean(window.DASHBOARD_DEMO);
const API_URL = "/api/metrics";
const POLL_INTERVAL = 5000;
const MAX_POINTS = 30;

const state = {
  cpu: [],
  mem: [],
  disk: [],
  load: [],
  lastTimestamp: null,
  demoTick: 0,
};

const elements = {
  host: document.getElementById("host"),
  cpuValue: document.getElementById("cpu-value"),
  memValue: document.getElementById("mem-value"),
  diskValue: document.getElementById("disk-value"),
  loadValue: document.getElementById("load-value"),
  statusText: document.getElementById("status-text"),
  statusIndicator: document.getElementById("status-indicator"),
  timestamp: document.getElementById("timestamp"),
  serviceList: document.getElementById("service-list"),
  serviceMeta: document.getElementById("service-meta"),
  serviceBlock: document.getElementById("service-block"),
  toggleSize: document.getElementById("toggle-size"),
  toggleDemo: document.getElementById("toggle-demo"),
};

const formatPercent = (value) => `${Math.round(value * 100)}%`;
const formatBytes = (bytes) => {
  if (!bytes) return "--";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let idx = 0;
  let size = bytes;
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx += 1;
  }
  return `${size.toFixed(1)} ${units[idx]}`;
};

const chartSize = (selector) => {
  const node = d3.select(selector).node();
  const { width, height } = node.getBoundingClientRect();
  return { width, height };
};

const updateSparkline = (selector, data, color) => {
  const { width, height } = chartSize(selector);
  const svg = d3.select(selector);
  svg.selectAll("*").remove();

  const x = d3.scaleLinear().domain([0, MAX_POINTS - 1]).range([0, width]);
  const y = d3.scaleLinear().domain([0, 1]).range([height, 0]);

  const line = d3
    .line()
    .x((d, i) => x(i))
    .y((d) => y(d))
    .curve(d3.curveCatmullRom.alpha(0.6));

  svg
    .append("path")
    .attr("d", line(data))
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", 2.2);

  svg
    .append("path")
    .attr("d", line(data.concat([data[data.length - 1]])))
    .attr("fill", color)
    .attr("opacity", 0.12)
    .attr(
      "d",
      `${line(data)} L ${width},${height} L 0,${height} Z`
    );
};

const updateDonut = (selector, value, color) => {
  const { width, height } = chartSize(selector);
  const radius = Math.min(width, height) / 2 - 4;
  const svg = d3.select(selector);
  svg.selectAll("*").remove();

  const g = svg
    .append("g")
    .attr("transform", `translate(${width / 2}, ${height / 2})`);

  const arc = d3.arc().innerRadius(radius * 0.6).outerRadius(radius);

  g.append("path")
    .datum({ startAngle: 0, endAngle: 2 * Math.PI })
    .attr("d", arc)
    .attr("fill", "#efe9e1");

  g.append("path")
    .datum({ startAngle: 0, endAngle: 2 * Math.PI * value })
    .attr("d", arc)
    .attr("fill", color);
};

const updateBars = (selector, values, color) => {
  const { width, height } = chartSize(selector);
  const svg = d3.select(selector);
  svg.selectAll("*").remove();

  const x = d3.scaleBand().domain([0, 1, 2]).range([0, width]).padding(0.3);
  const y = d3.scaleLinear().domain([0, Math.max(...values, 1)]).range([height, 0]);

  svg
    .selectAll("rect")
    .data(values)
    .enter()
    .append("rect")
    .attr("x", (_, i) => x(i))
    .attr("y", (d) => y(d))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d))
    .attr("rx", 4)
    .attr("fill", color);
};

const updateServices = (services = []) => {
  elements.serviceList.innerHTML = "";
  if (!services.length) {
    elements.serviceMeta.textContent = "Unconfigured";
    elements.serviceList.innerHTML =
      '<li class="service__item"><span>Set FRIDAY_SERVICES</span><span>--</span></li>';
    return;
  }
  elements.serviceMeta.textContent = `${services.length} checks`;
  services.forEach((service) => {
    const item = document.createElement("li");
    item.className = "service__item";
    const name = document.createElement("span");
    name.textContent = service.name;
    const status = document.createElement("span");
    status.textContent = service.ok
      ? `${service.latency_ms}ms`
      : "down";
    status.style.color = service.ok ? "#1a7f7a" : "#c94b3f";
    item.appendChild(name);
    item.appendChild(status);
    elements.serviceList.appendChild(item);
  });
};

const pushValue = (arr, value) => {
  if (typeof value !== "number") return;
  arr.push(value);
  if (arr.length > MAX_POINTS) arr.shift();
};

const padSeries = (arr) => {
  if (!arr.length) return Array(MAX_POINTS).fill(0);
  if (arr.length < MAX_POINTS) {
    return Array(MAX_POINTS - arr.length).fill(arr[0]).concat(arr);
  }
  return arr;
};

const render = (payload) => {
  if (payload.host && elements.host) {
    elements.host.textContent = payload.host;
  }

  const cpuUsage = payload.cpu?.usage ?? 0;
  const memUsage = payload.memory?.usage ?? 0;
  const diskUsage = payload.disk?.usage ?? 0;
  const load = payload.load || { "1m": 0, "5m": 0, "15m": 0 };

  elements.cpuValue.textContent =
    payload.cpu?.usage == null ? "--" : formatPercent(cpuUsage);
  elements.memValue.textContent =
    payload.memory == null
      ? "--"
      : `${formatPercent(memUsage)} / ${formatBytes(
          (payload.memory.total_kb || 0) * 1024
        )}`;
  elements.diskValue.textContent =
    payload.disk == null
      ? "--"
      : `${formatPercent(diskUsage)} / ${formatBytes(
          payload.disk.total_bytes || 0
        )}`;
  elements.loadValue.textContent = `${load["1m"].toFixed(2)} / ${load[
    "5m"
  ].toFixed(2)} / ${load["15m"].toFixed(2)}`;

  pushValue(state.cpu, cpuUsage);
  pushValue(state.mem, memUsage);
  pushValue(state.disk, diskUsage);
  pushValue(state.load, load["1m"] / 4);

  updateSparkline("#cpu-spark", padSeries(state.cpu), "#f08b3e");
  updateSparkline("#mem-spark", padSeries(state.mem), "#1a7f7a");
  updateDonut("#disk-donut", diskUsage, "#2b4d66");
  updateBars(
    "#load-bars",
    [load["1m"], load["5m"], load["15m"]],
    "#5f5d7a"
  );

  updateServices(payload.services);

  elements.timestamp.textContent = new Date(payload.timestamp * 1000).toLocaleTimeString();
};

const setStatus = (online, message) => {
  elements.statusIndicator.classList.toggle("status--offline", !online);
  elements.statusText.textContent = message;
};

const fetchMetrics = async () => {
  if (DEMO) {
    state.demoTick += 1;
    const wobble = (seed) => (Math.sin(state.demoTick / 4 + seed) + 1) / 2;
    return {
      timestamp: Date.now() / 1000,
      host: "demo-node",
      cpu: { usage: 0.2 + 0.6 * wobble(1) },
      memory: { usage: 0.3 + 0.5 * wobble(2), total_kb: 32768000 },
      disk: { usage: 0.5 + 0.3 * wobble(3), total_bytes: 512000000000 },
      load: {
        "1m": 0.2 + 1.4 * wobble(4),
        "5m": 0.15 + 1.1 * wobble(5),
        "15m": 0.1 + 0.9 * wobble(6),
      },
      services: [
        { name: "elasticsearch", ok: wobble(1) > 0.2, latency_ms: 28 },
        { name: "k8s-api", ok: wobble(2) > 0.3, latency_ms: 52 },
      ],
    };
  }

  const response = await fetch(API_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Metrics fetch failed");
  }
  return response.json();
};

const tick = async () => {
  try {
    const data = await fetchMetrics();
    render(data);
    setStatus(true, DEMO ? "Demo feed" : "Live");
  } catch (error) {
    setStatus(false, "Offline");
  }
};

const init = () => {
  if (elements.toggleSize) {
    elements.toggleSize.addEventListener("click", () => {
      const compact = document
        .getElementById("dashboard")
        .getAttribute("data-compact")
        .toLowerCase();
      const next = compact !== "true";
      document.getElementById("dashboard").setAttribute("data-compact", next);
      elements.toggleSize.textContent = next ? "Expand" : "Compact";
      setTimeout(() => tick(), 0);
    });
  }

  if (elements.toggleDemo) {
    elements.toggleDemo.addEventListener("click", () => {
      if (DEMO) {
        window.location.href = "/";
      } else {
        window.location.href = "/demo.html";
      }
    });
  }

  tick();
  setInterval(tick, POLL_INTERVAL);
};

window.addEventListener("load", init);
