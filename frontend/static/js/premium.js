

document.addEventListener('DOMContentLoaded', () => {
    
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    const timeDisplay = document.getElementById('current-time');
    const dateDisplay = document.getElementById('current-date');
    
    if (timeDisplay && dateDisplay) {
        function updateClock() {
            const now = new Date();
            timeDisplay.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            dateDisplay.textContent = now.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        }
        updateClock();
        setInterval(updateClock, 1000);
    }

    const flashMessages = document.querySelectorAll('.flash-msg');
    flashMessages.forEach(flash => {
        let type = 'info';
        if (flash.classList.contains('flash-success')) type = 'success';
        if (flash.classList.contains('flash-danger')) type = 'error';
        if (flash.classList.contains('flash-warning')) type = 'warning';

        const clone = flash.cloneNode(true);
        const closeBtn = clone.querySelector('.flash-close');
        if (closeBtn) closeBtn.remove();
        
        let msg = clone.textContent.trim();

        showToast(type, msg);

        flash.style.display = 'none';
    });

    const deleteForms = document.querySelectorAll('form[onsubmit*="return confirm"]');
    deleteForms.forEach(form => {
        
        form.removeAttribute('onsubmit');
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to revert this action!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#ef4444',
                cancelButtonColor: '#64748b',
                confirmButtonText: 'Yes, delete it!',
                customClass: {
                    popup: 'modal-pro',
                    confirmButton: 'btn-primary-sm',
                    cancelButton: 'btn-secondary-sm'
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    
                    Swal.fire({
                        title: 'Processing...',
                        text: 'Please wait',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading()
                        }
                    });
                    form.submit();
                }
            })
        });
    });
});

function showToast(type, message) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-pro ${type}`;
    
    let iconClass = 'fa-info-circle';
    let title = 'Notification';
    
    if (type === 'success') { iconClass = 'fa-check-circle'; title = 'Success'; }
    if (type === 'error') { iconClass = 'fa-exclamation-circle'; title = 'Error'; }
    if (type === 'warning') { iconClass = 'fa-exclamation-triangle'; title = 'Warning'; }

    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas ${iconClass}"></i>
        </div>
        <div class="toast-content">
            <span class="toast-title">${title}</span>
            <span class="toast-msg">${message}</span>
        </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        setTimeout(() => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 400); 
    }, 4000);
}
