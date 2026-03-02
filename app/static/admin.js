// Admin dashboard logic
const ENABLE_POLLING = false;

const AdminDebug = (function () {
    let container;
    let enabled = true;

    function init() {
        container = document.getElementById('adminDebugLog');
        if (!container) return;
        log('Debug console initialized.');
    }

    function log(message, data) {
        if (!enabled) return;
        if (!container) return;
        const item = document.createElement('div');
        item.style.cssText = 'padding: 6px 0; border-bottom: 1px dashed rgba(255,255,255,0.08); font-size: 0.8rem;';
        const time = new Date().toLocaleTimeString();
        item.innerHTML = `<span style="color: var(--text-muted); margin-right: 8px;">${time}</span>` +
            `<span style="color: var(--text-secondary);">${message}</span>` +
            (data ? `<pre style="white-space: pre-wrap; margin-top: 6px; color: var(--text-muted);">${JSON.stringify(data, null, 2)}</pre>` : '');
        container.prepend(item);
    }

    function error(message, data) {
        if (!enabled) return;
        if (!container) return;
        const item = document.createElement('div');
        item.style.cssText = 'padding: 6px 0; border-bottom: 1px dashed rgba(255,255,255,0.08); font-size: 0.8rem;';
        const time = new Date().toLocaleTimeString();
        item.innerHTML = `<span style="color: #b94a3a; margin-right: 8px;">${time}</span>` +
            `<span style="color: #f3b5ad;">${message}</span>` +
            (data ? `<pre style="white-space: pre-wrap; margin-top: 6px; color: #f1d0c9;">${JSON.stringify(data, null, 2)}</pre>` : '');
        container.prepend(item);
    }

    function toggle() {
        enabled = !enabled;
        log(`Debug console ${enabled ? 'enabled' : 'disabled'}.`);
    }

    return { init, log, error, toggle };
})();

// Monaco Editor for Admin
let adminStarterEditor;
let adminSolutionEditor;
let currentStarterLang = 'python';
let currentSolutionLang = 'python';
let starterCodeData = {
    python: '',
    cpp: '',
    java: '',
    c: ''
};
let solutionCodeData = {
    python: '',
    cpp: '',
    java: '',
    c: ''
};

// Default boilerplate code for each language
const DEFAULT_BOILERPLATE = {
    python: `# Read input
# For single line: line = input()
# For multiple lines: lines = [input() for _ in range(n)]
# For space-separated values: a, b = map(int, input().split())

# Your code here

# Print output
# print(result)
`,
    cpp: `#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {
    // Read input
    // int n; cin >> n;
    // string s; getline(cin, s);
    
    // Your code here
    
    // Print output
    // cout << result << endl;
    
    return 0;
}
`,
    java: `import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        // Read input
        // int n = sc.nextInt();
        // String s = sc.nextLine();
        
        // Your code here
        
        // Print output
        // System.out.println(result);
        
        sc.close();
    }
}
`,
    c: `#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // Read input
    // int n; scanf("%d", &n);
    // char s[1000]; fgets(s, sizeof(s), stdin);
    
    // Your code here
    
    // Print output
    // printf("%d\\n", result);
    
    return 0;
}
`,
};

window.switchStarterLang = function (lang) {
    if (adminStarterEditor) {
        // Save current code
        starterCodeData[currentStarterLang] = adminStarterEditor.getValue();
    }

    currentStarterLang = lang;

    // Update UI buttons
    const buttons = document.querySelectorAll('#starterLangSwitches button');
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase() === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    if (adminStarterEditor) {
        monaco.editor.setModelLanguage(adminStarterEditor.getModel(), lang);
        // Use saved code or default boilerplate
        const code = starterCodeData[lang] || DEFAULT_BOILERPLATE[lang] || '';
        adminStarterEditor.setValue(code);
    }
};

window.switchSolutionLang = function (lang) {
    if (adminSolutionEditor) {
        solutionCodeData[currentSolutionLang] = adminSolutionEditor.getValue();
    }

    currentSolutionLang = lang;

    const buttons = document.querySelectorAll('#solutionLangSwitches button');
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase() === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    if (adminSolutionEditor) {
        monaco.editor.setModelLanguage(adminSolutionEditor.getModel(), lang);
        const code = solutionCodeData[lang] || '';
        adminSolutionEditor.setValue(code);
    }
};

// Edit Modal Monaco
let editStarterEditor;
let editSolutionEditor;
let currentEditStarterLang = 'python';
let currentEditSolutionLang = 'python';
window.editStarterCodeData = {
    python: '',
    cpp: '',
    java: '',
    c: ''
};
window.editSolutionCodeData = {
    python: '',
    cpp: '',
    java: '',
    c: ''
};

window.switchEditStarterLang = function (lang, save = true) {
    if (editStarterEditor && save) {
        window.editStarterCodeData[currentEditStarterLang] = editStarterEditor.getValue();
    }
    currentEditStarterLang = lang;
    const buttons = document.querySelectorAll('#editStarterLangSwitches button');
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase() === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    if (editStarterEditor) {
        monaco.editor.setModelLanguage(editStarterEditor.getModel(), lang);
        // Use saved code or default boilerplate
        const code = window.editStarterCodeData[lang] || DEFAULT_BOILERPLATE[lang] || '';
        editStarterEditor.setValue(code);
    }
};

window.switchEditSolutionLang = function (lang, save = true) {
    if (editSolutionEditor && save) {
        window.editSolutionCodeData[currentEditSolutionLang] = editSolutionEditor.getValue();
    }
    currentEditSolutionLang = lang;
    const buttons = document.querySelectorAll('#editSolutionLangSwitches button');
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase() === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    if (editSolutionEditor) {
        monaco.editor.setModelLanguage(editSolutionEditor.getModel(), lang);
        const code = window.editSolutionCodeData[lang] || DEFAULT_BOILERPLATE[lang] || '';
        editSolutionEditor.setValue(code);
    }
};

function initAdminMonaco() {
    // Create Problem Editor
    const createContainer = document.getElementById('admin-starter-editor-container');
    const createSolutionContainer = document.getElementById('admin-solution-editor-container');
    const editContainer = document.getElementById('admin-edit-starter-editor-container');

    if ((!createContainer && !editContainer) || typeof require === 'undefined') return;

    require.config({ paths: { 'vs': '/static/libs/monaco-editor/min/vs' } });
    require(['vs/editor/editor.main'], function () {
        if (createContainer) {
            adminStarterEditor = monaco.editor.create(createContainer, {
                value: DEFAULT_BOILERPLATE.python,
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                fontSize: 13,
                minimap: { enabled: false },
                padding: { top: 12, bottom: 4 },
                scrollbar: { alwaysConsumeMouseWheel: false },
                scrollBeyondLastLine: false
            });
        }
        if (createSolutionContainer) {
            adminSolutionEditor = monaco.editor.create(createSolutionContainer, {
                value: '',
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                fontSize: 13,
                minimap: { enabled: false },
                padding: { top: 12, bottom: 4 },
                scrollbar: { alwaysConsumeMouseWheel: false },
                scrollBeyondLastLine: false
            });
        }
        if (editContainer) {
            editStarterEditor = monaco.editor.create(editContainer, {
                value: DEFAULT_BOILERPLATE.python,
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                fontSize: 13,
                minimap: { enabled: false },
                padding: { top: 12, bottom: 4 },
                scrollbar: { alwaysConsumeMouseWheel: false },
                scrollBeyondLastLine: false
            });
        }
        
        // Edit Solution Editor
        const editSolutionContainer = document.getElementById('admin-edit-solution-editor-container');
        if (editSolutionContainer) {
            editSolutionEditor = monaco.editor.create(editSolutionContainer, {
                value: DEFAULT_BOILERPLATE.python,
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                fontSize: 13,
                minimap: { enabled: false },
                padding: { top: 12, bottom: 4 },
                scrollbar: { alwaysConsumeMouseWheel: false },
                scrollBeyondLastLine: false
            });
        }
    });
}

function escapeJsString(value) {
    return String(value).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}

