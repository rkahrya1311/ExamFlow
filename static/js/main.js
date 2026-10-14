/**
 * ExamFlow Frontend Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Modal Trigger Logic
  document.querySelectorAll("[data-modal-target]").forEach((trigger) => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = trigger.getAttribute("data-modal-target");
      const modal = document.getElementById(targetId);
      if (modal) {
        modal.classList.add("active");
      }
    });
  });

  document.querySelectorAll(".modal-close, [data-modal-close]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".modal-overlay").forEach((m) => m.classList.remove("active"));
    });
  });

  window.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal-overlay")) {
      e.target.classList.remove("active");
    }
  });

  // 2. Classroom Visualizer Tab Switching
  const tabButtons = document.querySelectorAll(".room-tab-btn");
  const tabPanes = document.querySelectorAll(".room-tab-pane");

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabButtons.forEach((b) => b.classList.remove("active"));
      tabPanes.forEach((p) => (p.style.display = "none"));

      btn.classList.add("active");
      const targetRoomId = btn.getAttribute("data-room-target");
      const targetPane = document.getElementById(`room-pane-${targetRoomId}`);
      if (targetPane) {
        targetPane.style.display = "block";
      }
    });
  });

  // 3. Dynamic Capacity Calculator on Classroom Form
  const rowsInput = document.getElementById("room-rows");
  const colsInput = document.getElementById("room-cols");
  const capacityPreview = document.getElementById("capacity-preview");

  function updateCapacityPreview() {
    if (rowsInput && colsInput && capacityPreview) {
      const r = parseInt(rowsInput.value, 10) || 0;
      const c = parseInt(colsInput.value, 10) || 0;
      const benches = r * c;
      const seats = benches * 2;
      capacityPreview.textContent = `${benches} benches (${seats} student seats: Left & Right)`;
    }
  }

  if (rowsInput && colsInput) {
    rowsInput.addEventListener("input", updateCapacityPreview);
    colsInput.addEventListener("input", updateCapacityPreview);
  }

  // 4. File Dropzone filename display
  const fileInput = document.getElementById("csv-file-input");
  const dropzoneText = document.getElementById("dropzone-text");

  if (fileInput && dropzoneText) {
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length > 0) {
        dropzoneText.textContent = `Selected: ${fileInput.files[0].name} (${(fileInput.files[0].size / 1024).toFixed(1)} KB)`;
      }
    });
  }

  // 5. Auto dismiss flash alerts after 6 seconds
  setTimeout(() => {
    document.querySelectorAll(".alert").forEach((alert) => {
      alert.style.transition = "opacity 0.4s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 400);
    });
  }, 6000);
});
