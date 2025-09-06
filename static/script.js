// --- Configuration ---
const FLASH_AUTOHIDE_DELAY = 5000;

function hideAlert() {
  const alertContainer = document.querySelector("#global-alert-container");
  if (alertContainer) {
    alertContainer.innerHTML = "";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Flash Message Auto-Hide
  const flashMessageElement = document.querySelector(".flask-flash-message");
  if (flashMessageElement) {
    setTimeout(() => {
      hideAlert();
    }, FLASH_AUTOHIDE_DELAY);
  }

  const redirectUrl = document.body.getAttribute("data-redirect-url");
  const delay = parseInt(document.body.getAttribute("data-redirect-delay"));

  if (redirectUrl && delay) {
    startApologyRedirect(redirectUrl, delay);
  }

  // Add password validation for forms that need it
  setupPasswordValidation(
    "registerForm",
    "register-password",
    "register-confirmation",
    "registerSubmitBtn",
  );
  setupPasswordValidation(
    "passwordForm",
    "change-password",
    "change-confirmation",
    "changeSubmitBtn",
  );
});

// Add password validation for forms that need it
function setupPasswordValidation(
  formId,
  passwordId,
  confirmationId,
  submitBtnId,
) {
  const form = document.querySelector(`#${formId}`);
  if (!form) return;

  const password = document.querySelector(`#${passwordId}`);
  const confirmation = document.querySelector(`#${confirmationId}`);
  const submitBtn = document.querySelector(`#${submitBtnId}`);

  function validatePasswords() {
    const passwordValue = password.value;
    const confirmationValue = confirmation.value;

    if (confirmationValue === "") {
      hideAlert();
      submitBtn.disabled = false;
      return true;
    }

    if (passwordValue !== confirmationValue) {
      showAlert("Passwords do not match!");
      submitBtn.disabled = true;
      return false;
    } else {
      hideAlert();
      submitBtn.disabled = false;
      return true;
    }
  }

  confirmation.addEventListener("input", validatePasswords);
  password.addEventListener("input", validatePasswords);
}

// Generic form reset function
function resetAllForms() {
  const resultContainers = document.querySelectorAll('[id$="Result"]');
  resultContainers.forEach((container) => {
    container.style.display = "none";
  });

  const formContainers = document.querySelectorAll('[id$="Form"]');
  formContainers.forEach((container) => {
    container.style.display = "block";
    const inputs = container.querySelectorAll(
      'input[type="text"], input[type="number"]',
    );
    inputs.forEach((input) => {
      if (
        input.name !== "username" &&
        input.name !== "password" &&
        input.name !== "confirmation"
      ) {
        input.value = "";
      }
    });
  });

  hideAlert();
}

// Event delegation for all "show form" buttons
document.addEventListener("click", function (event) {
  if (event.target.closest(".show-form-btn")) {
    event.preventDefault();
    resetAllForms();
  }
});

// Global alert functions
function showAlert(message, type = "danger") {
  const alertContainer = document.querySelector("#global-alert-container");
  if (!alertContainer) return;

  alertContainer.innerHTML = "";
  const alertElement = document.createElement("div");
  alertElement.className = `alert alert-${type} alert-dismissible fade show`;
  alertElement.role = "alert";
  alertElement.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  alertContainer.appendChild(alertElement);
}

// Apology redirect functionality
function startApologyRedirect(redirectUrl, delay) {
  // Only run if we have both parameters
  if (!redirectUrl || !delay) return;

  let timeLeft = delay;
  const countdownElement = document.getElementById("countdown");

  // Update countdown display
  const timer = setInterval(() => {
    timeLeft--;
    if (countdownElement) {
      countdownElement.textContent = timeLeft;
    }

    if (timeLeft <= 0) {
      clearInterval(timer);
      window.location.href = redirectUrl;
    }
  }, 1000);
}
