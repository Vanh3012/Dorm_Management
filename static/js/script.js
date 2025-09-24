document.addEventListener("DOMContentLoaded", () => {
  // Auto-close sau 3 giây
  setTimeout(() => {
    document.querySelectorAll(".flash").forEach(f => f.remove());
  }, 3000);

  // Bấm nút X thì đóng
  document.querySelectorAll(".flash-close").forEach(btn => {
    btn.addEventListener("click", e => {
      e.target.closest(".flash").remove();
    });
  });
});
