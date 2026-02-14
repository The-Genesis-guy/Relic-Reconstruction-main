// Contest Management JavaScript - Enhanced UI (Permanent Fix: No Emojis, Dark Theme)
// Add this script to admin.html

async function loadContests() {
    try {
        const response = await fetch('/admin/contests');
        const contests = await response.json();
        const list = document.getElementById('contestsList');

        if (contests.length === 0) {
            list.innerHTML = '<p class="text-muted">No contests created yet.</p>';
            return;
        }

        // Build safe JS string literals to embed inside single-quoted HTML attributes.
        // - JSON.stringify handles escaping for JS
        // - Escape '&' to prevent HTML entity decoding (e.g. "&quot;" -> '"') before JS runs
        // - Escape "'" so it can't break out of a single-quoted attribute
        const onclickJson = (v) =>
            JSON.stringify(v == null ? '' : String(v))
                .replace(/&/g, '&amp;')
                .replace(/'/g, '&#39;');

        list.innerHTML = `
            <table class="table" style="width: 100%; font-size: 0.825rem; table-layout: fixed;">
                <thead>
                    <tr>
                        <th style="width: 100px;">Status</th>
                        <th style="width: 25%;">Title</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th style="width: 80px;">Problems</th>
                        <th style="text-align: right; width: 420px;">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${contests.map(c => {
            const now = new Date();
            const start = new Date(c.start_time);
            const end = new Date(c.end_time);
            let statusBadge = '';
            if (!c.is_active) statusBadge = '<span class="badge badge-danger" style="font-size: 10px;">Inactive</span>';
            else if (now < start) statusBadge = '<span class="badge badge-primary" style="font-size: 10px;">Upcoming</span>';
            else if (now > end) statusBadge = '<span class="badge badge-danger" style="font-size: 10px;">Ended</span>';
            else statusBadge = '<span class="badge badge-success" style="font-size: 10px;">Running</span>';

            const formatOptions = { month: 'numeric', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' };
            const startStr = start.toLocaleString(undefined, formatOptions);
            const endStr = end.toLocaleString(undefined, formatOptions);

            const titleArg = onclickJson(c.title);
            const descArg = onclickJson(c.description || '');
            const startArg = onclickJson(c.start_time);
            const endArg = onclickJson(c.end_time);

            return `
                        <tr>
                            <td>${statusBadge}</td>
                            <td style="font-weight: 500; color: var(--text-primary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${c.title}</td>
                            <td style="color: var(--text-secondary); opacity: 0.8;">${startStr}</td>
                            <td style="color: var(--text-secondary); opacity: 0.8;">${endStr}</td>
                            <td style="text-align: center;">${c.problem_count}</td>
                            <td style="text-align: right;">
                                <div style="display: flex; gap: 0.4rem; justify-content: flex-end; align-items: center; white-space: nowrap;">
                                    <button onclick="toggleContestProblems(${c.id})" class="btn btn-sm btn-outline" style="padding: 4px 10px; font-size: 11px;">Manage Problems</button>
                                    <button onclick='editContest(${c.id}, ${titleArg}, ${descArg}, ${startArg}, ${endArg}, ${c.is_active}, ${c.show_leaderboard})' class="btn btn-sm btn-outline" style="padding: 4px 10px; font-size: 11px;">Edit</button>
                                    <button onclick="toggleContest(${c.id})" class="btn btn-sm ${c.is_active ? 'btn-danger' : 'btn-success'}" style="padding: 4px 10px; font-size: 11px; min-width: 80px;">
                                        ${c.is_active ? 'Deactivate' : 'Activate'}
                                    </button>
                                    <button onclick="deleteContest(${c.id})" class="btn btn-sm" style="padding: 4px 10px; font-size: 11px; background: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.2);">
                                        Delete
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr id="contest-problems-row-${c.id}" style="display: none;">
                            <td colspan="6">
                                <div id="problems-list-${c.id}" style="padding: 1rem; background: rgba(0,0,0,0.15); border-radius: 8px; margin: 0.5rem 0;">
                                    <div class="spinner" style="width: 20px; height: 20px; margin: 10px auto;"></div>
                                </div>
                            </td>
                        </tr>
                    `;
        }).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Error loading contests:', error);
        document.getElementById('contestsList').textContent = 'Error loading contests.';
    }
}

function toggleContestProblems(contestId) {
    const row = document.getElementById(`contest-problems-row-${contestId}`);
    if (!row) return;
    const isVisible = row.style.display === 'table-row';
    row.style.display = isVisible ? 'none' : 'table-row';
    if (!isVisible) {
        loadContestProblems(contestId);
    }
}

async function loadAllProblems() {
    const listDiv = document.getElementById('allProblemsList');
    if (!listDiv) return;
    try {
        const response = await fetch('/admin/problems_list');
        const problems = await response.json();
        if (problems.length === 0) {
            listDiv.innerHTML = `<p style="text-align: center; color: var(--text-muted); font-size: 0.875rem; padding: 1rem;">No problems created yet.</p>`;
            return;
        }
        listDiv.innerHTML = `
            <table class="table" style="font-size: 0.825rem; width: 100%; table-layout: fixed;">
                <thead>
                    <tr>
                        <th style="width: 40%;">Title</th>
                        <th style="width: 15%;">Contest</th>
                        <th style="width: 100px;">Status</th>
                        <th style="text-align: right; width: 320px;">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${problems.map(p => `
                        <tr>
                            <td style="text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
                                <div style="font-weight: 600; color: var(--text-primary);">${p.title}</div>
                                <div style="font-size: 0.75rem; color: var(--text-muted); opacity: 0.8;">${p.problem_type} • Round ${p.round_number || 1}</div>
                            </td>
                            <td style="color: var(--text-secondary); opacity: 0.8;">${p.contest_id || 'Unassigned'}</td>
                            <td>
                                <span class="badge ${p.enabled ? 'badge-success' : 'badge-danger'}" style="font-size: 10px; padding: 2px 8px;">
                                    ${p.enabled ? 'Live' : 'Hidden'}
                                </span>
                            </td>
                            <td style="text-align: right;">
                                <div style="display: flex; gap: 0.4rem; justify-content: flex-end; align-items: center; white-space: nowrap;">
                                    <button onclick="openEditModal(${p.id})" class="btn btn-sm btn-outline" style="padding: 4px 10px; font-size: 11px;">Edit</button>
                                    <button onclick="rejudgeProblem(${p.id}, 0)" class="btn btn-sm btn-outline" style="padding: 4px 10px; font-size: 11px; background: rgba(59, 130, 246, 0.1); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.2);">Rejudge</button>
                                    <button onclick="toggleProblem(${p.id}, 0)" class="btn btn-sm btn-outline" style="padding: 4px 10px; font-size: 11px;">${p.enabled ? 'Hide' : 'Show'}</button>
                                    <button onclick="deleteProblem(${p.id}, 0)" class="btn btn-sm" style="padding: 4px 10px; font-size: 11px; background: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.2);">Delete</button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        listDiv.innerHTML = `<p style="color: var(--danger); font-size: 0.875rem;">Error loading problems: ${error}</p>`;
    }
}

async function loadContestProblems(contestId) {
    const listDiv = document.getElementById(`problems-list-${contestId}`);

    try {
        const response = await fetch(`/admin/contest/${contestId}/problems`);
        const problems = await response.json();

        if (problems.length === 0) {
            listDiv.innerHTML = `<p style="text-align: center; color: var(--text-muted); font-size: 0.875rem; padding: 1rem;">No problems in this contest yet.</p>`;
            return;
        }

        const assignBox = contestId === 0 ? '' : `
            <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 1rem;">
                <select id="assignSelect-${contestId}" class="form-select" style="max-width: 320px;">
                    <option value="">Add existing problem...</option>
                </select>
                <button onclick="assignSelectedProblem(${contestId})" class="btn btn-sm btn-outline">Add</button>
            </div>
        `;

        listDiv.innerHTML = `
            ${assignBox}
            <table class="table" style="font-size: 0.875rem; width: 100%;">
                <thead>
                    <tr>
                        <th style="width: 40%;">Title</th>
                        <th>Status</th>
                        <th>Stats</th>
                        <th style="text-align: right;">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${problems.map(p => `
                        <tr>
                            <td>
                                <div style="font-weight: 600; color: var(--text-primary);">${p.title}</div>
                                <div style="font-size: 0.75rem; color: var(--text-muted);">${p.problem_type}</div>
                            </td>
                            <td>
                                <span class="badge ${p.enabled ? 'badge-success' : 'badge-danger'}" style="font-size: 10px; padding: 2px 8px;">
                                    ${p.enabled ? 'Live' : 'Hidden'}
                                </span>
                            </td>
                            <td>
                                <span style="color: var(--text-secondary);">${p.ac_count}/${p.submission_count} AC</span>
                            </td>
                            <td style="text-align: right;">
                                <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
                                    <button onclick="openEditModal(${p.id})" class="btn btn-sm btn-outline" style="padding: 4px 8px; font-size: 11px;">
                                        Manage
                                    </button>
                                    <button onclick="rejudgeProblem(${p.id}, ${contestId})" class="btn btn-sm btn-outline" style="padding: 4px 8px; font-size: 11px; background: rgba(59, 130, 246, 0.1); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.2);" title="Rejudge all submissions">
                                        Rejudge
                                    </button>
                                    <button onclick="toggleProblem(${p.id}, ${contestId})" class="btn btn-sm btn-outline" style="padding: 4px 8px; font-size: 11px;">
                                        ${p.enabled ? 'Hide' : 'Show'}
                                    </button>
                                    <button onclick="deleteProblem(${p.id}, ${contestId})" class="btn btn-sm" style="padding: 4px 8px; font-size: 11px; background: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.2);">
                                        Delete
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        if (contestId !== 0) {
            await loadUnassignedOptions(contestId);
        }
    } catch (error) {
        listDiv.innerHTML = `<p style="color: var(--danger); font-size: 0.875rem;">Error loading problems: ${error}</p>`;
    }
}

async function loadUnassignedOptions(contestId) {
    try {
        const response = await fetch('/admin/contest/0/problems');
        const problems = await response.json();
        const select = document.getElementById(`assignSelect-${contestId}`);
        if (!select) return;
        select.innerHTML = '<option value="">Add existing problem...</option>';
        problems.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = `${p.title} (ID ${p.id})`;
            select.appendChild(opt);
        });
    } catch (error) {
        // ignore
    }
}

async function assignSelectedProblem(contestId) {
    const select = document.getElementById(`assignSelect-${contestId}`);
    if (!select || !select.value) return;
    try {
        const response = await fetch(`/admin/assign_problem/${select.value}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contest_id: contestId })
        });
        const result = await response.json();
        if (result.success || result.message) {
            loadContestProblems(contestId);
        } else {
            showAlert(result.error || 'Failed to assign problem', 'error');
        }
    } catch (error) {
        showAlert('Error assigning problem: ' + error, 'error');
    }
}

// Problem Editing Logic
async function openEditModal(problemId) {
    const modal = document.getElementById('editProblemModal');
    modal.style.display = 'block';

    // Reset form
    document.getElementById('editProblemForm').reset();
    document.getElementById('editProblemId').value = problemId;
    document.getElementById('testCasesList').innerHTML = '<div class="spinner"></div>';

    try {
        // Fetch problem details - we might need a specific endpoint or use existing one if available
        // For now, let's assume we can fetch via /admin/problem/<id>
        // But wait, I don't have that route. I'll use the contest problems list or add a new route.
        // Actually, let's just fetch it from the API I'll add.
        const response = await fetch(`/api/problem_details/${problemId}`);
        const p = await response.json();

        document.getElementById('editTitle').value = p.title;
        document.getElementById('editDescription').value = p.description;
        document.getElementById('editInputFormat').value = p.input_format || '';
        document.getElementById('editOutputFormat').value = p.output_format || '';
        document.getElementById('editSampleInput').value = p.sample_input || '';
        document.getElementById('editSampleOutput').value = p.sample_output || '';
        const editProblemType = document.getElementById('editProblemType');
        if (editProblemType) editProblemType.value = p.problem_type || 'coding';
        const editTotalMarks = document.getElementById('editTotalMarks');
        if (editTotalMarks) editTotalMarks.value = p.total_marks || 100;
        const editProblemMode = document.getElementById('editProblemMode');
        if (editProblemMode) editProblemMode.value = p.problem_mode || 'stdin';
        const editFunctionName = document.getElementById('editFunctionName');
        if (editFunctionName) editFunctionName.value = p.function_name || 'solve';
        const editConstraints = document.getElementById('editConstraints');
        if (editConstraints) editConstraints.value = p.constraints || '';
        const editReferenceSolution = document.getElementById('editReferenceSolution');
        if (editReferenceSolution) editReferenceSolution.value = p.reference_solution || '';
        
        // Set difficulty field
        const editDifficulty = document.getElementById('editDifficulty');
        if (editDifficulty) editDifficulty.value = p.difficulty || 'easy';

        const editProblemContest = document.getElementById('editProblemContest');
        if (editProblemContest) {
            editProblemContest.dataset.original = p.contest_id ? String(p.contest_id) : '';
            editProblemContest.dataset.touched = 'false';
            if (editProblemContest.value !== editProblemContest.dataset.original) {
                editProblemContest.value = editProblemContest.dataset.original;
            }
        }

        // Load multi-language starter codes and solutions
        const starterCodes = p.starter_codes || {};
        const solutions = p.solutions || {};
        
        // Fallback to old format if new format not available
        if (Object.keys(starterCodes).length === 0 && p.starter_code) {
            const starterMap = parseStarterCodeMap(p.starter_code);
            Object.assign(starterCodes, starterMap);
        }
        
        // Update the global starter data for Monaco
        if (typeof window.editStarterCodeData !== 'undefined') {
            window.editStarterCodeData.python = starterCodes.python || '';
            window.editStarterCodeData.cpp = starterCodes.cpp || '';
            window.editStarterCodeData.java = starterCodes.java || '';
            window.editStarterCodeData.c = starterCodes.c || '';
            
            // Store solutions separately for submission
            if (typeof window.editSolutionCodeData === 'undefined') {
                window.editSolutionCodeData = {};
            }
            window.editSolutionCodeData.python = solutions.python || '';
            window.editSolutionCodeData.cpp = solutions.cpp || '';
            window.editSolutionCodeData.java = solutions.java || '';
            window.editSolutionCodeData.c = solutions.c || '';

            if (typeof switchEditStarterLang === 'function') {
                switchEditStarterLang('python', false); // Reset to python and refresh editor WITHOUT saving
            }
            if (typeof switchEditSolutionLang === 'function') {
                switchEditSolutionLang('python', false); // Reset solution editor too
            }
        }

        loadTestCases(problemId);
    } catch (error) {
        showAlert('Error loading problem details: ' + error, 'error');
    }
}

function closeEditModal() {
    document.getElementById('editProblemModal').style.display = 'none';
}

async function testProblem() {
    const problemId = document.getElementById('editProblemId').value;
    const problemMode = document.getElementById('editProblemMode')?.value || 'stdin';
    const functionName = document.getElementById('editFunctionName')?.value || 'solve';
    
    // Collect all solution code
    if (window.editSolutionEditor && typeof currentEditSolutionLang !== 'undefined') {
        window.editSolutionCodeData[currentEditSolutionLang] = window.editSolutionEditor.getValue();
    }
    
    const solutions = {};
    for (const [lang, code] of Object.entries(window.editSolutionCodeData || {})) {
        if (code && code.trim()) {
            solutions[lang] = code;
        }
    }
    
    if (Object.keys(solutions).length === 0) {
        showAlert('Please enter at least one reference solution to test', 'warning');
        return;
    }
    
    const resultsContainer = document.getElementById('testResultsContainer');
    const resultsDiv = document.getElementById('testResults');
    
    resultsContainer.style.display = 'block';
    resultsDiv.innerHTML = '<div class="spinner" style="width: 20px; height: 20px;"></div> <span style="margin-left: 0.5rem;">Testing all languages...</span>';
    
    try {
        const response = await fetch(`/admin/test_problem/${problemId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                solutions: solutions,
                problem_mode: problemMode,
                function_name: functionName
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            let html = '<div style="max-height: 500px; overflow-y: auto;">';
            
            // Display results for each language
            for (const [language, langResult] of Object.entries(result.results)) {
                const passRate = ((langResult.passed / langResult.total) * 100).toFixed(1);
                const statusColor = langResult.passed === langResult.total ? 'var(--success)' : 'var(--danger)';
                const langName = {'python': 'Python', 'cpp': 'C++', 'java': 'Java', 'c': 'C'}[language] || language;
                
                html += `
                    <div style="margin-bottom: 1.5rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px; border: 2px solid ${statusColor};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h4 style="margin: 0; color: var(--text-primary);">${langName}</h4>
                            <strong style="color: ${statusColor};">${langResult.passed}/${langResult.total} Passed (${passRate}%)</strong>
                        </div>
                `;
                
                if (langResult.passed < langResult.total) {
                    html += '<div style="font-size: 0.85rem;">';
                    langResult.test_results.forEach((test, idx) => {
                        if (!test.passed) {
                            const icon = '❌';
                            html += `
                                <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: rgba(239, 68, 68, 0.1); border-radius: 4px; border-left: 2px solid var(--danger);">
                                    <div><strong>${icon} Test ${idx + 1}:</strong> ${test.verdict}</div>
                                    <div style="font-size: 0.75rem; margin-top: 0.25rem; color: var(--text-muted);">
                                        <div>Input: <code>${test.input}</code></div>
                                        <div>Expected: <code>${test.expected}</code></div>
                                        <div>Got: <code>${test.actual}</code></div>
                            `;
                            if (test.error) {
                                html += `<div style="color: var(--danger);">Error: ${test.error}</div>`;
                            }
                            html += `</div></div>`;
                        }
                    });
                    html += '</div>';
                } else {
                    html += '<div style="color: var(--success); font-size: 0.9rem;">✅ All test cases passed!</div>';
                }
                
                html += '</div>';
            }
            
            html += '</div>';
            resultsDiv.innerHTML = html;
            
            // Check if all languages passed all tests
            const allPassed = Object.values(result.results).every(r => r.passed === r.total);
            if (allPassed) {
                showAlert('All languages passed all test cases! ✅', 'success');
            } else {
                showAlert('Some tests failed. Check results above.', 'warning');
            }
        } else {
            resultsDiv.innerHTML = `<p style="color: var(--danger);">Error: ${result.error}</p>`;
            showAlert(result.error, 'error');
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p style="color: var(--danger);">Error: ${error.message}</p>`;
        showAlert('Error testing problem: ' + error.message, 'error');
    }
}

function parseStarterCodeMap(raw) {
    if (!raw) return {};
    try {
        const data = JSON.parse(raw);
        if (data && typeof data === 'object' && !Array.isArray(data)) {
            return data;
        }
    } catch (e) {
        return { default: raw };
    }
    return {};
}

function setStarterFromMap(map, elementId, lang) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.value = map[lang] || map.default || '';
}

async function loadTestCases(problemId) {
    const listDiv = document.getElementById('testCasesList');
    try {
        const response = await fetch(`/admin/problem/${problemId}/test_cases`);
        const cases = await response.json();

        if (cases.length === 0) {
            listDiv.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem;">No hidden test cases yet.</p>';
            return;
        }

        listDiv.innerHTML = `
            <table class="table" style="font-size: 0.75rem;">
                <thead>
                    <tr>
                        <th>Input</th>
                        <th>Expected Output</th>
                        <th style="text-align: right;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${cases.map(tc => `
                        <tr>
                            <td style="font-family: monospace;">${tc.input.substring(0, 30)}${tc.input.length > 30 ? '...' : ''}</td>
                            <td style="font-family: monospace;">${tc.expected_output.substring(0, 30)}${tc.expected_output.length > 30 ? '...' : ''}</td>
                            <td style="text-align: right;">
                                <button onclick="deleteTestCase(${tc.id}, ${problemId})" class="btn btn-sm btn-danger" style="padding: 2px 6px; font-size: 10px;">Delete</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        listDiv.innerHTML = `<p style="color: var(--danger);">Error loading test cases: ${error}</p>`;
    }
}

async function addTestCase() {
    const problemId = document.getElementById('editProblemId').value;
    const input = document.getElementById('newTestInput').value.trim();
    const output = document.getElementById('newTestOutput').value.trim();

    if (!input || !output) {
        showAlert('Please enter both input and expected output', 'warning');
        return;
    }

    try {
        const response = await fetch(`/admin/problem/${problemId}/add_test_case`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input, expected_output: output, is_sample: 0 })
        });
        const result = await response.json();
        if (result.message) {
            document.getElementById('newTestInput').value = '';
            document.getElementById('newTestOutput').value = '';
            loadTestCases(problemId);
        } else {
            showAlert(result.error, 'error');
        }
    } catch (error) {
        showAlert('Error adding test case: ' + error, 'error');
    }
}

