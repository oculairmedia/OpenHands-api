const { io } = require("socket.io-client");

const BASE_URL = "192.168.50.90:3000"; // From provided URL
const LATEST_EVENT_ID = -1; // Start from beginning

function createOpenHandsClient(conversationId) {
  const socket = io(`ws://${BASE_URL}`, {
    transports: ["websocket"],
    query: {
      conversation_id: conversationId,
      latest_event_id: LATEST_EVENT_ID,
      source: "external_client"
    },
    auth: {
      token: "external-access-token"
    }
  });

  socket.io.on("reconnect_attempt", () => {
    console.log("[OpenHands] Attempting to reconnect...");
  });

  socket.io.on("reconnect_error", (error) => {
    console.error("[OpenHands] Reconnection error:", error);
  });

  socket.on("connect", () => {
    console.log("[OpenHands] Connected to server");
  });

  socket.on("connect_error", (err) => {
    console.error("[OpenHands] Connection error:", err.message);
  });

  return {
    sendMessage: (text) => {
      return new Promise((resolve, reject) => {
        const messageEvent = {
          source: "user",
          action: "message",
          message: text,
          args: {
            content: text,
            wait_for_response: true
          }
        };

        console.log("[OpenHands] Sending user message:", messageEvent);
        socket.emit("oh_action", messageEvent, (ack) => {
          if (ack && ack.status === "received") {
            console.log("[OpenHands] Server acknowledged message delivery");
          } else {
            console.warn("[OpenHands] No explicit acknowledgment from server (this may be normal).");
          }
        });

        let finalResponse = null;

        const eventHandler = (event) => {
          console.log("[OpenHands] Received event:", event);
          if (event.source === 'agent' && event.message) {
            finalResponse = event;
          }
          if (event.source === 'agent' && event.extras && event.extras.agent_state === 'awaiting_user_input') {
            socket.off("oh_event", eventHandler);
            resolve(finalResponse);
          }
        };

        socket.on("oh_event", eventHandler);

        // Add a timeout to reject the promise if no response is received
        setTimeout(() => {
          socket.off("oh_event", eventHandler);
          if (finalResponse) {
            resolve(finalResponse);
          } else {
            reject(new Error("Timeout waiting for response"));
          }
        }, 120000); // 120 seconds timeout
      });
    }
  };
}

module.exports = { createOpenHandsClient };