window.showSection = function showSection(sectionId, el) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const target = el || (window.event && window.event.currentTarget);
    if (target && target.classList) {
        target.classList.add('active');
    }

    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
    }

    if (sectionId && window.location.hash !== `#${sectionId}`) {
        window.location.hash = sectionId;
    }

    refreshCurrentSection();
};

window.forceRefresh = function forceRefresh() {
    refreshCurrentSection();
};


async function refreshCurrentSection() {
    const activeSection = document.querySelector('.content-section.active')?.id;

    if (activeSection === 'overview') {
        await loadStats();
        await loadSubmissions();
        await loadAdminLogs();
        await loadProctorLogs();
    } else if (activeSection === 'contests') {
        if (typeof loadContests === 'function') await loadContests();
    } else if (activeSection === 'problems') {
        if (typeof loadAllProblems === 'function') await loadAllProblems();
    } else if (activeSection === 'users') {
        await loadUsers();
    } else if (activeSection === 'submissions') {
        await loadFilteredSubmissions();
    }
}

async function loadStats() {
    try {
        AdminDebug.log('Fetching /admin/stats');
        const response = await fetch('/admin/stats');
        const stats = await response.json();
        document.getElementById('totalUsers').textContent = stats.total_users || 0;
        document.getElementById('totalProblems').textContent = stats.total_problems || 0;
        document.getElementById('totalSubmissions').textContent = stats.total_submissions || 0;
        document.getElementById('totalContests').textContent = stats.total_contests || 0;

        // Update live metrics
        const queueSizeEl = document.getElementById('queueSize');
        const pendingCountEl = document.getElementById('pendingCount');
        const activeWorkersEl = document.getElementById('activeWorkers');
        
        if (queueSizeEl) queueSizeEl.textContent = stats.queue_size || 0;
        if (pendingCountEl) pendingCountEl.textContent = stats.pending_submissions || 0;
        if (activeWorkersEl) activeWorkersEl.textContent = stats.active_workers || 0;

        const statusBox = document.getElementById('systemStatus');
        const statusText = document.getElementById('systemStatusText');
        if (statusBox && statusText) {
            const queueSize = Number(stats.queue_size || 0);
            const pending = Number(stats.pending_submissions || 0);
            if (queueSize >= 20 || pending >= 20) {
                statusBox.style.display = 'block';
                statusText.textContent = `High load detected. Queue size: ${queueSize}, pending submissions: ${pending}.`;
            } else {
                statusBox.style.display = 'none';
                statusText.textContent = '';
            }
        }
    } catch (error) {
        AdminDebug.error('Error loading stats', { error: String(error) });
    }
}

