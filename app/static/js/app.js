document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggle = document.getElementById("sidebar-toggle");
  const icon = document.getElementById("sidebar-toggle-icon");

  if (!sidebar || !toggle || !icon) {
    return;
  }

  toggle.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    icon.textContent = sidebar.classList.contains("collapsed") ? "›" : "‹";
  });
});
