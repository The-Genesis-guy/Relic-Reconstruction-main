(function () {
    const enabled = window.LEADERBOARD_ENABLED !== false;

    async function loadLeaderboard() {
        if (!enabled) return;
        const contestId = document.getElementById('contestFilter')?.value;
        const url = contestId ? `/api/leaderboard?contest_id=${contestId}` : '/api/leaderboard';

        try {
            const response = await fetch(url);
            const data = await response.json();
            const tbody = document.getElementById('leaderboardBody');

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 3rem; color: var(--text-muted);">No submissions yet</td></tr>';
                return;
            }

            tbody.innerHTML = data.map(row => {
                const rankClass = row.rank <= 3 ? `rank-${row.rank}` : '';
                const rankDisplay = row.rank === 1 ? '#1' : row.rank === 2 ? '#2' : row.rank === 3 ? '#3' : `#${row.rank}`;

                return `
                    <tr class="${rankClass}">
                        <td class="rank-cell">${rankDisplay}</td>
                        <td style="font-weight: 600; color: var(--text-primary);">${row.username}</td>
                        <td style="text-align: right; font-weight: 700; color: var(--primary);">${row.points}</td>
                        <td style="text-align: right; color: var(--text-secondary);">${row.problems_solved}</td>
                        <td style="text-align: right; font-family: monospace; color: var(--accent);">${row.time_str}</td>
                    </tr>
                `;
            }).join('');
        } catch (error) {
            console.error('Error loading leaderboard:', error);
        }
    }

    // Initialize SocketIO
    let socket;
    if (typeof io !== 'undefined' && enabled) {
        socket = io();
        socket.on('connect', () => {
            console.log('Leaderboard connected to WebSocket');
            socket.emit('join_leaderboard');
        });

        socket.on('leaderboard_update', (data) => {
            console.log('Real-time leaderboard update triggered', data);
            loadLeaderboard();
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        const filter = document.getElementById('contestFilter');
        if (filter) {
            filter.addEventListener('change', loadLeaderboard);
        }

        if (enabled) {
            loadLeaderboard();
            // Fallback polling (every 60 seconds)
            setInterval(loadLeaderboard, 60000);
        }
    });
})();