async function loadAdminLogs() {
    try {
        AdminDebug.log('Fetching /admin/logs');
        const response = await fetch('/admin/logs?limit=20');
        const logs = await response.json();
        const list = document.getElementById('adminActionLogs');

        if (!list) return;

        if (logs.length === 0) {
            list.innerHTML = '<p style="text-align:center; color: var(--text-muted); font-size: 0.875rem;">No admin actions logged yet.</p>';
            return;
        }

        list.innerHTML = `
            <table class="table" style="width: 100%; font-size: 0.75rem;">
                <thead>
                    <tr>
                        <th style="width: 140px;">Time</th>
                        <th style="width: 100px;">Admin</th>
                        <th style="width: 120px;">Action</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    ${logs.map(log => {
            // Append Z to force UTC interpretation, then convert to local
            const timeStr = log.created_at.includes(' ') ? log.created_at.replace(' ', 'T') + 'Z' : log.created_at + 'Z';
            const time = new Date(timeStr).toLocaleString();

            // Color coding based on action type
            let badgeClass = 'badge-info';
            if (log.action.includes('DELETE') || log.action.includes('RESET') || log.action.includes('CLEAR')) {
                badgeClass = 'badge-danger';
            } else if (log.action.includes('CREATE') || log.action.includes('ADD')) {
                badgeClass = 'badge-success';
            } else if (log.action.includes('UPDATE') || log.action.includes('EDIT') || log.action.includes('TOGGLE')) {
                badgeClass = 'badge-warning';
            }

            return `
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                                <td style="color: var(--text-muted); font-size: 0.75rem; white-space: nowrap;">${time}</td>
                                <td style="color: var(--text-primary); font-weight: 500;">${log.admin}</td>
                                <td>
                                    <span class="badge ${badgeClass}" style="font-size: 10px; padding: 2px 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                                        ${log.action.replace(/_/g, ' ')}
                                    </span>
                                </td>
                                <td style="color: var(--text-secondary); font-size: 0.75rem; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${log.details || ''}">
                                    ${log.details || '-'}
                                </td>
                            </tr>
                        `;
        }).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        AdminDebug.error('Error loading admin logs', { error: String(error) });
        const list = document.getElementById('adminActionLogs');
        if (list) {
            list.innerHTML = '<p style="color: var(--danger); font-size: 0.875rem;">Error loading logs</p>';
        }
    }
}

async function loadProctorLogs() {
    try {
        AdminDebug.log('Fetching /admin/proctor_logs');
        const response = await fetch('/admin/proctor_logs?limit=50');
        const logs = await response.json();
        const list = document.getElementById('adminProctorLogs');

        if (!list) return;

        if (logs.length === 0) {
            list.innerHTML = '<p style="text-align:center; color: var(--text-muted); font-size: 0.875rem;">No proctoring events logged.</p>';
            return;
        }

        list.innerHTML = `
            <table class="table" style="width: 100%; font-size: 0.75rem;">
                <thead>
                    <tr>
                        <th style="width: 140px;">Time</th>
                        <th style="width: 120px;">Student</th>
                        <th style="width: 140px;">Event</th>
                        <th>Evidence</th>
                    </tr>
                </thead>
                <tbody>
                    ${logs.map(log => {
            const timeStr = log.created_at.includes(' ') ? log.created_at.replace(' ', 'T') + 'Z' : log.created_at + 'Z';
            const time = new Date(timeStr).toLocaleString();

            return `
                            <tr>
                                <td style="color: var(--text-muted); font-size: 0.7rem;">${time}</td>
                                <td style="color: #facc15; font-weight: 600;">${log.admin}</td>
                                <td>
                                    <span class="badge" style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 9px; padding: 2px 6px;">
                                        ${log.action}
                                    </span>
                                </td>
                                <td style="color: var(--text-secondary); font-size: 0.7rem;">${log.details || '-'}</td>
                            </tr>
                        `;
        }).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        AdminDebug.error('Error loading proctor logs', { error: String(error) });
        const list = document.getElementById('adminProctorLogs');
        if (list) {
            list.innerHTML = '<p style="color: var(--danger); font-size: 0.875rem;">Error loading logs</p>';
        }
    }
}

async function loadSubmissions() {
    try {
        AdminDebug.log('Fetching /api/admin/submissions');
        const response = await fetch('/api/admin/submissions');
        const subs = await response.json();
        renderSubmissions(subs);
    } catch (error) {
        AdminDebug.error('Error loading submissions', { error: String(error) });
    }
}

function renderSubmissions(subs) {
    const list = document.getElementById('liveSubmissions');
    if (!list) return;

    if (subs.length === 0) {
        list.innerHTML = '<p style="text-align:center; color: var(--text-muted);">No submissions yet.</p>';
        return;
    }

    list.innerHTML = `
        <table class="table" style="width: 100%; font-size: 0.875rem;">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>User</th>
                    <th>Problem</th>
                    <th>Verdict</th>
                    <th style="text-align: right;">Action</th>
                </tr>
            </thead>
            <tbody id="liveSubmissionsBody">
                ${subs.map(s => renderSubmissionRow(s)).join('')}
            </tbody>
        </table>
    `;
}

function renderSubmissionRow(s) {
    const verdictColor = s.verdict === 'AC' ? 'var(--success)' :
        s.verdict === 'PENDING' ? 'var(--warning)' : 'var(--danger)';
    const safeUser = escapeJsString(s.username);
    const safeProblem = escapeJsString(s.problem_title);
    const safeLang = escapeJsString(s.language || 'unknown');

    return `
        <tr id="sub-row-${s.id || s.submission_id}" class="fade-in">
            <td>${new Date(s.submitted_at).toLocaleTimeString()}</td>
            <td>${s.username}</td>
            <td>${s.problem_title}</td>
            <td class="verdict-cell">
                <span style="color: ${verdictColor}; font-weight: 600;">${s.verdict}</span>
                ${s.judging_status !== 'completed' && s.verdict === 'PENDING' ? '<span class="spinner" style="width: 10px; height: 10px; display: inline-block; margin-left: 5px;"></span>' : ''}
            </td>
            <td style="text-align: right;">
                <button onclick="viewSubmissionCode(${s.id || s.submission_id}, '${safeUser}', '${safeProblem}', '${safeLang}')" class="btn btn-sm btn-outline" style="padding: 2px 8px; font-size: 11px;">
                    View Code
                </button>
            </td>
        </tr>
    `;
}

// Initialize SocketIO
let socket;
if (typeof io !== 'undefined') {
    socket = window.socket || io();
    window.socket = socket;
    socket.on('connect', () => {
        AdminDebug.log('Admin connected to WebSocket');
        socket.emit('join_admin');
    });

    socket.on('admin_submission_queued', (data) => {
        AdminDebug.log('Real-time submission queued', data);
        const tbody = document.getElementById('liveSubmissionsBody');
        if (tbody) {
            const html = renderSubmissionRow({
                ...data,
                verdict: 'PENDING',
                judging_status: 'queued'
            });
            tbody.insertAdjacentHTML('afterbegin', html);
            if (tbody.children.length > 50) tbody.removeChild(tbody.lastChild);
        }
    });

    socket.on('admin_submission_update', (data) => {
        AdminDebug.log('Real-time admin update received', data);
        const tbody = document.getElementById('liveSubmissionsBody');
        if (tbody) {
            const existingRow = document.getElementById(`sub-row-${data.submission_id}`);
            const newRowHtml = renderSubmissionRow({
                ...data,
                id: data.submission_id,
                judging_status: 'completed'
            });

            if (existingRow) {
                existingRow.outerHTML = newRowHtml;
            } else {
                tbody.insertAdjacentHTML('afterbegin', newRowHtml);
                if (tbody.children.length > 50) tbody.removeChild(tbody.lastChild);
            }
        }
        // Update stats too
        loadStats();
    });

    socket.on('admin_log_append', (log) => {
        AdminDebug.log('Real-time admin log received', log);
        const container = document.getElementById('adminActionLogs');
        if (!container) return;

        const tbody = container.querySelector('tbody');
        if (!tbody) {
            loadAdminLogs(); // Table doesn't exist yet, reload fully
            return;
        }

        const time = new Date(log.created_at).toLocaleString();
        let badgeClass = 'badge-info';
        if (log.action.includes('DELETE') || log.action.includes('RESET') || log.action.includes('CLEAR')) {
            badgeClass = 'badge-danger';
        } else if (log.action.includes('CREATE') || log.action.includes('ADD')) {
            badgeClass = 'badge-success';
        } else if (log.action.includes('UPDATE') || log.action.includes('EDIT') || log.action.includes('TOGGLE')) {
            badgeClass = 'badge-warning';
        }

        const row = `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);" class="fade-in">
                <td style="color: var(--text-muted); font-size: 0.75rem; white-space: nowrap;">${time}</td>
                <td style="color: var(--text-primary); font-weight: 500;">${log.admin}</td>
                <td>
                    <span class="badge ${badgeClass}" style="font-size: 10px; padding: 2px 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                        ${log.action.replace(/_/g, ' ')}
                    </span>
                </td>
                <td style="color: var(--text-secondary); font-size: 0.75rem; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${log.details || ''}">
                    ${log.details || '-'}
                </td>
            </tr>
        `;
        tbody.insertAdjacentHTML('afterbegin', row);
        if (tbody.children.length > 20) tbody.removeChild(tbody.lastChild);
    });

    socket.on('proctor_log_append', (log) => {
        AdminDebug.log('Real-time proctor log received', log);
        const container = document.getElementById('adminProctorLogs');
        if (!container) return;

        const tbody = container.querySelector('tbody');
        if (!tbody) {
            loadProctorLogs();
            return;
        }

        const time = new Date(log.created_at).toLocaleString();
        const row = `
            <tr class="fade-in">
                <td style="color: var(--text-muted); font-size: 0.7rem;">${time}</td>
                <td style="color: #facc15; font-weight: 600;">${log.admin}</td>
                <td>
                    <span class="badge" style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 9px; padding: 2px 6px;">
                        ${log.action}
                    </span>
                </td>
                <td style="color: var(--text-secondary); font-size: 0.7rem;">${log.details || '-'}</td>
            </tr>
        `;
        tbody.insertAdjacentHTML('afterbegin', row);
        if (tbody.children.length > 50) tbody.removeChild(tbody.lastChild);
    });
}

async function loadUsers() {
    try {
        AdminDebug.log('Fetching /api/admin/users');
        const response = await fetch('/api/admin/users');
        const users = await response.json();
        const list = document.getElementById('usersList');

        list.innerHTML = `
            <table class="table" style="width: 100%; font-size: 0.875rem;">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Role</th>
                        <th style="text-align: right;">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(u => `
                        <tr>
                            <td>#${u.id}</td>
                            <td>${u.username}</td>
                            <td>
                                <span class="badge ${u.role === 'admin' ? 'badge-info' : 'badge-primary'}">
                                    ${u.role}
                                </span>
                            </td>
                            <td style="text-align: right;">
                                ${u.role !== 'admin' ? `
                                <button onclick="resetUserPassword(${u.id}, '${u.username}')" class="btn btn-sm btn-outline" style="padding: 2px 8px; font-size: 11px; margin-right: 4px;">
                                    Reset Password
                                </button>
                                <button onclick="deleteUser(${u.id})" class="btn btn-sm btn-danger" style="padding: 2px 8px; font-size: 11px;">
                                    Delete
                                </button>` : '<span style="color: var(--text-muted); font-size: 11px;">Protected</span>'}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        AdminDebug.error('Error loading users', { error: String(error) });
    }
}

async function resetUserPassword(userId, username) {
    const newPassword = await showModal('Reset Password', `Reset password for user: ${username}`, {
        confirmText: 'Reset',
        showInput: true,
        showCancel: true,
        placeholder: 'Enter new password',
        required: true
    });

    if (!newPassword) {
        return;
    }

    if (newPassword.length < 3) {
        showAlert('Password must be at least 3 characters long', 'warning');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('new_password', newPassword);

        const response = await fetch('/admin/reset_password', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showAlert(`✅ Password reset successfully!\n\nUsername: ${username}\nNew Password: ${newPassword}`, 'success');
        } else {
            showAlert(result.error || 'Error resetting password', 'error');
        }
    } catch (error) {
        showAlert('Error resetting password: ' + error, 'error');
    }
}

async function deleteUser(userId) {
    const confirmed = await showModal('Confirm Delete', 'Are you sure you want to delete this user? This action cannot be undone.', { showCancel: true, confirmText: 'Delete' });
    if (!confirmed) return;

    try {
        const response = await fetch(`/admin/delete_user/${userId}`, { method: 'POST' });
        const result = await response.json();
        if (result.success) {
            showAlert('User deleted successfully', 'success');
            loadUsers();
            loadStats();
        } else {
            showAlert(result.error, 'error');
        }
    } catch (error) {
        showAlert('Error deleting user: ' + error, 'error');
    }
}

function editContest(id, title, description, start, end, isActive, showLeaderboard) {
    document.getElementById('editContestId').value = id;
    document.getElementById('editContestTitle').value = title;
    document.getElementById('editContestDescription').value = description;

    // Convert datetime format from "YYYY-MM-DD HH:MM:SS" to "YYYY-MM-DDTHH:MM"
    // datetime-local input requires format: "YYYY-MM-DDTHH:MM"
    const formatDateTimeLocal = (dateStr) => {
        if (!dateStr) return '';
        // Remove seconds and replace space with T
        return dateStr.substring(0, 16).replace(' ', 'T');
    };

    document.getElementById('editContestStart').value = formatDateTimeLocal(start);
    document.getElementById('editContestEnd').value = formatDateTimeLocal(end);
    document.getElementById('editContestActive').checked = isActive;
    const showLeaderboardEl = document.getElementById('editContestShowLeaderboard');
    if (showLeaderboardEl) showLeaderboardEl.checked = showLeaderboard;

    document.getElementById('editContestModal').style.display = 'block';
}

async function toggleContest(id) {
    try {
        const response = await fetch(`/admin/toggle_contest/${id}`, { method: 'POST' });
        const result = await response.json();
        if (result.message) {
            showAlert(result.message, 'success');
            loadContests();
        } else {
            showAlert(result.error, 'error');
        }
    } catch (error) {
        showAlert('Error toggling contest: ' + error, 'error');
    }
}

async function loadContestOptions() {
    try {
        AdminDebug.log('Fetching /admin/contests');
        const response = await fetch('/admin/contests');
        const contests = await response.json();

        const updateSelect = (id) => {
            const select = document.getElementById(id);
            if (!select) return;
            select.innerHTML = '<option value="">No Contest</option>';
            contests.forEach(contest => {
                const option = document.createElement('option');
                option.value = contest.id;
                option.textContent = contest.title;
                select.appendChild(option);
            });
        };

        updateSelect('problemContestSelect');
        updateSelect('editProblemContest');
        updateSelect('filterContest');

        // Also update leaderboard contest select
        const leaderboardSelect = document.getElementById('contestSelectLeaderboard');
        if (leaderboardSelect) {
            leaderboardSelect.innerHTML = '<option value="">-- Select a Contest --</option>';
            contests.forEach(contest => {
                const option = document.createElement('option');
                option.value = contest.id;
                option.textContent = contest.title;
                leaderboardSelect.appendChild(option);
            });
        }

    } catch (error) {
        AdminDebug.error('Error loading contests', { error: String(error) });
    }
}

function collectStarterCode(isEdit = false) {
    const targetEditor = isEdit ? editStarterEditor : adminStarterEditor;
    const targetData = isEdit ? editStarterCodeData : starterCodeData;
    const targetLang = isEdit ? currentEditStarterLang : currentStarterLang;

    if (targetEditor) {
        targetData[targetLang] = targetEditor.getValue();
    }
    // Filter out empty entries
    const map = {};
    for (const [lang, code] of Object.entries(targetData)) {
        if (code && code.trim()) {
            map[lang] = code;
        }
    }
    return map;
}

function collectSolutionCode(isEdit = false) {
    const targetEditor = isEdit ? editSolutionEditor : adminSolutionEditor;
    const targetData = isEdit ? editSolutionCodeData : solutionCodeData;
    const targetLang = isEdit ? currentEditSolutionLang : currentSolutionLang;

    if (targetEditor) {
        targetData[targetLang] = targetEditor.getValue();
    }
    const map = {};
    for (const [lang, code] of Object.entries(targetData)) {
        if (code && code.trim()) {
            map[lang] = code;
        }
    }
    return map;
}

// Manual test case management for create form
let manualTestCases = [];
let currentImageTarget = 'create'; // 'create' or 'edit'

function openImageUploadModal(target) {
    currentImageTarget = target;
    document.getElementById('imageUploadModal').style.display = 'block';
    document.getElementById('imageFileInput').value = '';
    document.getElementById('imageWidth').value = '';
    document.getElementById('imageAlt').value = '';
    document.getElementById('imagePreviewContainer').style.display = 'none';
    document.getElementById('uploadProgress').style.display = 'none';
}

function closeImageUploadModal() {
    document.getElementById('imageUploadModal').style.display = 'none';
}

// Preview image when selected
document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('imageFileInput');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const preview = document.getElementById('imagePreview');
                    preview.src = event.target.result;
                    document.getElementById('imagePreviewContainer').style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
});

