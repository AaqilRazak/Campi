const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Connect to the SQLite database
const db = new sqlite3.Database('./database.db');

// API to fetch dashboard data
app.get('/api/dashboard', (req, res) => {
    db.all(`SELECT COUNT(*) AS totalInteractions FROM MessageHistory`, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json({
            totalInteractions: rows[0]?.totalInteractions || 0,
            averageResponseTime: '1.2s', // Fake value
            systemUptime: '99.9%' // Fake value
        });
    });
});

// API to fetch users
app.get('/api/users', (req, res) => {
    db.all(`SELECT Username AS username, RoleName AS role, 'Active' AS status
            FROM UserInformation
            INNER JOIN UserRoles ON UserInformation.UserRoleID = UserRoles.UserRoleID`, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// API to fetch logs
app.get('/api/logs', (req, res) => {
    db.all(`SELECT SessionLogs.SessionID, UserInformation.Username AS user, MessageHistory.Timestamp AS date,
            GROUP_CONCAT(MessageHistory.MessageText || ' (' || MessageHistory.Sender || ')', '|') AS conversation
            FROM MessageHistory
            INNER JOIN SessionLogs ON MessageHistory.SessionID = SessionLogs.SessionID
            INNER JOIN UserInformation ON SessionLogs.UserID = UserInformation.UserID
            GROUP BY SessionLogs.SessionID`, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows.map(row => ({
            user: row.user,
            date: row.date,
            conversation: row.conversation.split('|').map(msg => {
                const [message, sender] = msg.split(' (');
                return { sender: sender.slice(0, -1), message };
            })
        })));
    });
});

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://localhost:5000');
});