async function deleteTestCase(testCaseId, problemId) {
    const confirmed = await showModal('Confirm Delete', 'Are you sure you want to delete this test case?', { showCancel: true, confirmText: 'Delete' });
    if (!confirmed) return;
    try {
        await fetch(`/admin/delete_test_case/${testCaseId}`, { method: 'POST' });
        loadTestCases(problemId);
        showAlert('Test case deleted successfully', 'success');
    } catch (error) {
        showAlert('Error deleting test case: ' + error, 'error');
    }
}

// Form handler for problem editing
document.addEventListener('DOMContentLoaded', function () {
    const editProblemContest = document.getElementById('editProblemContest');
    if (editProblemContest) {
        editProblemContest.addEventListener('change', () => {
            editProblemContest.dataset.touched = 'true';
        });
    }

    const editForm = document.getElementById('editProblemForm');
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const problemId = document.getElementById('editProblemId').value;
            const starterMap = typeof collectStarterCode === 'function' ? collectStarterCode(true) : {};
            
            // Collect solution code from Monaco editor
            let solutionMap = {};
            if (typeof window.editSolutionCodeData !== 'undefined' && typeof window.switchEditSolutionLang === 'function') {
                // Save current editor content
                if (window.editSolutionEditor && typeof currentEditSolutionLang !== 'undefined') {
                    window.editSolutionCodeData[currentEditSolutionLang] = window.editSolutionEditor.getValue();
                }
                // Filter out empty solutions
                for (const [lang, code] of Object.entries(window.editSolutionCodeData)) {
                    if (code && code.trim()) {
                        solutionMap[lang] = code;
                    }
                }
            }
            
            const contestSelect = document.getElementById('editProblemContest');
            let contestIdValue = contestSelect?.value ?? '';
            if (contestSelect && contestIdValue === '' && contestSelect.dataset.touched !== 'true') {
                contestIdValue = contestSelect.dataset.original || '';
            }

            const data = {
                title: document.getElementById('editTitle').value,
                description: document.getElementById('editDescription').value,
                input_format: document.getElementById('editInputFormat').value,
                output_format: document.getElementById('editOutputFormat').value,
                sample_input: document.getElementById('editSampleInput').value,
                sample_output: document.getElementById('editSampleOutput').value,
                test_input: document.getElementById('editSampleInput').value, // Fallback
                expected_output: document.getElementById('editSampleOutput').value, // Fallback
                contest_id: contestIdValue,
                problem_type: document.getElementById('editProblemType')?.value || 'coding',
                total_marks: document.getElementById('editTotalMarks')?.value || 100,
                problem_mode: document.getElementById('editProblemMode')?.value || 'stdin',
                function_name: document.getElementById('editFunctionName')?.value || 'solve',
                constraints: document.getElementById('editConstraints')?.value || '',
                reference_solution: document.getElementById('editReferenceSolution')?.value || '',
                difficulty: document.getElementById('editDifficulty')?.value || 'easy',
                starter_code_dict: starterMap,
                solution_code_dict: solutionMap
            };

            try {
                const response = await fetch(`/admin/edit_problem/${problemId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.success) {
                    showAlert('Problem updated successfully', 'success');
                    closeEditModal();
                    loadContests();
                } else {
                    showAlert(result.error, 'error');
                }
            } catch (error) {
                showAlert('Error updating problem: ' + error, 'error');
            }
        });
    }
});

async function toggleProblem(problemId, contestId) {
    try {
        const response = await fetch(`/admin/toggle_problem/${problemId}`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            showAlert('Operation successful', 'success');
            if (contestId === 0 || contestId === '0' || contestId === null || typeof contestId === 'undefined') {
                loadAllProblems();
                loadContests();
            } else {
                loadContestProblems(contestId);
                loadContests();
            }
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Error: ' + error, 'error');
    }
}

async function deleteProblem(problemId, contestId) {
    const confirmed = await showModal('Delete Problem', 'Are you sure you want to delete this problem? All submissions will be lost.', { showCancel: true, confirmText: 'Delete Problem' });
    if (!confirmed) return;

    try {
        const response = await fetch(`/admin/delete_problem/${problemId}`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            showAlert('Problem deleted successfully', 'success');
            if (contestId === 0 || contestId === '0' || !contestId) {
                loadAllProblems();
            } else {
                loadContestProblems(contestId);
            }
            loadContests();
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Error: ' + error, 'error');
    }
}

async function rejudgeProblem(problemId, contestId) {
    const confirmed = await showModal('Rejudge Problem', 'Rejudge all submissions for this problem? This will re-run all test cases.', { showCancel: true, confirmText: 'Rejudge All' });
    if (!confirmed) return;

    try {
        const response = await fetch(`/admin/rejudge_problem/${problemId}`, { method: 'POST' });
        const data = await response.json();
        if (data.message) {
            showAlert(data.message, 'success');
            if (typeof AdminDebug !== 'undefined') {
                AdminDebug.log(`Rejudged problem #${problemId}`, data);
            }
            // Refresh the problem list
            if (contestId === 0 || contestId === '0' || contestId === null || typeof contestId === 'undefined') {
                loadAllProblems();
            } else {
                loadContestProblems(contestId);
            }
        } else {
            showAlert(data.error || 'Error rejudging problem', 'error');
        }
    } catch (error) {
        showAlert('Error: ' + error, 'error');
    }
}

