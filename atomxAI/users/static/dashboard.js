document.addEventListener("DOMContentLoaded", function () {
  const allSideMenu = document.querySelectorAll("#sidebar .side-menu.top li a");
  const dashboardContent = document.getElementById("dashboard-content"); // Dashboard section
  const createExamRoomContent = document.getElementById("create-exam-room-content"); // Create Exam Room section
  const manageStudentContent = document.getElementById("manage-student-content"); // Manage Student section
  const logReportsContent = document.getElementById("log-reports-content"); // log reports content section

  // Handle sidebar menu clicks
  allSideMenu.forEach((item) => {
    const li = item.parentElement;

    item.addEventListener("click", function () {
      allSideMenu.forEach((i) => {
        i.parentElement.classList.remove("active");
      });
      li.classList.add("active");

      // Switch content based on sidebar item clicked
      if (item.innerText.includes("Create Exam Room")) {
        dashboardContent.style.display = "none";
        createExamRoomContent.style.display = "block";
        manageStudentContent.style.display = "none";
        logReportsContent.style.display = "none";
      } else if (item.innerText.includes("Dashboard")) {
        createExamRoomContent.style.display = "none";
        dashboardContent.style.display = "block";
        manageStudentContent.style.display = "none";
        logReportsContent.style.display = "none";
      } else if (item.innerText.includes("Manage Students")) {
        createExamRoomContent.style.display = "none";
        dashboardContent.style.display = "none";
        manageStudentContent.style.display = "block";
        logReportsContent.style.display = "none";
      } else if (item.innerText.includes("Logs and Reports")) {
        createExamRoomContent.style.display = "none";
        dashboardContent.style.display = "none";
        manageStudentContent.style.display = "none";
        logReportsContent.style.display = "block";
      }
    });
  });

  // HANDLE WINDOW RESIZE 
  if (window.innerWidth < 768) {
    sidebar.classList.add("hide");
  } else if (window.innerWidth > 576) {
    if (searchButtonIcon) {
      searchButtonIcon.classList.replace("bx-x", "bx-search");
    }
    if (searchForm) {
      searchForm.classList.remove("show");
    }
  }

  window.addEventListener("resize", function () {
    if (this.innerWidth > 576) {
      if (searchButtonIcon) {
        searchButtonIcon.classList.replace("bx-x", "bx-search");
      }
      if (searchForm) {
        searchForm.classList.remove("show");
      }
    }
  });
});
