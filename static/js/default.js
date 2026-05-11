const Toast = Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  didOpen: (toast) => {
    toast.addEventListener('mouseenter', Swal.stopTimer);
    toast.addEventListener('mouseleave', Swal.resumeTimer);
  },
});

/**
 * Show a toast notification (toastr style)
 * @param {string} message - Notification text
 * @param {string} type - 'success'|'error'|'warning'|'info'
 */
function showNotificationToastr(message, type = 'info') {
  let icon = 'info';
  switch (type) {
    case 'success':
      icon = 'success';
      break;
    case 'error':
      icon = 'error';
      break;
    case 'warning':
      icon = 'warning';
      break;
    case 'info':
    default:
      icon = 'info';
      break;
  }

  Toast.fire({
    icon: icon,
    title: message,
  });
}

/**
 * Show a modal popup notification
 * @param {string} message - Notification text
 * @param {string} type - 'success'|'error'|'warning'|'info'
 * @param {string|null} redirectUrl - Optional URL to redirect on success
 */
function showNotificationPopup(message, type = 'info', redirectUrl = null) {
  let icon = 'info';
  let title = '';
  let confirmButtonText = 'OK';

  switch (type) {
    case 'success':
      icon = 'success';
      title = 'Success!';
      break;
    case 'error':
      icon = 'error';
      title = 'Error!';
      break;
    case 'warning':
      icon = 'warning';
      title = 'Warning!';
      break;
    case 'info':
    default:
      icon = 'info';
      title = 'Info';
      break;
  }

  Swal.fire({
    icon: icon,
    title: title,
    text: message,
    confirmButtonText: confirmButtonText,
    allowOutsideClick: false,
  }).then((result) => {
    if (result.isConfirmed && type === 'success' && redirectUrl) {
      window.location.href = redirectUrl;
    }
  });
}

/**
 * Show a confirmation prompt before performing an action (e.g., delete, logout, etc.)
 *
 * @param {string} action          - The action type (e.g., 'delete', 'logout', etc.)
 * @param {string} actionUrl       - The URL to perform the action (e.g., the delete endpoint)
 * @param {string} redirectUrl     - The URL to redirect to after the action is performed
 * @param {string} method          - The HTTP method to use (e.g., 'GET', 'POST', 'DELETE')
 * @param {string} notifyMode      - 'popup' or 'toast' (how success/error is shown)
 */
function confirmAction(action, actionUrl, redirectUrl, method = 'POST', notifyMode = 'popup') {
  let title = '';
  let message = '';

  switch (action) {
    case 'delete':
      title = 'Are you sure?';
      message = 'This action cannot be undone!';
      break;
    case 'logout':
      title = 'Log out?';
      message = 'You will be signed out of your account.';
      break;
    default:
      title = 'Confirm action';
      message = 'Are you sure you want to proceed?';
      break;
  }

  Swal.fire({
    title: title,
    text: message,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    reverseButtons: true,
    allowOutsideClick: false,
  }).then((result) => {
    if (result.isConfirmed) {
      performAction(actionUrl, redirectUrl, method, notifyMode);
    }
  });
}

/**
 * Perform the action (e.g., delete, logout, etc.)
 *
 * @param {string} actionUrl     - The URL endpoint to trigger the action
 * @param {string} redirectUrl   - The URL to redirect to after the action
 * @param {string} method        - HTTP method: 'GET', 'POST', 'DELETE', etc.
 * @param {string} notifyMode    - 'popup' or 'toast' (how feedback is shown)
 */
function performAction(actionUrl, redirectUrl, method = 'POST', notifyMode = 'popup') {
  console.log(actionUrl, redirectUrl, method);

  fetch(actionUrl, { method: method })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      const msg = data.message || 'Operation completed.';

      if (data.status || data.success) {
        if (notifyMode === 'toast') {
          showNotificationToastr(msg, 'success');
          if (redirectUrl) {
            window.location.href = redirectUrl;
          }
        } else {
          showNotificationPopup(msg, 'success', redirectUrl);
        }
      } else {
        const errorMsg = data.message || 'Operation failed.';
        if (notifyMode === 'toast') {
          showNotificationToastr(errorMsg, 'error');
        } else {
          showNotificationPopup(errorMsg, 'error');
        }
      }
    })
    .catch((error) => {
      const errorMsg = 'Something went wrong, please try again later.';
      if (notifyMode === 'toast') {
        showNotificationToastr(errorMsg, 'error');
      } else {
        showNotificationPopup(errorMsg, 'error');
      }
    });
}