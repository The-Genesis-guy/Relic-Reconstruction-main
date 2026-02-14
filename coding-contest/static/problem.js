(function () {
    const DEBUG = false;
    const debugLog = (...args) => DEBUG && console.log('[problem]', ...args);
    const debugError = (...args) => DEBUG && console.error('[problem]', ...args);

    const data = window.PROBLEM_DATA || {};
    debugLog('problem.js loaded', data);
    if (!data.problemId) {
        console.warn('PROBLEM_DATA missing or problemId undefined');
    }
    // Dynamic accessors
    const getProblemMode = () => (window.PROBLEM_DATA && window.PROBLEM_DATA.problemMode) || 'stdin';
    const getFunctionName = () => (window.PROBLEM_DATA && window.PROBLEM_DATA.functionName) || 'solve';
    const getStarterMap = () => (window.PROBLEM_DATA && window.PROBLEM_DATA.starterCodeMap) || {};

    function defaultStarter(language) {
        const problemMode = getProblemMode();
        const functionName = getFunctionName();

        if (language === 'python') {
            return problemMode === 'function'
                ? `def ${functionName}(data):\n    # data will contain the input in the format described\n    return \"\"`
                : `import sys\n\ndef main():\n    data = sys.stdin.read().strip()\n    # Write your logic here\n    # print(result)\n\nif __name__ == '__main__':\n    main()\n`;
        }
        if (language === 'cpp') {
            return problemMode === 'function'
                ? `std::string ${functionName}(const std::string& data) {\n    // return the answer\n    return \"\";\n}`
                : `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n\n    // Write your logic here\n\n    return 0;\n}\n`;
        }
        if (language === 'c') {
            return problemMode === 'function'
                ? `#include <stdlib.h>\n#include <string.h>\n\nchar* ${functionName}(const char* data) {\n    // return result (malloc a string)\n    char* out = (char*)malloc(1);\n    out[0] = '\\0';\n    return out;\n}`
                : `#include <stdio.h>\n\nint main() {\n    // Write your logic here\n    return 0;\n}\n`;
        }
        if (language === 'java') {
            return problemMode === 'function'
                ? `class Solution {\n    public String ${functionName}(String data) {\n        // return the answer\n        return \"\";\n    }\n}`
                : `import java.io.*;\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) throws Exception {\n        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));\n        // Write your logic here\n    }\n}\n`;
        }
        return '';
    }

    function emptyStarter(language) {
        if (language === 'python') return '# Write your code here';
        if (language === 'cpp' || language === 'c' || language === 'java') return '// Write your code here';
        return '';
    }

    function getStarterCode(language) {
        let map = getStarterMap();
        // Handle if map is string (initial load case might be string if not parsed properly in problem.html script block, but we handle that there)
        if (typeof map === 'string') {
            try { map = JSON.parse(map); } catch (e) { map = {}; }
        }

        if (map && map[language]) {
            return map[language];
        }
        if (map && map.default) {
            return map.default;
        }
        return defaultStarter(language);
    }

    // Monaco Editor Integration
    let monacoEditor;
    const editorContainer = document.getElementById('editor-container');

    if (editorContainer && typeof require !== 'undefined') {
        require.config({ paths: { 'vs': '/static/libs/monaco-editor/min/vs' } });
        require(['vs/editor/editor.main'], function () {
            monacoEditor = monaco.editor.create(editorContainer, {
                value: '',
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: false, // Disable automatic layout to prevent jumps
                fontSize: 14,
                fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                lineNumbers: 'on',
                roundedSelection: true,
                cursorStyle: 'line',
                cursorBlinking: 'smooth',
                formatOnPaste: true,
                formatOnType: true,
                padding: { top: 16, bottom: 16 },
                scrollbar: {
                    alwaysConsumeMouseWheel: false
                },
                fixedOverflowWidgets: true // Prevent overflow widgets from affecting layout
            });
            window.monacoEditor = monacoEditor; // Make globally accessible
            debugLog('Monaco Editor initialized');
            
            // Manual layout on window resize only (less aggressive)
            let resizeTimeout;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {
                    if (monacoEditor) {
                        monacoEditor.layout();
                    }
                }, 100);
            });

            // Fix scroll propagation - allow page scroll when editor is at top/bottom
            editorContainer.addEventListener('wheel', function (e) {
                const scrollTop = monacoEditor.getScrollTop();
                const scrollHeight = monacoEditor.getScrollHeight();
                const containerHeight = editorContainer.clientHeight;

                const isAtTop = scrollTop === 0;
                const isAtBottom = scrollTop + containerHeight >= scrollHeight - 1;

                // Allow page scroll when at editor boundaries
                if ((e.deltaY < 0 && isAtTop) || (e.deltaY > 0 && isAtBottom)) {
                    // Don't stop propagation - let the page scroll
                    return;
                }
            }, { passive: true });

            // Apply initial starter code
            const langSelect = document.getElementById('language');
            if (langSelect) {
                applyStarterCode(langSelect.value);
            }
        });
    }

    function applyStarterCode(language) {
        try {
            const code = getStarterCode(language) || emptyStarter(language);
            const textarea = document.getElementById('code');
            if (textarea) textarea.value = code;

            if (monacoEditor) {
                const monacoLang = language === 'javascript' ? 'javascript' :
                    language === 'cpp' ? 'cpp' :
                        language === 'c' ? 'c' :
                            language === 'java' ? 'java' : 'python';

                monaco.editor.setModelLanguage(monacoEditor.getModel(), monacoLang);
                monacoEditor.setValue(code);
            }
            debugLog('Starter code applied', { language, mode: getProblemMode() });
        } catch (e) {
            debugError('applyStarterCode failed', String(e));
        }
    }

    async function readJson(response) {
        try {
            return await response.json();
        } catch (error) {
            return { error: 'Invalid JSON response', status: response.status };
        }
    }

    // Cooldown management
    let runCooldownTimer = null;
    let submitCooldownTimer = null;

    function startCooldown(type, seconds) {
        const btn = document.getElementById(type === 'run' ? 'runBtn' : 'submitBtn');
        const cooldownSpan = document.getElementById(type === 'run' ? 'runCooldown' : 'submitCooldown');

        if (!btn || !cooldownSpan) return;

        btn.disabled = true;
        btn.style.opacity = '0.6';
        btn.style.cursor = 'not-allowed';
        cooldownSpan.style.display = 'inline';

        let remaining = seconds;
        cooldownSpan.textContent = `(${remaining}s)`;

        const timer = setInterval(() => {
            remaining--;
            if (remaining <= 0) {
                clearInterval(timer);
                btn.disabled = false;
                btn.style.opacity = '1';
                btn.style.cursor = 'pointer';
                cooldownSpan.style.display = 'none';
                if (type === 'run') runCooldownTimer = null;
                else submitCooldownTimer = null;
            } else {
                cooldownSpan.textContent = `(${remaining}s)`;
            }
        }, 1000);

        if (type === 'run') runCooldownTimer = timer;
        else submitCooldownTimer = timer;
    }

    // Status timer update
    function updateStatusTimer() {
        const timerEl = document.getElementById('statusTimer');
        const contestTimerEl = document.querySelector('.contest-timer');

        if (timerEl && contestTimerEl) {
            timerEl.textContent = contestTimerEl.textContent || 'Loading...';
        }
    }

    // Update status timer every second
    setInterval(updateStatusTimer, 1000);
    setTimeout(updateStatusTimer, 100);

    window.runCode = async function runCode() {
        const code = monacoEditor ? monacoEditor.getValue() : document.getElementById('code').value;
        const language = document.getElementById('language').value;
        const resultDiv = document.getElementById('result');

        resultDiv.classList.remove('hidden');
        resultDiv.innerHTML = '<div class="result-box" style="background: rgba(59, 130, 246, 0.1); border-color: var(--info);"><div class="spinner"></div><p style="text-align: center; margin-top: 1rem; color: var(--text-secondary);">Running code...</p></div>';

        try {
            const response = await fetch(`/run/${data.problemId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, language })
            });
            const res = await readJson(response);
            if (!response.ok) {
                debugError('Run failed', response.status, res);
            }

            if (res.error || (res.verdict && res.verdict !== 'AC')) {
                debugError('Run error', res.error || res.output);
                resultDiv.innerHTML = `<div class="result-box" style="background: rgba(239, 68, 68, 0.1); border-color: var(--danger);"><strong style="color: var(--danger);">Error</strong><pre style="margin-top: 0.5rem; color: var(--text-secondary);">${res.error || res.output || 'Unknown Error'}</pre></div>`;
            } else {
                resultDiv.innerHTML = `<div class="result-box" style="background: rgba(16, 185, 129, 0.1); border-color: var(--success);"><strong style="color: var(--success);">Output</strong><pre style="margin-top: 0.5rem; color: var(--text-secondary);">${res.output || 'No output'}</pre></div>`;
            }

            // Start 3s cooldown
            startCooldown('run', 3);
        } catch (error) {
            debugError('Run exception', String(error));
            resultDiv.innerHTML = `<div class="result-box" style="background: rgba(239, 68, 68, 0.1); border-color: var(--danger);"><strong style="color: var(--danger);">Error</strong><p style="margin-top: 0.5rem; color: var(--text-secondary);">${error}</p></div>`;
        }
    };

    window.submitCode = async function submitCode() {
        const code = monacoEditor ? monacoEditor.getValue() : document.getElementById('code').value;
        const language = document.getElementById('language').value;
        const resultDiv = document.getElementById('result');

        resultDiv.classList.remove('hidden');
        resultDiv.innerHTML = '<div class="result-box" style="background: rgba(59, 130, 246, 0.1); border-color: var(--info);"><div class="spinner"></div><p style="text-align: center; margin-top: 1rem; color: var(--text-secondary);">Judging submission...</p></div>';

        try {
            const response = await fetch(`/submit/${data.problemId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, language })
            });
            const res = await readJson(response);
            if (!response.ok) {
                debugError('Submit failed', response.status, res);
            }

            if (res.error) {
                debugError('Submit error', res.error);
                resultDiv.innerHTML = `<div class="result-box" style="background: rgba(239, 68, 68, 0.1); border-color: var(--danger);"><strong style="color: var(--danger);">${res.error}</strong></div>`;
            } else {
                window.ACTIVE_SUBMISSION_ID = res.submission_id;
                pollSubmission(res.submission_id);
                // Start 3s cooldown
                startCooldown('submit', 3);
            }
        } catch (error) {
            debugError('Submit exception', String(error));
            resultDiv.innerHTML = `<div class="result-box" style="background: rgba(239, 68, 68, 0.1); border-color: var(--danger);"><strong style="color: var(--danger);">Error: ${error}</strong></div>`;
        }
    };

    // Initialize SocketIO
    let socket;
    if (typeof io !== 'undefined') {
        socket = window.socket || io();
        window.socket = socket;
        socket.on('connected', (data) => debugLog('WebSocket connected', data));

        socket.on('submission_update', (res) => {
            debugLog('Real-time submission update', res);

            // 1. Update Sidebar Status (Global)
            if (res.problem_id) {
                const sidebarItem = document.querySelector(`.sidebar-problem-item[data-problem-id="${res.problem_id}"]`);
                if (sidebarItem) {
                    const statusDiv = sidebarItem.querySelector('.problem-status');
                    if (statusDiv) {
                        // Update class and icon based on verdict
                        sidebarItem.classList.remove('solved', 'attempted');
                        // If previously solved, keep solved. If AC, mark solved.
                        // Since we don't have full history here, we just apply current verdict logic optimistically
                        // A more robust way would be if res had 'is_solved' for the problem

                        if (res.verdict === 'AC') {
                            sidebarItem.classList.add('solved');
                            statusDiv.innerHTML = '<span class="status-icon solved">✓</span>';
                        } else if (!sidebarItem.classList.contains('solved')) {
                            sidebarItem.classList.add('attempted');
                            statusDiv.innerHTML = '<span class="status-icon attempted">○</span>';
                        }
                    }
                }
            }

            // 2. Show Global Toast Notification
            if (window.showNotification) {
                const colors = { 'AC': '#10b981', 'WA': '#ef4444', 'TLE': '#f59e0b', 'RE': '#ef4444', 'CE': '#ef4444' };
                const color = colors[res.verdict] || '#3b82f6';
                const msg = `Problem: ${res.problem_title || 'Unknown'}<br><strong style="color: ${color}">${res.verdict}</strong>`;
                window.showNotification({ sender: 'System', message: msg, timestamp: 'Just now' });
            }

            // 3. Update Local Result View (if on same problem)
            const activeSubmissionId = window.ACTIVE_SUBMISSION_ID;
            // Also check if we are currently viewing the problem for this result
            // This prevents showing results for Problem A inside Problem B's result box
            const isCurrentProblem = window.PROBLEM_DATA && window.PROBLEM_DATA.problemId == res.problem_id;

            if (activeSubmissionId && res.submission_id == activeSubmissionId && isCurrentProblem) {
                displayResult(res);
                if (window.showAlert) {
                    if (res.verdict === 'AC') {
                        showAlert(`🚀 SUBMISSION SUCCESSFUL!\nAll test cases passed.`, 'success');
                    } else {
                        showAlert(`Judge Completed: ${res.verdict}\nReview the details below.`, 'info');
                    }
                }
                window.ACTIVE_SUBMISSION_ID = null;
            }
        });
    } else {
        console.warn('SocketIO not loaded, falling back to polling');
    }

    async function pollSubmission(submissionId) {
        // Fallback polling logic
        debugLog('Polling for submission', submissionId);
        try {
            const response = await fetch(`/submission_status/${submissionId}`);
            const res = await response.json();

            if (res.verdict === 'PENDING') {
                setTimeout(() => pollSubmission(submissionId), 2000);
                return;
            }
            displayResult(res);
        } catch (error) {
            debugError('Polling error', error);
        }
    }

    function displayResult(res) {
        const resultDiv = document.getElementById('result');
        const verdictColors = {
            'AC': { bg: 'rgba(16, 185, 129, 0.1)', border: 'var(--success)', color: 'var(--success)' },
            'PC': { bg: 'rgba(245, 158, 11, 0.1)', border: 'var(--warning)', color: 'var(--warning)' },
            'WA': { bg: 'rgba(239, 68, 68, 0.1)', border: 'var(--danger)', color: 'var(--danger)' },
            'TLE': { bg: 'rgba(245, 158, 11, 0.1)', border: 'var(--warning)', color: 'var(--warning)' },
            'RE': { bg: 'rgba(239, 68, 68, 0.1)', border: 'var(--danger)', color: 'var(--danger)' },
            'CE': { bg: 'rgba(239, 68, 68, 0.1)', border: 'var(--danger)', color: 'var(--danger)' }
        };

        const style = verdictColors[res.verdict] || verdictColors['WA'];

        // Verdict messages without points
        const verdictMessages = {
            'AC': 'Accepted - All test cases passed!',
            'PC': 'Partial Credit - Some test cases passed',
            'WA': 'Wrong Answer - Some test cases failed',
            'TLE': 'Time Limit Exceeded - Your solution is too slow',
            'RE': 'Runtime Error - Your program crashed',
            'CE': 'Compilation Error - Check your syntax'
        };

        const message = verdictMessages[res.verdict] || res.verdict;

        resultDiv.innerHTML = `
            <div class="result-box" style="background: ${style.bg}; border-color: ${style.border};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div>
                        <strong style="color: ${style.color}; font-size: 1.25rem; display: block;">${message}</strong>
                        ${data.showScores && res.points !== undefined ? `<span style="color: var(--accent); font-size: 0.9rem; font-weight: 600;">Score: ${res.points} / ${res.max_points || 0}</span>` : ''}
                    </div>
                    <div style="text-align: right;">
                        <span style="display: block; color: var(--text-secondary); font-weight: 600;">${res.total_passed || 0}/${res.total_tests || 0} Tests Passed</span>
                    </div>
                </div>
                ${res.output ? `<pre style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 4px; color: var(--text-secondary); font-size: 0.9rem; overflow-x: auto; border: 1px solid rgba(255,255,255,0.05);">${res.output}</pre>` : ''}
            </div>
        `;
    }

    function initProblemEditor() {
        const languageSelect = document.getElementById('language');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                applyStarterCode(e.target.value);
            });
            applyStarterCode(languageSelect.value);
        } else {
            debugError('Language select not found');
        }
    }

    // Expose loadProblem globally
    window.loadProblem = async function (event, problemId) {
        if (event) event.preventDefault();

        debugLog('Loading problem', problemId);

        // Visual feedback on sidebar
        document.querySelectorAll('.sidebar-problem-item').forEach(el => {
            el.classList.remove('active');
            if (el.dataset.problemId == problemId) {
                el.classList.add('active');
            }
        });

        // Show loading state
        const contentDiv = document.querySelector('.problem-content');
        contentDiv.style.opacity = '0.5';

        try {
            const response = await fetch(`/api/student/problem/${problemId}`);
            if (!response.ok) throw new Error('Failed to load problem');

            const problem = await response.json();

            // Update Global Data
            window.PROBLEM_DATA.problemId = problem.id;
            window.PROBLEM_DATA.starterCodeMap = JSON.parse(problem.starter_code_map);
            window.PROBLEM_DATA.problemMode = problem.problem_mode;
            window.PROBLEM_DATA.functionName = problem.function_name;
            // update other data fields if necessary

            // Update URL (without reload)
            history.pushState({ problemId: problem.id }, '', `/problem/${problem.id}`);

            // Update Title and Badges
            document.querySelector('h1').textContent = problem.title;
            document.querySelector('.badge-info').textContent = problem.problem_type;
            document.querySelector('.badge-success').textContent = problem.problem_mode;

            const fnBadge = document.querySelector('.badge-warning');
            if (problem.problem_mode === 'function') {
                if (fnBadge) fnBadge.textContent = `function: ${problem.function_name}`;
                else {
                    const span = document.createElement('span');
                    span.className = 'badge badge-warning';
                    span.textContent = `function: ${problem.function_name}`;
                    document.querySelector('.badge-success').after(span);
                }
            } else if (fnBadge) {
                fnBadge.remove();
            }

            // Update Description and I/O
            let html = `<p>${problem.description}</p>`;
            html += `<h3>Input Format</h3><pre style="background: var(--bg-darker); padding: 1rem; border-radius: var(--radius); overflow-x: auto;">${problem.input_format}</pre>`;
            html += `<h3>Output Format</h3><pre style="background: var(--bg-darker); padding: 1rem; border-radius: var(--radius); overflow-x: auto;">${problem.output_format}</pre>`;

            if (problem.constraints) {
                html += `<h3>Constraints</h3><pre style="background: var(--bg-darker); padding: 1rem; border-radius: var(--radius); overflow-x: auto;">${problem.constraints}</pre>`;
            }

            html += `<h3>Sample Test Cases</h3>`;
            if (problem.sample_tests && problem.sample_tests.length > 0) {
                problem.sample_tests.forEach((test, index) => {
                    html += `
                    <div style="margin-bottom: 1.5rem; padding: 1rem; background: var(--bg-darker); border-radius: var(--radius); border-left: 3px solid var(--accent);">
                        <h4 style="margin-top: 0; color: var(--accent); font-size: 0.9rem;">Test Case ${index + 1}</h4>
                        <div style="margin-bottom: 0.75rem;">
                            <strong style="color: var(--text-secondary);">Input:</strong>
                            <pre style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 4px; margin-top: 0.25rem; overflow-x: auto;">${test.input}</pre>
                        </div>
                        <div>
                            <strong style="color: var(--text-secondary);">Expected Output:</strong>
                            <pre style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 4px; margin-top: 0.25rem; overflow-x: auto;">${test.expected_output}</pre>
                        </div>
                    </div>`;
                });
            } else {
                html += `
                    <div style="margin-bottom: 1.5rem; padding: 1rem; background: var(--bg-darker); border-radius: var(--radius); border-left: 3px solid var(--accent);">
                        <h4 style="margin-top: 0; color: var(--accent); font-size: 0.9rem;">Sample Test Case</h4>
                        <div style="margin-bottom: 0.75rem;">
                            <strong style="color: var(--text-secondary);">Input:</strong>
                            <pre style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 4px; margin-top: 0.25rem; overflow-x: auto;">${problem.sample_input || ''}</pre>
                        </div>
                        <div>
                            <strong style="color: var(--text-secondary);">Expected Output:</strong>
                            <pre style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 4px; margin-top: 0.25rem; overflow-x: auto;">${problem.sample_output || ''}</pre>
                        </div>
                    </div>`;
            }

            contentDiv.innerHTML = html;

            // Reset Editor
            const langSelect = document.getElementById('language');
            if (langSelect) applyStarterCode(langSelect.value);

            // Clear result
            const resultDiv = document.getElementById('result');
            resultDiv.classList.add('hidden');
            resultDiv.innerHTML = '';

            // Close Sidebar on mobile
            if (window.innerWidth < 768) {
                const sidebar = document.getElementById('problemSidebar');
                if (sidebar) sidebar.classList.remove('open');
            }

        } catch (error) {
            console.error('Error loading problem:', error);
            if (window.showAlert) showAlert('Failed to load problem details', 'error');
            else alert('Failed to load problem details');
        } finally {
            contentDiv.style.opacity = '1';
        }
    };

    // Handle Browser Back/Forward
    window.addEventListener('popstate', (event) => {
        if (event.state && event.state.problemId) {
            loadProblem(null, event.state.problemId);
        } else {
            // If no state (e.g. initial page load), reload to be safe or try to parse URL
            location.reload();
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initProblemEditor);
    } else {
        initProblemEditor();
    }
})();
