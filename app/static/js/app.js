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

  document.querySelectorAll(".today-button").forEach((button) => {
    button.addEventListener("click", () => {
      const targetId = button.dataset.dateTarget;
      const target = document.getElementById(targetId);
      if (!target) {
        return;
      }
      target.value = button.dataset.today;
      target.dispatchEvent(new Event("change", { bubbles: true }));
    });
  });
});
