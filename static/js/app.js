document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".btn.primary").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.style.transform = "scale(.98)";
      setTimeout(() => btn.style.transform = "", 120);
    });
  });
});