async function toggleContest(contestId) {
    // Note: We avoid event.target here if called from code, but buttons use it
    const button = (typeof event !== 'undefined') ? event.target : null;
    if (button) button.disabled = true;

    try {
        const response = await fetch(`/admin/toggle_contest/${contestId}`, { method: 'POST' });
        const data = await response.json();
        showAlert(data.message, data.success !== false ? 'success' : 'error');
        loadContests();
    } catch (error) {
        showAlert('Error: ' + error, 'error');
        if (button) button.disabled = false;
    }
}

async function deleteContest(contestId) {
    const confirmed = await showModal('Delete Contest', 'WARNING: Are you sure you want to delete this contest? ALL associated problems and submissions will be permanently deleted.', { showCancel: true, confirmText: 'Delete EVERYTHING' });
    if (!confirmed) return;

    try {
        const response = await fetch(`/admin/delete_contest/${contestId}`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            showAlert('Contest deleted successfully.', 'success');
            loadContests();
            if (typeof loadContestOptions === 'function') loadContestOptions();
        } else {
            showAlert(data.error || 'Failed to delete contest', 'error');
        }
    } catch (error) {
        showAlert('Error: ' + error, 'error');
    }
}

// Create Contest Form handler
document.addEventListener('DOMContentLoaded', function () {
    const createForm = document.getElementById('createContestForm');
    if (createForm && !createForm.dataset.attached) {
        createForm.dataset.attached = 'true';
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                title: formData.get('title'),
                description: formData.get('description'),
                start_time: formData.get('start_time'),
                end_time: formData.get('end_time')
            };

            const submitBtn = e.target.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = true;

            try {
                const response = await fetch('/admin/create_contest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.message) {
                    showAlert(result.message, 'success');
                    e.target.reset();
                    loadContests();
                    loadContestOptions();
                } else {
                    showAlert('Error: ' + (result.error || 'Unknown error'), 'error');
                }
            } catch (error) {
                showAlert('Error: ' + error, 'error');
            } finally {
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    }
    loadContests();
});
