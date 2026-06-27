const chartConfig = { displaylogo: false, responsive: true };

function getValue(id) {
  const element = document.getElementById(id);
  return element ? element.value : "";
}

function setText(id, text) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = text;
  }
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

async function drawChart(elementId, url) {
  const element = document.getElementById(elementId);
  if (!element) {
    return;
  }
  element.classList.add("loading");
  element.textContent = "Loading...";
  try {
    const payload = await fetchJson(url);
    const figure = payload.figure || {};
    element.textContent = "";
    await Plotly.react(element, figure.data || [], figure.layout || {}, chartConfig);
  } catch (error) {
    Plotly.purge(element);
    element.textContent = error.message;
  } finally {
    element.classList.remove("loading");
  }
}

function bindChange(ids, handler) {
  ids.forEach((id) => {
    const element = document.getElementById(id);
    if (element) {
      element.addEventListener("change", handler);
    }
  });
}

function initHome() {
  const render = () => {
    const baseDate = getValue("home-base-date");
    const demandField = getValue("home-demand-field");
    drawChart("home-price-chart", `/api/v1/charts/home/price?base_date=${baseDate}`);
    drawChart("home-demand-chart", `/api/v1/charts/home/demand?base_date=${baseDate}&field=${demandField}`);
  };
  bindChange(["home-base-date", "home-demand-field"], render);
  render();
}

function initBalance() {
  const render = () => {
    const baseDate = getValue("balance-base-date");
    const area = getValue("balance-area");
    drawChart("balance-price-chart", `/api/v1/charts/balance/price?base_date=${baseDate}`);
    drawChart("balance-supply-chart", `/api/v1/charts/balance/supply?base_date=${baseDate}&area=${area}`);
  };
  bindChange(["balance-base-date", "balance-area"], render);
  render();
}

function initTrend() {
  const render = () => {
    const baseDate = getValue("trend-base-date");
    const spotType = getValue("trend-spot-type");
    const area = getValue("trend-area");
    drawChart("trend-spot-chart", `/api/v1/charts/trend/spot?base_date=${baseDate}&spot_type=${spotType}`);
    drawChart("trend-supply-chart", `/api/v1/charts/trend/supply?base_date=${baseDate}&area=${area}`);
  };
  bindChange(["trend-base-date", "trend-spot-type", "trend-area"], render);
  render();
}

function tableHtml(rows) {
  if (!rows.length) {
    return "対象期間のデータがありません。";
  }
  const columns = Object.keys(rows[0]);
  const head = columns.map((column) => `<th>${column}</th>`).join("");
  const body = rows
    .map((row) => {
      const cells = columns.map((column) => `<td>${row[column] ?? ""}</td>`).join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");
  return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

function updateCsvLink() {
  const begin = getValue("download-start-date");
  const end = getValue("download-end-date");
  const link = document.getElementById("download-csv-link");
  if (link) {
    link.href = `/api/v1/export/spot-prices.csv?begin=${begin}&end=${end}`;
  }
}

function initDownload() {
  const button = document.getElementById("download-load-button");
  const load = async () => {
    const begin = getValue("download-start-date");
    const end = getValue("download-end-date");
    updateCsvLink();
    setText("download-table-container", "Loading...");
    try {
      const rows = await fetchJson(`/api/v1/spot-prices?begin=${begin}&end=${end}`);
      document.getElementById("download-table-container").innerHTML = tableHtml(rows);
    } catch (error) {
      setText("download-table-container", error.message);
    }
  };
  bindChange(["download-start-date", "download-end-date"], updateCsvLink);
  if (button) {
    button.addEventListener("click", load);
  }
  updateCsvLink();
}

function initPublishApiUrl() {
  const button = document.getElementById("api-url-button");
  const container = document.getElementById("api-url-container");
  if (!button || !container) {
    return;
  }
  button.addEventListener("click", async () => {
    const begin = getValue("api-start-date");
    const end = getValue("api-end-date");
    const url = `${window.location.origin}/api/v1/spot-prices?begin=${begin}&end=${end}`;
    container.innerHTML = `
      <div class="generated-url">
        <span>API Endpoint</span>
        <code id="generated-api-url">${url}</code>
        <button id="copy-api-url" class="secondary-button" type="button">コピー</button>
      </div>
    `;
    document.getElementById("copy-api-url").addEventListener("click", async () => {
      await navigator.clipboard.writeText(url);
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  if (page === "home") {
    initHome();
  } else if (page === "balance") {
    initBalance();
  } else if (page === "trend") {
    initTrend();
  } else if (page === "download") {
    initDownload();
  } else if (page === "publishapiurl") {
    initPublishApiUrl();
  }
});
