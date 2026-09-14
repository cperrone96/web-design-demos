/*
 * Demo-only form behavior. The handler prevents navigation and network
 * submission, validates with the browser's native constraints, and shows a
 * local confirmation. Production sites should replace this with an approved
 * form processor and privacy/consent implementation.
 */
(function () {
  "use strict";

  document.querySelectorAll("form[data-demo-form]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (!form.reportValidity()) return;

      var status = document.getElementById(form.dataset.demoStatus);
      if (status) {
        status.hidden = false;
        status.textContent =
          "Demo only: no information was sent or stored. A production deployment would connect this form to an owner-approved workflow.";
        status.focus();
      }
      form.reset();
    });
  });
})();
