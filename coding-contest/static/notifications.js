// Notification system for real-time broadcasts and premium alerts
(function () {
    const containerId = 'notification-container';

    // Inject styles immediately
    const styleId = 'notification-styles';
    if (!document.getElementById(styleId)) {
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            @keyframes toastSlideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes modalFadeIn {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }
            .animate-toast-in {
                animation: toastSlideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }
            .animate-modal-in {
                animation: modalFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }
            .premium-toast {
                background: rgba(15, 23, 42, 0.95);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                margin-bottom: 12px;
                border-left: 4px solid var(--primary, #3b82f6);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
                display: flex;
                flex-direction: column;
                gap: 6px;
                min-width: 320px;
                max-width: 450px;
                pointer-events: auto;
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
            }
            .premium-modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.85); /* Slightly darker */
                backdrop-filter: blur(10px);
                z-index: 2000000;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .premium-modal {
                background: #1e293b;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                width: 100%;
                max-width: 500px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                color: white;
                overflow: hidden;
                position: relative;
            }
            .modal-header {
                padding: 20px 24px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .modal-body {
                padding: 24px;
                line-height: 1.6;
                font-size: 1rem;
                color: rgba(255, 255, 255, 0.9);
            }
            .modal-footer {
                padding: 16px 24px;
                background: rgba(0, 0, 0, 0.2);
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }
            .modal-btn {
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                border: none;
            }
            .modal-btn-primary {
                background: var(--primary, #3b82f6);
                color: white;
            }
            .modal-btn-primary:hover {
                filter: brightness(1.1);
                transform: translateY(-1px);
            }
            .cancel-btn {
                background: rgba(255,255,255,0.1);
                color: white;
            }
            .cancel-btn:hover {
                background: rgba(255,255,255,0.15);
            }
        `;
        document.head.appendChild(style);
    }

    function createContainer() {
        let container = document.getElementById(containerId);
        if (container) return container;

        container = document.createElement('div');
        container.id = containerId;
        container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            pointer-events: none;
        `;
        document.body.appendChild(container);
        return container;
    }

    // Expose global functions immediately
    window.showNotification = showNotification;
    window.showAlert = showAlert;
    window.showModal = showModal;

    function showNotification(data) {
        const container = createContainer();
        const toast = document.createElement('div');
        toast.className = 'premium-toast animate-toast-in';

        const timestamp = data.timestamp || new Date().toLocaleTimeString();
        const sender = data.sender || 'System';

        toast.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <strong style="color: var(--primary, #3b82f6); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;">Broadcast from ${sender}</strong>
                <span style="color: rgba(255,255,255,0.4); font-size: 0.65rem;">${timestamp}</span>
            </div>
            <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem; padding-right: 20px;">${data.message}</div>
            <button class="toast-close-btn" style="position: absolute; top: 12px; right: 12px; background: none; border: none; color: rgba(255,255,255,0.3); cursor: pointer; font-size: 1.4rem; line-height: 1; padding: 4px; display: flex; align-items: center; justify-content: center;">&times;</button>
        `;

        toast.querySelector('.toast-close-btn').onclick = () => removeToast(toast);

        container.appendChild(toast);
        setTimeout(() => removeToast(toast), 10000);
    }

    function showAlert(message, type = 'info') {
        const container = createContainer();
        const toast = document.createElement('div');
        toast.className = 'premium-toast animate-toast-in';

        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        toast.style.borderLeftColor = colors[type] || colors.info;

        toast.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <div style="flex: 1; color: rgba(255,255,255,0.95); font-weight: 500; font-size: 0.95rem; white-space: pre-line; padding-right: 10px;">${message}</div>
                <button class="toast-close-btn" style="background: none; border: none; color: rgba(255,255,255,0.3); cursor: pointer; font-size: 1.4rem; line-height: 0.8; padding: 4px;">&times;</button>
            </div>
        `;

        toast.querySelector('.toast-close-btn').onclick = () => removeToast(toast);

        container.appendChild(toast);
        setTimeout(() => removeToast(toast), 6000);
    }

    function showModal(title, message, options = {}) {
        createContainer();
        const overlay = document.createElement('div');
        overlay.className = 'premium-modal-overlay';

        overlay.innerHTML = `
            <div class="premium-modal animate-modal-in">
                <div class="modal-header">
                    <h3 style="margin: 0; font-size: 1.25rem;">${title}</h3>
                    <button class="close-btn" style="background: none; border: none; color: rgba(255,255,255,0.5); cursor: pointer; font-size: 1.8rem; padding: 10px; line-height: 1; transition: color 0.2s;">&times;</button>
                </div>
                <div class="modal-body">
                    <div style="white-space: pre-line; margin-bottom: 16px;">${message}</div>
                    ${options.showInput ? `<input type="text" id="modalInput" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.2); color: white; outline: none;" placeholder="${options.placeholder || ''}">` : ''}
                </div>
                <div class="modal-footer">
                    ${options.showCancel ? `<button class="modal-btn cancel-btn" style="background: rgba(255,255,255,0.1); color: white;">Cancel</button>` : ''}
                    <button class="modal-btn modal-btn-primary confirm-btn">${options.confirmText || 'OK'}</button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        const input = overlay.querySelector('#modalInput');
        if (input) input.focus();

        return new Promise((resolve) => {
            const close = (val) => {
                overlay.style.opacity = '0';
                overlay.style.transition = 'opacity 0.2s';
                setTimeout(() => overlay.remove(), 200);
                resolve(val);
            };

            // Allow closing by clicking the overlay backdrop
            overlay.onclick = (e) => {
                if (e.target === overlay) close(null);
            };

            overlay.querySelector('.confirm-btn').onclick = () => {
                const value = input ? input.value : true;
                if (options.showInput && !value && options.required) {
                    input.style.borderColor = '#ef4444';
                    return;
                }
                close(value);
            };

            const cancelBtn = overlay.querySelector('.cancel-btn');
            if (cancelBtn) cancelBtn.onclick = () => close(null);

            const closeBtn = overlay.querySelector('.close-btn');
            if (closeBtn) closeBtn.onclick = () => close(null);

            if (input) {
                input.onkeydown = (e) => {
                    if (e.key === 'Enter') overlay.querySelector('.confirm-btn').click();
                    if (e.key === 'Escape') close(null);
                };
            }
        });
    }

    function removeToast(toast) {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.5s ease-in';
            setTimeout(() => toast.remove(), 500);
        }
    }

    // Override native alert for consistency
    window.alert = (msg) => showAlert(msg);

    function formatTime(seconds) {
        if (seconds <= 0) return "00:00:00";
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        return [h, m, s].map(v => v.toString().padStart(2, '0')).join(':');
    }

    function updateTimers(data) {
        const timerElements = document.querySelectorAll('.contest-timer');
        timerElements.forEach(el => {
            const contestId = el.dataset.contestId;
            if (!contestId) return;
            const contest = data.contests.find(c => c.id == contestId);

            if (contest) {
                if (contest.status === 'upcoming') {
                    el.innerHTML = `<span style="color: var(--primary);">Starts in: ${formatTime(contest.remaining)}</span>`;
                } else if (contest.status === 'running') {
                    el.innerHTML = `<span style="color: var(--success);">Ends in: ${formatTime(contest.remaining)}</span>`;
                } else {
                    el.innerHTML = `<span style="color: var(--danger);">Contest Ended</span>`;
                }
            }
        });
    }

    // Global listener
    window.addEventListener('load', () => {
        const checkSocket = setInterval(() => {
            if (window.socket || (typeof io !== 'undefined' && !window.broadcastSocket)) {
                window.broadcastSocket = window.socket || io();
                // crucial: share it back if we created it
                if (!window.socket) window.socket = window.broadcastSocket;

                window.broadcastSocket.on('broadcast', (data) => {
                    showNotification(data);
                });

                window.broadcastSocket.on('timer_update', (data) => {
                    updateTimers(data);
                });

                console.log('Broadcast & Timer listeners attached');
                clearInterval(checkSocket);
            }
        }, 500);
        setTimeout(() => clearInterval(checkSocket), 5000);
    });
})();
