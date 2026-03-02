// ✅ STRICT PROCTORING: Enforce Fullscreen
(function () {
    let proctorOverlay = null;
    let isConfirmingExit = false;

    function createOverlay() {
        if (document.getElementById('proctor-overlay')) return;

        proctorOverlay = document.createElement('div');
        proctorOverlay.id = 'proctor-overlay';
        proctorOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #0f172a;
            z-index: 999999; /* High, but below modals */
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
        `;

        proctorOverlay.innerHTML = `
            <div style="max-width: 500px; padding: 2rem; background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; backdrop-filter: blur(10px); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);">
                <h1 style="margin-bottom: 1rem; color: #ef4444; font-size: 2rem;">⚠️ Test Paused</h1>
                <p style="margin-bottom: 2rem; font-size: 1.1rem; line-height: 1.6; color: rgba(255,255,255,0.9);">
                    Strict Proctoring Mode is active.<br>
                    You must remain in fullscreen mode to continue the contest.
                </p>
                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <button id="enter-fs-btn" style="
                        background: #3b82f6; 
                        color: white; 
                        border: none; 
                        padding: 0.75rem 1.5rem; 
                        font-size: 1rem; 
                        font-weight: 600; 
                        border-radius: 8px; 
                        cursor: pointer;
                        transition: all 0.2s;
                    ">Resume Contest</button>
                    <button id="quit-contest-btn" style="
                        background: rgba(255,255,255,0.1); 
                        color: white; 
                        border: 1px solid rgba(255,255,255,0.2); 
                        padding: 0.75rem 1.5rem; 
                        font-size: 1rem; 
                        font-weight: 500; 
                        border-radius: 8px; 
                        cursor: pointer;
                        transition: all 0.2s;
                    ">Exit Contest</button>
                </div>
            </div>
        `;

        document.body.appendChild(proctorOverlay);

        document.getElementById('enter-fs-btn').addEventListener('click', async () => {
            try {
                // 1. Request Fullscreen (Standard)
                if (document.documentElement.requestFullscreen) {
                    await document.documentElement.requestFullscreen();
                } else if (document.documentElement.webkitRequestFullscreen) {
                    await document.documentElement.webkitRequestFullscreen();
                } else if (document.documentElement.msRequestFullscreen) {
                    await document.documentElement.msRequestFullscreen();
                }

                // 2. Request Esc Lock (Chrome/Edge Only - Optional)
                if (navigator.keyboard && navigator.keyboard.lock) {
                    try {
                        await navigator.keyboard.lock(['Escape']);
                    } catch (e) {
                        console.warn('Keyboard lock failed:', e);
                    }
                }

                // Hide overlay immediately on success, let event listener handle logging if needed
                if (proctorOverlay) proctorOverlay.style.display = 'none';

            } catch (err) {
                console.error('Proctoring entry failed:', err);
                const msg = 'Failed to enter fullscreen mode. Please ensure you are not using a private/incognito window that blocks this feature.';
                if (window.showAlert) showAlert(msg, 'error');
                else alert(msg);
            }
        });

        document.getElementById('quit-contest-btn').addEventListener('click', async () => {
            await triggerExitConfirmation('/dashboard');
        });
    }

    async function triggerExitConfirmation(targetUrl) {
        if (isConfirmingExit) return;
        isConfirmingExit = true;

        if (window.showModal) {
            const confirm1 = await showModal('⚠️ Exit Contest?', 'Are you sure you want to leave the contest? Your work is saved, but this will be logged.', {
                showCancel: true,
                confirmText: 'Yes, Exit'
            });
            if (confirm1) {
                const confirm2 = await showModal('☢️ Final Confirmation', 'SYSTEM ALERT: Are you REALLY sure? Exiting the contest window while the timer is running might be flagged as a policy violation.', {
                    showCancel: true,
                    confirmText: 'CONFIRM EXIT'
                });
                if (confirm2) {
                    window.onbeforeunload = null;
                    window.location.href = targetUrl;
                    isConfirmingExit = false; // Just in case, though we are navigating
                    return;
                }
            }
        } else {
            if (confirm('Exit contest?') && confirm('REALLY SURE? This will be logged.')) {
                window.onbeforeunload = null;
                window.location.href = targetUrl;
                isConfirmingExit = false;
                return;
            }
        }

        isConfirmingExit = false;
    }

    function checkFullscreen() {
        if (!document.fullscreenElement) {
            if (!proctorOverlay) createOverlay();

            // Only log if we weren't already showing the overlay (prevents double logging)
            if (proctorOverlay.style.display !== 'flex') {
                proctorOverlay.style.display = 'flex';
                logProctoringEvent('fullscreen_exit');
            }
        } else {
            if (proctorOverlay) proctorOverlay.style.display = 'none';
        }
    }

    // Monitor fullscreen changes (log only exits)
    document.addEventListener('fullscreenchange', async () => {
        if (!document.fullscreenElement) {
            logProctoringEvent('fullscreen_exit');
        }
        checkFullscreen();
        // Re-lock if we just entered
        if (document.fullscreenElement && navigator.keyboard && navigator.keyboard.lock) {
            try { await navigator.keyboard.lock(['Escape']); } catch (e) { }
        }
    });

    // Handle Escape key explicitly
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            // If we've successfully locked it, the browser won't minimize.
            // We can now show the confirmation flow while STILL in fullscreen.
            e.preventDefault();
            triggerExitConfirmation('/dashboard');

            // Fallback: if browser minimized anyway (long-press Esc)
            setTimeout(checkFullscreen, 150);
        }
    });

    // Initial check (wait for DOM)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            createOverlay();
            checkFullscreen();
        });
    } else {
        createOverlay();
        checkFullscreen();
    }

    // Tab visibility monitoring (debounced and single entry)
    let lastHidden = null;
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            lastHidden = Date.now();
        } else {
            // Only log when coming back, as a single transition
            if (lastHidden) {
                logProctoringEvent('focus_return');
                lastHidden = null;
            }
            checkFullscreen();
        }
    });

    // Log proctoring events (send to server)
    function logProctoringEvent(event) {
        fetch('/api/proctor_log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event: event,
                timestamp: new Date().toISOString()
            })
        }).catch(err => console.warn('Failed to log proctor event:', err));
    }

    // Prevent F12/Inspect (Optional - Basic Deterrent)
    document.addEventListener('keydown', e => {
        if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I')) {
            e.preventDefault();
        }
    });

    // 🚀 Navigational Safety: Double confirmation for leaving the page
    document.addEventListener('click', async (e) => {
        const link = e.target.closest('a');
        if (!link || !link.href || link.target === '_blank') return;

        // Check if the link is meant to exit the contest page
        const isInternalProblemChange = link.href.includes('/problem/') ||
            link.hasAttribute('onclick') ||
            link.href.startsWith('javascript:');

        if (isInternalProblemChange) return;

        const url = new URL(link.href);
        if (url.origin === window.location.origin) {
            // Trying to go back to dashboard, leaderboard, etc.
            e.preventDefault();
            await triggerExitConfirmation(link.href);
        }
    });

    // Standard browser prompt for tab closure
    window.onbeforeunload = function () {
        return "Contest is in progress. Are you sure you want to close this tab?";
    };

})();