async function uploadAndInsertImage() {
    const fileInput = document.getElementById('imageFileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select an image file', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    const progressDiv = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('uploadProgressBar');
    const statusText = document.getElementById('uploadStatus');

    try {
        progressDiv.style.display = 'block';
        progressBar.style.width = '30%';
        statusText.textContent = 'Uploading...';

        const response = await fetch('/admin/upload_problem_image', {
            method: 'POST',
            body: formData
        });

        progressBar.style.width = '70%';

        const result = await response.json();

        if (result.success && result.url) {
            progressBar.style.width = '100%';
            statusText.textContent = 'Upload complete!';

            // Build image tag
            const width = document.getElementById('imageWidth').value;
            const alt = document.getElementById('imageAlt').value || 'Problem image';
            
            let imgTag = `<img src="${result.url}" alt="${alt}"`;
            if (width) {
                imgTag += ` width="${width}"`;
            }
            imgTag += ` style="max-width: 100%; height: auto; display: block; margin: 1rem 0;">`;

            // Insert into appropriate textarea
            const targetTextarea = currentImageTarget === 'create' 
                ? document.getElementById('createDescription')
                : document.getElementById('editDescription');

            if (targetTextarea) {
                const cursorPos = targetTextarea.selectionStart;
                const textBefore = targetTextarea.value.substring(0, cursorPos);
                const textAfter = targetTextarea.value.substring(cursorPos);
                targetTextarea.value = textBefore + '\n' + imgTag + '\n' + textAfter;
            }

            showAlert('Image uploaded and inserted successfully!', 'success');
            setTimeout(() => {
                closeImageUploadModal();
            }, 500);
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        progressBar.style.width = '0%';
        statusText.textContent = 'Upload failed';
        showAlert('Error uploading image: ' + error.message, 'error');
    }
}

function handleTestFileChange() {
    const fileInput = document.getElementById('createProblemTestFile');
    const hint = document.getElementById('fileUploadHint');
    
    if (fileInput && fileInput.files && fileInput.files.length > 0) {
        if (hint) hint.style.display = 'block';
        if (manualTestCases.length > 0) {
            showAlert('Note: File upload selected. Manual test cases will be ignored.', 'info');
        }
    } else {
        if (hint) hint.style.display = 'none';
    }
}

function addManualTestCase() {
    const input = document.getElementById('createTestInput').value.trim();
    const output = document.getElementById('createTestOutput').value.trim();
    const isSample = parseInt(document.getElementById('createTestType').value);

    if (!input || !output) {
        showAlert('Please enter both input and expected output', 'warning');
        return;
    }

    manualTestCases.push({
        input: input,
        expected_output: output,
        is_sample: isSample
    });

    // Clear inputs
    document.getElementById('createTestInput').value = '';
    document.getElementById('createTestOutput').value = '';
    document.getElementById('createTestType').value = '0';

    renderManualTestCases();
    showAlert(`Test case added! Total: ${manualTestCases.length}`, 'success');
    
    // Clear file input if manual tests are being used
    const fileInput = document.getElementById('createProblemTestFile');
    if (fileInput && fileInput.files && fileInput.files.length > 0) {
        fileInput.value = '';
        const hint = document.getElementById('fileUploadHint');
        if (hint) hint.style.display = 'none';
        showAlert('File upload cleared. Using manual test cases.', 'info');
    }
}

function removeManualTestCase(index) {
    manualTestCases.splice(index, 1);
    renderManualTestCases();
}

function renderManualTestCases() {
    const listDiv = document.getElementById('manualTestCasesList');
    if (!listDiv) return;

    if (manualTestCases.length === 0) {
        listDiv.innerHTML = '<p style="color: var(--text-muted); font-size: 0.75rem; text-align: center; padding: 0.5rem;">No test cases added yet</p>';
        return;
    }

    listDiv.innerHTML = `
        <div style="margin-bottom: 1rem;">
            <p style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                <strong>${manualTestCases.length}</strong> test case(s) added
            </p>
            <table class="table" style="font-size: 0.75rem;">
                <thead>
                    <tr>
                        <th style="width: 60px;">Type</th>
                        <th>Input</th>
                        <th>Expected Output</th>
                        <th style="width: 60px; text-align: right;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${manualTestCases.map((tc, idx) => `
                        <tr>
                            <td>
                                <span class="badge ${tc.is_sample ? 'badge-primary' : 'badge-success'}" style="font-size: 9px;">
                                    ${tc.is_sample ? 'Sample' : 'Hidden'}
                                </span>
                            </td>
                            <td style="font-family: monospace; font-size: 0.7rem;">${tc.input.substring(0, 30)}${tc.input.length > 30 ? '...' : ''}</td>
                            <td style="font-family: monospace; font-size: 0.7rem;">${tc.expected_output.substring(0, 30)}${tc.expected_output.length > 30 ? '...' : ''}</td>
                            <td style="text-align: right;">
                                <button onclick="removeManualTestCase(${idx})" class="btn btn-sm btn-danger" style="padding: 2px 6px; font-size: 10px;">×</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function resetContest() {
    const confirmed = await showModal('Reset Contest', 'Clear all submissions? This cannot be undone.', { showCancel: true, confirmText: 'Clear Submissions' });
    if (!confirmed) return;
    try {
        const response = await fetch('/admin/reset_contest', { method: 'POST' });
        const result = await response.json();
        showAlert(result.message || result.error, result.success ? 'success' : 'error');
        if (result.message) {
            loadSubmissions();
            loadStats();
        }
    } catch (error) {
        showAlert('Error resetting contest: ' + error, 'error');
    }
}

async function clearStudents() {
    const confirmed = await showModal('Clear Students', 'Delete all student accounts? This cannot be undone.', { showCancel: true, confirmText: 'Delete All Students' });
    if (!confirmed) return;
    try {
        const response = await fetch('/admin/clear_students', { method: 'POST' });
        const result = await response.json();
        showAlert(result.message || result.error, result.success ? 'success' : 'error');
        if (result.message) {
            loadUsers();
            loadStats();
        }
    } catch (error) {
        showAlert('Error clearing students: ' + error, 'error');
    }
}


async function viewSubmissionCode(submissionId, username, problemTitle, language) {
    try {
        const response = await fetch(`/admin/view_submission/${submissionId}`);
        const data = await response.json();

        if (data.error) {
            showAlert(data.error, 'error');
            return;
        }

        const escapeHtml = (text) => {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };

        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 9999; display: flex; align-items: center; justify-content: center;';

        const modalContent = document.createElement('div');
        modalContent.style.cssText = 'background: #0f172a; color: white; padding: 30px; border-radius: 10px; max-width: 90%; max-height: 90%; overflow: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);';

        modalContent.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
                <div>
                    <h2 style="margin: 0; color: #fff;">Submission #${submissionId}</h2>
                    <p style="margin: 5px 0 0 0; color: #cbd5f5;">
                        <strong>User:</strong> ${escapeHtml(username)} | 
                        <strong>Problem:</strong> ${escapeHtml(problemTitle)} | 
                        <strong>Language:</strong> ${escapeHtml(language)} |
                        <strong>Verdict:</strong> <span style="font-weight: 700;">${escapeHtml(data.verdict)}</span>
                    </p>
                </div>
                <button onclick="this.closest('div[style*=\'position: fixed\']').remove()" 
                        style="background: #dc3545; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 14px;">
                    Close
                </button>
            </div>
            <div style="margin-bottom: 15px;">
                <h3 style="margin: 0 0 10px 0; color: #fff;">Code</h3>
                <pre style="background: #0b1220; color: #e2e8f0; padding: 15px; border-radius: 6px; overflow-x: auto; border: 1px solid rgba(255,255,255,0.08);">${escapeHtml(data.code || '')}</pre>
            </div>
            <div>
                <h3 style="margin: 0 0 10px 0; color: #fff;">Output</h3>
                <pre style="background: #0b1220; color: #e2e8f0; padding: 15px; border-radius: 6px; overflow-x: auto; border: 1px solid rgba(255,255,255,0.08); max-height: 300px;">${escapeHtml(data.output || '')}</pre>
            </div>
        `;

        modal.appendChild(modalContent);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
        document.body.appendChild(modal);
    } catch (error) {
        showAlert('Error loading submission: ' + error, 'error');
    }
}


function syncProblemMode() {
    const type = document.getElementById('problemTypeSelect');
    const mode = document.getElementById('problemModeSelect');
    if (!type || !mode) return;
    if (type.value === 'coding') {
        mode.value = 'function';
    } else if (type.value === 'debugging') {
        mode.value = 'stdin';
    }
}


async function loadFilteredSubmissions() {
    const list = document.getElementById('filteredSubmissions');
    if (!list) return;
    const params = new URLSearchParams({
        username: document.getElementById('filterUsername')?.value || '',
        problem: document.getElementById('filterProblem')?.value || '',
        verdict: document.getElementById('filterVerdict')?.value || '',
        contest_id: document.getElementById('filterContest')?.value || '',
        limit: document.getElementById('filterLimit')?.value || '50'
    });
    try {
        AdminDebug.log('Fetching /api/admin/submissions_search', Object.fromEntries(params));
        const response = await fetch(`/api/admin/submissions_search?${params.toString()}`);
        const subs = await response.json();
        if (subs.error) {
            list.innerHTML = `<p style="color: var(--danger);">${subs.error}</p>`;
            return;
        }
        if (subs.length === 0) {
            list.innerHTML = '<p style="text-align:center; color: var(--text-muted);">No submissions found.</p>';
            return;
        }
        list.innerHTML = `
            <table class="table" style="width: 100%; font-size: 0.875rem;">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>User</th>
                        <th>Problem</th>
                        <th>Verdict</th>
                        <th style="text-align: right;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${subs.map(s => {
            const verdictColor = s.verdict === 'AC' ? 'var(--success)' :
                s.verdict === 'PENDING' ? 'var(--warning)' : 'var(--danger)';
            const safeUser = escapeJsString(s.username);
            const safeProblem = escapeJsString(s.problem_title);
            const safeLang = escapeJsString(s.language);
            return `
                            <tr>
                                <td>${new Date(s.submitted_at + ' Z').toLocaleString()}</td>
                                <td>${s.username}</td>
                                <td>${s.problem_title}</td>
                                <td><span style="color: ${verdictColor}; font-weight: 600;">${s.verdict}</span></td>
                                <td style="text-align: right;">
                                    <button onclick="viewSubmissionCode(${s.id}, '${safeUser}', '${safeProblem}', '${safeLang}')" class="btn btn-sm btn-outline" style="padding: 2px 8px; font-size: 11px;">View Code</button>
                                </td>
                            </tr>
                        `;
        }).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        AdminDebug.error('Error loading filtered submissions', { error: String(error) });
        list.innerHTML = `<p style="color: var(--danger);">Error loading submissions</p>`;
    }
}

function initAdminHandlers() {
    const editContestForm = document.getElementById('editContestForm');
    if (editContestForm) {
        editContestForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('editContestId').value;
            const data = {
                title: document.getElementById('editContestTitle').value,
                description: document.getElementById('editContestDescription').value,
                start_time: document.getElementById('editContestStart').value,
                end_time: document.getElementById('editContestEnd').value,
                is_active: document.getElementById('editContestActive').checked,
                show_leaderboard: document.getElementById('editContestShowLeaderboard')?.checked ?? true
            };

            try {
                const response = await fetch(`/admin/edit_contest/${id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                showAlert(result.message || result.error, result.message ? 'success' : 'error');
                if (result.message) {
                    document.getElementById('editContestModal').style.display = 'none';
                    loadContests();
                }
            } catch (error) {
                showAlert('Error updating contest: ' + error, 'error');
            }
        });
    }

    // createContestForm listener removed - handled by contest_management.js

    const bulkCreateUserForm = document.getElementById('bulkCreateUserForm');
    if (bulkCreateUserForm) {
        bulkCreateUserForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            try {
                const response = await fetch('/admin/bulk_create_users', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.errors && result.errors.length > 0) {
                    showModal('Bulk Creation Results', `Created: ${result.total_created}\n\nErrors:\n${result.errors.join('\n')}`);
                } else {
                    showAlert(`Successfully created ${result.total_created} users.`, 'success');
                }

                if (result.total_created > 0) {
                    e.target.reset();
                    loadUsers();
                    loadStats();
                }
            } catch (error) {
                showAlert('Error creating users: ' + error, 'error');
            }
        });
    }

    const bulkResetPasswordForm = document.getElementById('bulkResetPasswordForm');
    if (bulkResetPasswordForm) {
        bulkResetPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            const roleText = data.role === 'all' ? 'ALL non-admin users' : 'ALL STUDENTS';
            const confirmed = await showModal('Bulk Password Reset', `⚠️ WARNING: This will reset passwords for ${roleText}!\n\nNew password: ${data.new_password}\n\nAre you sure?`, { showCancel: true, confirmText: 'Reset All' });
            if (!confirmed) return;

            try {
                const response = await fetch('/admin/bulk_reset_passwords', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();

                if (result.success) {
                    showModal('Passwords Reset', `✅ Success!\n\nReset passwords for ${result.count} users:\n${result.users.join(', ')}\n\nNew password: ${data.new_password}`);
                    e.target.reset();
                } else {
                    showAlert(result.error || 'Error resetting passwords', 'error');
                }
            } catch (error) {
                showAlert('Error resetting passwords: ' + error, 'error');
            }
        });
    }

    const uploadTestCasesForm = document.getElementById('uploadTestCasesForm');
    if (uploadTestCasesForm) {
        uploadTestCasesForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const problemId = document.getElementById('editProblemId').value;
            try {
                const response = await fetch(`/admin/problem/${problemId}/upload_test_cases`, {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                showAlert(result.message || result.error, result.success !== false ? 'success' : 'error');
                if (result.message) {
                    if (typeof loadTestCases === 'function') {
                        loadTestCases(problemId);
                    }
                }
            } catch (error) {
                showAlert('Error uploading test cases: ' + error, 'error');
            }
        });
    }

    const typeSelect = document.getElementById('problemTypeSelect');
    if (typeSelect) {
        typeSelect.addEventListener('change', syncProblemMode);
        syncProblemMode();
    }

    // Initialize manual test cases list
    renderManualTestCases();

    const createProblemForm = document.getElementById('createProblemForm');
    if (createProblemForm) {
        createProblemForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Validate form
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            // Check all required fields
            const requiredFields = [
                { name: 'title', label: 'Problem Title' },
                { name: 'problem_type', label: 'Problem Type' },
                { name: 'total_marks', label: 'Total Marks' },
                { name: 'problem_mode', label: 'Problem Mode' },
                { name: 'function_name', label: 'Function Name' }
            ];

            for (const field of requiredFields) {
                if (data[field.name] === '' || data[field.name] === undefined) {
                    showAlert(`❌ ${field.label} is required!\n\nPlease fill in all required fields marked with *`, 'warning');
                    const input = e.target.querySelector(`[name="${field.name}"]`);
                    if (input) input.focus();
                    return;
                }
            }

            // Validate total marks
            const totalMarks = parseInt(data.total_marks);
            if (isNaN(totalMarks) || totalMarks < 1 || totalMarks > 1000) {
                showAlert('❌ Total Marks must be between 1 and 1000', 'warning');
                e.target.querySelector('[name="total_marks"]')?.focus();
                return;
            }

            // Validate test cases - either file upload OR manual test cases
            const testFileInput = document.getElementById('createProblemTestFile');
            const hasFileUpload = testFileInput && testFileInput.files && testFileInput.files.length > 0;
            const hasManualTests = manualTestCases.length > 0;

            if (!hasFileUpload && !hasManualTests) {
                showAlert('❌ Test cases are required!\n\nYou must either upload a test case file OR add test cases manually.\nPlease use one of the two options provided.', 'warning');
                return;
            }

            if (hasFileUpload && hasManualTests) {
                showAlert('⚠️ Please use only ONE method!\n\nYou can either upload a file OR add test cases manually, not both.\nPlease clear one option before proceeding.', 'warning');
                return;
            }

            // Collect starter and solution code from Monaco editors
            const starterMap = collectStarterCode();
            const solutionMap = collectSolutionCode();
            
            // Prepare data with multi-language support
            data.starter_code_dict = starterMap;
            if (Object.keys(solutionMap).length > 0) {
                data.solution_code_dict = solutionMap;
            }
            data.difficulty = data.difficulty || 'easy';

            // Ensure total_marks is a number
            data.total_marks = totalMarks;

            try {
                const response = await fetch('/admin/create_problem', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();

                if (result.message && result.problem_id) {
                    // Handle test cases based on method chosen
                    if (hasFileUpload) {
                        // Upload test cases from file
                        const testFormData = new FormData();
                        testFormData.append('file', testFileInput.files[0]);

                        try {
                            const uploadResponse = await fetch(`/admin/problem/${result.problem_id}/upload_test_cases`, {
                                method: 'POST',
                                body: testFormData
                            });

                            if (!uploadResponse.ok) {
                                throw new Error(`Test case upload failed with status: ${uploadResponse.status}`);
                            }

                            const uploadResult = await uploadResponse.json();

                            if (uploadResult.error) {
                                throw new Error(uploadResult.error);
                            }

                            showAlert('✅ Problem created successfully!', 'success');
                            showModal('Success', 'Problem created and test cases uploaded successfully!');
                        } catch (uploadError) {
                            console.error('Test case upload error:', uploadError);
                            showAlert('⚠️ Problem created but test case upload failed!', 'warning');
                            showModal('Warning',
                                'Problem created but test case upload failed!\n\n' +
                                'Error: ' + uploadError.message + '\n\n' +
                                'Please upload test cases manually for problem ID: ' + result.problem_id);
                        }
                    } else if (hasManualTests) {
                        // Add manual test cases one by one
                        try {
                            let successCount = 0;
                            for (const testCase of manualTestCases) {
                                const tcResponse = await fetch(`/admin/problem/${result.problem_id}/add_test_case`, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify(testCase)
                                });
                                const tcResult = await tcResponse.json();
                                if (tcResult.message) {
                                    successCount++;
                                }
                            }
                            
                            if (successCount === manualTestCases.length) {
                                showAlert('✅ Problem created successfully!', 'success');
                                showModal('Success', `Problem created with ${successCount} test case(s)!`);
                                manualTestCases = [];
                                renderManualTestCases();
                            } else {
                                showAlert('⚠️ Problem created but some test cases failed!', 'warning');
                            }
                        } catch (tcError) {
                            console.error('Manual test case error:', tcError);
                            showAlert('⚠️ Problem created but test case addition failed!', 'warning');
                        }
                    }

                    // Reset form and editor
                    e.target.reset();
                    if (testFileInput) testFileInput.value = '';

                    // Reset starter code data
                    starterCodeData = {};
                    if (adminStarterEditor) {
                        adminStarterEditor.setValue(DEFAULT_BOILERPLATE.python || '');
                    }
                    // Reset solution code data
                    solutionCodeData = { python: '', cpp: '', java: '', c: '' };
                    if (adminSolutionEditor) {
                        adminSolutionEditor.setValue('');
                    }

                    // Refresh lists
                    loadStats();
                    if (typeof loadAllProblems === 'function') loadAllProblems();
                } else {
                    showAlert(result.error || 'Error creating problem', 'error');
                }
            } catch (error) {
                console.error('Problem creation error:', error);
                showAlert('Error creating problem: ' + error.message, 'error');
            }
        });
    }

    const createUserForm = document.getElementById('createUserForm');
    if (createUserForm) {
        createUserForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            try {
                const response = await fetch('/admin/create_user', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                showAlert(result.message || result.error, result.success ? 'success' : 'error');
                if (result.message) {
                    e.target.reset();
                    loadUsers();
                    loadStats();
                }
            } catch (error) {
                showAlert('Error creating user: ' + error, 'error');
            }
        });
    }

    const submissionFilterForm = document.getElementById('submissionFilterForm');
    if (submissionFilterForm) {
        submissionFilterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            loadFilteredSubmissions();
        });
    }
    const clearFilters = document.getElementById('clearFilters');
    if (clearFilters) {
        clearFilters.addEventListener('click', () => {
            document.getElementById('filterUsername').value = '';
            document.getElementById('filterProblem').value = '';
            document.getElementById('filterVerdict').value = '';
            document.getElementById('filterContest').value = '';
            document.getElementById('filterLimit').value = '50';
            loadFilteredSubmissions();
        });
    }

    const broadcastForm = document.getElementById('broadcastForm');
    if (broadcastForm) {
        broadcastForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const message = e.target.elements.message.value;
            if (socket && socket.connected) {
                socket.emit('broadcast', { message });
                e.target.reset();
                showAlert('Broadcast message sent!', 'success');
            } else {
                showAlert('WebSocket not connected. Cannot send broadcast.', 'error');
            }
        });
    }

    const contestSettingsForm = document.getElementById('contestSettingsForm');
    if (contestSettingsForm) {
        contestSettingsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                leaderboard_enabled: formData.get('leaderboard_enabled') ? 1 : 0,
                show_scores_to_students: formData.get('show_scores_to_students') ? 1 : 0
            };
            try {
                const response = await fetch('/admin/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                showAlert(result.message || result.error, result.success ? 'success' : 'error');
                if (result.success) loadSettings();
            } catch (error) {
                showAlert('Error updating settings: ' + error, 'error');
            }
        });
    }
}

window.addEventListener('DOMContentLoaded', () => {
    AdminDebug.init();
    loadContestOptions();
    const hash = window.location.hash.replace('#', '').trim();
    if (hash) {
        const navItem = document.querySelector(`.nav-item[data-section="${hash}"]`);
        showSection(hash, navItem || undefined);
    } else {
        refreshCurrentSection();
    }
    initAdminHandlers();
    initAdminMonaco();

    // Auto-refresh live metrics every 3 seconds
    setInterval(() => {
        const activeSection = document.querySelector('.content-section.active')?.id;
        if (activeSection === 'overview') {
            loadStats(); // Update live metrics
        }
    }, 3000);

    // Auto-refresh full overview every 15 seconds
    if (ENABLE_POLLING) {
        setInterval(() => {
            const activeSection = document.querySelector('.content-section.active')?.id;
            if (activeSection === 'overview') {
                refreshCurrentSection();
            }
        }, 15000);
    }
});

window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '').trim();
    if (!hash) return;
    const navItem = document.querySelector(`.nav-item[data-section="${hash}"]`);
    showSection(hash, navItem || undefined);
});

// ============================================================================
// Leaderboard and Scorecard Functions
// ============================================================================

async function loadDetailedLeaderboard() {
    try {
        const response = await fetch('/admin/detailed_leaderboard');
        const data = await response.json();

        if (data.error) {
            showAlert(data.error, 'error');
            return;
        }

        displayDetailedLeaderboard(data);
    } catch (error) {
        console.error('Error loading detailed leaderboard:', error);
        showAlert('Failed to load leaderboard', 'error');
    }
}

function displayDetailedLeaderboard(data) {
    const container = document.getElementById('detailedLeaderboardContainer');
    if (!container) return;

    if (data.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">No users found</p>';
        return;
    }

    // Get all contest names
    const contestNames = data.length > 0 ? Object.keys(data[0].contests) : [];

    let html = `
        <div style="overflow-x: auto; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(0,0,0,0.2);">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.8rem; table-layout: fixed;">
                <thead>
                    <tr style="background: rgba(255,255,255,0.05); border-bottom: 2px solid var(--border-color);">
                        <th style="padding: 12px; text-align: left; width: 60px;">Rank</th>
                        <th style="padding: 12px; text-align: left; width: 140px;">Username</th>
                        <th style="padding: 12px; text-align: right; width: 100px;">Total Points</th>
                        <th style="padding: 12px; text-align: right; width: 100px;">Highest</th>
                        <th style="padding: 12px; text-align: right; width: 90px;">Solved</th>
                        <th style="padding: 12px; text-align: right; width: 80px;">Time</th>
    `;

    // Add contest columns
    contestNames.forEach(contest => {
        html += `<th style="padding: 12px; text-align: right; width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${contest}">${contest}</th>`;
    });

    html += `
                        <th style="padding: 12px; text-align: center; width: 120px;">Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    data.forEach((user, idx) => {
        const rowColor = idx % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent';
        const totalSeconds = user.total_time_penalty || 0;
        const h = Math.floor(totalSeconds / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = totalSeconds % 60;
        const timeStr = h > 0
            ? `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
            : `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        html += `
            <tr style="background: ${rowColor}; border-bottom: 1px solid var(--border-color);">
                <td style="padding: 12px; text-align: center;">${user.rank}</td>
                <td style="padding: 12px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.username}</td>
                <td style="padding: 12px; text-align: right; font-weight: 600; color: var(--primary-color);">${user.total_points}</td>
                <td style="padding: 12px; text-align: right; font-weight: 600; color: #fbbf24;">${user.highest_score}</td>
                <td style="padding: 12px; text-align: right;">${user.total_problems_solved}</td>
                <td style="padding: 12px; text-align: right; color: var(--text-muted); font-family: monospace;">${timeStr}</td>
        `;

        // Add contest scores
        contestNames.forEach(contest => {
            const contestData = user.contests[contest];
            html += `
                <td style="padding: 12px; text-align: right; white-space: nowrap;">
                    <span style="color: var(--text-secondary);">${contestData.points}</span>
                    <span style="color: var(--text-muted); font-size: 0.85em;"> (${contestData.solved})</span>
                </td>
            `;
        });

        html += `
                <td style="padding: 12px; text-align: center;">
                    <button onclick="viewUserScorecard(${user.user_id}, '${user.username}')" 
                            style="padding: 6px 10px; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.75rem; white-space: nowrap;">
                        View Details
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

async function viewUserScorecard(userId, username, contestId = null) {
    try {
        let url = `/admin/user_scorecard/${userId}`;
        if (contestId) {
            url += `?contest_id=${contestId}`;
        }
        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            showAlert(data.error, 'error');
            return;
        }

        displayUserScorecard(data, contestId);
    } catch (error) {
        console.error('Error loading user scorecard:', error);
        showAlert('Failed to load scorecard', 'error');
    }
}

function displayUserScorecard(data, filterContestId = null) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.95);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        overflow-y: auto;
        padding: 20px;
    `;

    let html = `
        <div style="background: #1a1d29; border-radius: 8px; max-width: 1200px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); position: relative;">
            <button onclick="this.parentElement.remove()" class="modal-close-btn">&times;</button>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <h2 style="margin: 0; color: #e5e7eb;">Scorecard: ${data.username}</h2>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px;">
                <div style="background: rgba(255,255,255,0.08); padding: 15px; border-radius: 6px;">
                    <div style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 5px;">Total Points</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #60a5fa;">${data.total_points}</div>
                </div>
                <div style="background: rgba(255,255,255,0.08); padding: 15px; border-radius: 6px;">
                    <div style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 5px;">Problems Solved</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #4ade80;">${data.total_problems_solved}</div>
                </div>
                <div style="background: rgba(255,255,255,0.08); padding: 15px; border-radius: 6px;">
                    <div style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 5px;">Total Submissions</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #d1d5db;">${data.total_submissions}</div>
                </div>
                <div style="background: rgba(255,255,255,0.08); padding: 15px; border-radius: 6px;">
                    <div style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 5px;">AC Submissions</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #4ade80;">${data.ac_submissions}</div>
                </div>
            </div>
    `;

    // Add per-contest breakdown (filter if contestId provided)
    const contestsToShow = filterContestId
        ? data.contests.filter(c => c.contest_id === filterContestId)
        : data.contests;

    contestsToShow.forEach(contest => {
        html += `
            <div style="margin-bottom: 30px; background: rgba(255,255,255,0.06); padding: 20px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
                <h3 style="margin: 0 0 15px 0; color: #e5e7eb; display: flex; justify-content: space-between; align-items: center;">
                    <span>${contest.contest_title}</span>
                    <span style="font-size: 0.9rem; color: #60a5fa;">
                        ${contest.total_points} points | ${contest.problems_solved} solved
                    </span>
                </h3>
                
                <div style="display: grid; gap: 15px;">
        `;

        contest.problems.forEach(problem => {
            const difficultyColor = problem.difficulty === 'easy' ? '#4ade80' :
                problem.difficulty === 'medium' ? '#fbbf24' : '#f87171';
            const solvedIcon = problem.solved ? '✓' : '✗';
            const solvedColor = problem.solved ? '#4ade80' : '#f87171';

            html += `
                <div style="background: rgba(255,255,255,0.08); padding: 15px; border-radius: 6px; border-left: 3px solid ${difficultyColor};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div>
                            <span style="font-weight: 500; color: #e5e7eb;">${problem.problem_title}</span>
                            <span style="margin-left: 10px; padding: 2px 8px; background: ${difficultyColor}; color: #000; border-radius: 3px; font-size: 0.75rem; font-weight: 600;">
                                ${problem.difficulty.toUpperCase()}
                            </span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.2rem; color: ${solvedColor}; margin-right: 10px;">${solvedIcon}</span>
                            <span style="font-weight: 600; color: #60a5fa;">${problem.best_points}/${problem.total_marks}</span>
                            <span style="color: #9ca3af; font-size: 0.85rem; margin-left: 5px;">(${problem.attempts} attempts)</span>
                        </div>
                    </div>
            `;

            if (problem.submissions.length > 0) {
                html += `
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.15);">
                        <div style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 8px;">Submissions:</div>
                        <div style="display: grid; gap: 8px;">
                `;

                problem.submissions.slice(0, 5).forEach((sub, idx) => {
                    const verdictColor = sub.verdict === 'AC' ? '#4ade80' :
                        sub.verdict === 'WA' ? '#fbbf24' : '#f87171';
                    const submissionId = `submission_${problem.problem_id}_${idx}`;
                    const codeId = `code_${problem.problem_id}_${idx}`;
                    const testInfo = sub.tests_total ? `${sub.tests_passed || 0}/${sub.tests_total}` : 'N/A';

                    html += `
                        <div style="background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden;">
                            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; padding: 8px; cursor: pointer;" 
                                 onclick="document.getElementById('${submissionId}').style.display = document.getElementById('${submissionId}').style.display === 'none' ? 'block' : 'none'">
                                <span style="color: #9ca3af;">${new Date(sub.submitted_at + ' Z').toLocaleString()}</span>
                                <span style="color: ${verdictColor}; font-weight: 600;">${sub.verdict}</span>
                                <span style="color: #d1d5db;">${sub.language}</span>
                                <span style="color: #60a5fa;">${sub.points_awarded || 0} pts</span>
                                <span style="color: #9ca3af; font-size: 0.75rem;">Tests: ${testInfo}</span>
                                <span style="color: #60a5fa; font-size: 0.75rem;">▼ Details</span>
                            </div>
                            <div id="${submissionId}" style="display: none; padding: 12px; background: rgba(0,0,0,0.3); border-top: 1px solid rgba(255,255,255,0.1);">
                                <div style="margin-bottom: 10px;">
                                    <div style="font-size: 0.75rem; color: #9ca3af; margin-bottom: 4px;">Test Cases: <span style="color: ${verdictColor}; font-weight: 600;">${testInfo} passed</span></div>
                                    ${sub.output ? `<div style="font-size: 0.75rem; color: #9ca3af; margin-bottom: 4px;">Output: <span style="color: #d1d5db;">${sub.output.substring(0, 100)}${sub.output.length > 100 ? '...' : ''}</span></div>` : ''}
                                </div>
                                <div style="margin-top: 8px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                        <span style="font-size: 0.75rem; color: #9ca3af;">Code:</span>
                                        <button onclick="
                                            const code = document.getElementById('${codeId}');
                                            const btn = this;
                                            if (code.style.display === 'none') {
                                                code.style.display = 'block';
                                                btn.textContent = 'Hide Code';
                                            } else {
                                                code.style.display = 'none';
                                                btn.textContent = 'Show Code';
                                            }
                                        " style="padding: 2px 8px; background: #60a5fa; color: #000; border: none; border-radius: 3px; cursor: pointer; font-size: 0.7rem;">
                                            Show Code
                                        </button>
                                    </div>
                                    <pre id="${codeId}" style="display: none; background: #0d1117; color: #e5e7eb; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 0.75rem; margin: 0; border: 1px solid rgba(255,255,255,0.1); max-height: 300px; overflow-y: auto;"><code>${sub.code ? sub.code.replace(/</g, '&lt;').replace(/>/g, '&gt;') : 'No code available'}</code></pre>
                                </div>
                            </div>
                        </div>
                    `;
                });

                if (problem.submissions.length > 5) {
                    html += `<div style="font-size: 0.75rem; color: #9ca3af; text-align: center; margin-top: 5px;">... and ${problem.submissions.length - 5} more submissions</div>`;
                }

                html += `
                        </div>
                    </div>
                `;
            }

            html += `</div>`;
        });

        html += `
                </div>
            </div>
        `;
    });

    html += `
        </div>
    `;

    modal.innerHTML = html;
    document.body.appendChild(modal);

    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

async function loadContestLeaderboard(contestId) {
    try {
        const response = await fetch(`/admin/contest_leaderboard/${contestId}`);
        const data = await response.json();

        if (data.error) {
            showAlert(data.error, 'error');
            return;
        }

        displayContestLeaderboard(data);
    } catch (error) {
        console.error('Error loading contest leaderboard:', error);
        showAlert('Failed to load contest leaderboard', 'error');
    }
}

function displayContestLeaderboard(data) {
    const container = document.getElementById('contestLeaderboardContainer');
    if (!container) return;

    let html = `
        <h3 style="margin: 0 0 20px 0; color: var(--text-primary);">${data.contest_title} - Leaderboard</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
            <thead>
                <tr style="background: rgba(255,255,255,0.05); border-bottom: 2px solid var(--border-color);">
                    <th style="padding: 12px; text-align: left;">Rank</th>
                    <th style="padding: 12px; text-align: left;">Username</th>
                    <th style="padding: 12px; text-align: right;">Points</th>
                    <th style="padding: 12px; text-align: right;">Solved</th>
                    <th style="padding: 12px; text-align: right;">TimeTaken</th>
                    <th style="padding: 12px; text-align: right;">Attempted</th>
                    <th style="padding: 12px; text-align: center;">Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    data.leaderboard.forEach((user, idx) => {
        const rowColor = idx % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent';
        const totalSeconds = user.time_penalty || 0;
        const h = Math.floor(totalSeconds / 3600);
        const m = Math.floor((totalSeconds % 3600) / 60);
        const s = totalSeconds % 60;
        const timeStr = h > 0
            ? `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
            : `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        html += `
            <tr style="background: ${rowColor}; border-bottom: 1px solid var(--border-color);">
                <td style="padding: 12px;">${user.rank}</td>
                <td style="padding: 12px; font-weight: 500;">${user.username}</td>
                <td style="padding: 12px; text-align: right; font-weight: 600; color: var(--primary-color);">${user.points}</td>
                <td style="padding: 12px; text-align: right; color: var(--success-color);">${user.problems_solved}</td>
                <td style="padding: 12px; text-align: right; color: var(--text-muted); font-family: monospace;">${timeStr}</td>
                <td style="padding: 12px; text-align: right; color: var(--text-muted);">${user.problems_attempted}</td>
                <td style="padding: 12px; text-align: center;">
                    <button onclick="viewUserScorecard(${user.user_id}, '${user.username}', ${data.contest_id})" 
                            style="padding: 6px 12px; background: var(--primary-color); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85rem;">
                        View Details
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// Make functions globally available
window.loadDetailedLeaderboard = loadDetailedLeaderboard;
window.viewUserScorecard = viewUserScorecard;
window.loadContestLeaderboard = loadContestLeaderboard;
