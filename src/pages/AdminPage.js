import React, { useState, useEffect, useRef } from "react";
import Chart from "chart.js/auto";
import '../styles/admin_interface.css';

const AdminInterface = () => {
  const [dashboardData, setDashboardData] = useState({
    totalInteractions: "Loading...",
    averageResponseTime: "Loading...",
    systemUptime: "Loading...",
  });
  const [usersData, setUsersData] = useState([]);
  const [logsData, setLogsData] = useState([]);
  const [apiKeysData, setApiKeysData] = useState([]);
  const [selectedLog, setSelectedLog] = useState(null);

  const interactionVolumeChartRef = useRef(null);
  const responseTimeChartRef = useRef(null);
  const commonQuestionsChartRef = useRef(null);

  useEffect(() => {
    fetchDashboardData();
    fetchUsersData();
    fetchLogsData();
    fetchApiKeys();

    return () => {
      if (interactionVolumeChartRef.current) interactionVolumeChartRef.current.destroy();
      if (responseTimeChartRef.current) responseTimeChartRef.current.destroy();
      if (commonQuestionsChartRef.current) commonQuestionsChartRef.current.destroy();
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/dashboard");
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error("Failed to fetch dashboard data", error);
    }
  };

  const fetchUsersData = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/users");
      const data = await response.json();
      setUsersData(data);
    } catch (error) {
      console.error("Failed to fetch users data", error);
    }
  };

  const fetchLogsData = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/logs");
      const data = await response.json();
      setLogsData(data);
    } catch (error) {
      console.error("Failed to fetch logs data", error);
    }
  };

  const fetchApiKeys = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/apikeys");
      const data = await response.json();
      setApiKeysData(data);
    } catch (error) {
      console.error("Failed to fetch API keys", error);
    }
  };

  const createCharts = () => {
    createInteractionVolumeChart();
    createResponseTimeChart();
    createCommonQuestionsChart();
  };

  const createInteractionVolumeChart = () => {
    const ctx = document.getElementById("interactionVolumeChart").getContext("2d");
    if (interactionVolumeChartRef.current) interactionVolumeChartRef.current.destroy();

    interactionVolumeChartRef.current = new Chart(ctx, {
      type: "line",
      data: {
        labels: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        datasets: [{ label: "Interactions", data: [300, 500, 200, 700, 600, 600, 400, 500, 400, 800, 400, 300] }],
      },
    });
  };

  const createResponseTimeChart = () => {
    const ctx = document.getElementById("responseTimeChart").getContext("2d");
    if (responseTimeChartRef.current) responseTimeChartRef.current.destroy();

    responseTimeChartRef.current = new Chart(ctx, {
      type: "line",
      data: {
        labels: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        datasets: [{ label: "Response Time (seconds)", data: [1.5, 1.2, 2.0, 1.8, 1.3, 1.1, 1.2, 1.5, 1.5, 1.4, 1.4, 1.3] }],
      },
    });
  };

  const createCommonQuestionsChart = () => {
    const ctx = document.getElementById("commonQuestionsChart").getContext("2d");
    if (commonQuestionsChartRef.current) commonQuestionsChartRef.current.destroy();

    commonQuestionsChartRef.current = new Chart(ctx, {
      type: "pie",
      data: {
        labels: ["Financial Aid", "Course Registration", "Campus Events", "Library Hours"],
        datasets: [{ label: "Common Questions", data: [30, 20, 25, 25] }],
      },
    });
  };

  const handleGreetingSave = () => {
    const greetingMessage = document.getElementById("greeting-message").value;
    alert(`Greeting message saved: ${greetingMessage}`);
  };

  const handleAddFaq = () => {
    const faqQuestion = document.getElementById("new-faq-question").value;
    const faqAnswer = document.getElementById("new-faq-answer").value;
    alert(`FAQ added: ${faqQuestion} - ${faqAnswer}`);
  };

  const handleAddApiKey = async () => {
    const newKey = document.getElementById("new-key").value;
    try {
      await fetch("http://localhost:5000/api/apikeys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: newKey }),
      });
      setApiKeysData([...apiKeysData, { key: newKey }]);
      alert("New API Key added.");
    } catch (error) {
      console.error("Failed to add API key", error);
    }
  };

  return (
    <div className="admin-interface">
      <div className="sidebar">
        <h2>Admin Panel</h2>
        <ul>
          <li><a href="#dashboard">Dashboard</a></li>
          <li><a href="#user-management">User Management</a></li>
          <li><a href="#chatbot-configuration">Chatbot Configuration</a></li>
          <li><a href="#analytics-dashboard">Analytics</a></li>
          <li><a href="#logs-history">Logs</a></li>
          <li><a href="#apikeys">API Key Management</a></li>
        </ul>
      </div>
      <div className="main-content">
        <section id="dashboard">
          <h2>Dashboard</h2>
          <div className="info-boxes">
            <div className="info-box"><h3>Total Interactions</h3><p>{dashboardData.totalInteractions}</p></div>
            <div className="info-box"><h3>Average Response Time</h3><p>{dashboardData.averageResponseTime}</p></div>
            <div className="info-box"><h3>System Uptime</h3><p>{dashboardData.systemUptime}</p></div>
          </div>
          <canvas id="interactionVolumeChart"></canvas>
        </section>
        <section id="user-management">
          <h2>User Management</h2>
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Role</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {usersData.map((user, index) => (
                <tr key={index}>
                  <td>{user.username}</td>
                  <td>{user.role}</td>
                  <td>{user.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        <section id="chatbot-configuration">
          <h2>Chatbot Configuration</h2>
          <div>
            <label>Greeting Message:</label>
            <input type="text" id="greeting-message" placeholder="Enter greeting message" />
            <button onClick={handleGreetingSave}>Save Greeting</button>
          </div>
          <h3>Manage FAQ</h3>
          <input type="text" id="new-faq-question" placeholder="New FAQ Question" />
          <textarea id="new-faq-answer" placeholder="New FAQ Answer"></textarea>
          <button onClick={handleAddFaq}>Add FAQ</button>
        </section>
        <section id="analytics-dashboard">
          <h2>Analytics Dashboard</h2>
          <div className="chart-container"><canvas id="interactionVolumeChart"></canvas></div>
          <div className="chart-container"><canvas id="commonQuestionsChart"></canvas></div>
          <div className="chart-container"><canvas id="responseTimeChart"></canvas></div>
        </section>
        <section id="logs-history">
          <h2>Conversation Logs</h2>
          {selectedLog ? (
            <div>
              <h3>Conversation Details</h3>
              <div className="chat-history">
                {selectedLog.conversation.map((message, index) => (
                  <p key={index} className={message.sender === "User" ? "chat-user" : "chat-bot"}>
                    {message.sender === "User" ? "User: " : "Bot: "}{message.message}
                  </p>
                ))}
              </div>
              <button onClick={() => setSelectedLog(null)}>Back to Logs</button>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>User</th>
                  <th>Topic</th>
                </tr>
              </thead>
              <tbody>
                {logsData.map((log, index) => (
                  <tr key={index} onClick={() => setSelectedLog(log)}>
                    <td>{log.date}</td>
                    <td>{log.user}</td>
                    <td>{log.topic}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
        <section id="apikeys">
          <h2>API Key Management</h2>
          <div>
            <label>Add New API Key:</label>
            <input type="text" id="new-key" placeholder="Enter API key" />
            <button onClick={handleAddApiKey}>Add Key</button>
          </div>
          <h3>Existing Keys</h3>
          <table>
            <thead>
              <tr>
                <th>Key</th>
              </tr>
            </thead>
            <tbody>
              {apiKeysData.map((keyData, index) => (
                <tr key={index}>
                  <td>{keyData.key}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
};

export default AdminInterface;
