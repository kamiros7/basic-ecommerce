// To connect to the SSE endpoint
const eventSource = new EventSource("http://127.0.0.1:9093/sse");

eventSource.onmessage = (event) => {
    console.log("Received message:", event.data);
    let data = JSON.parse(event.data)
    const notificationsDiv = document.getElementById("notifications");
    const messageElement = document.createElement("div");
    messageElement.textContent = `Order ID: ${data.order_id}, Status: ${data.status}`;
    notificationsDiv.appendChild(messageElement);
};

eventSource.onerror = (error) => {
    console.error("SSE error:", error);
    eventSource.close(); // Close the connection if needed
};
