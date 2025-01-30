const express = require('express');
const { createOpenHandsClient } = require('./scripts/openhands-client');

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.post('/send-message', async (req, res) => {
  const { conversationId, message } = req.body;

  if (!conversationId || !message) {
    return res.status(400).json({ error: 'Missing conversationId or message' });
  }

  try {
    const client = createOpenHandsClient(conversationId);
    const response = await client.sendMessage(message);
    console.log('OpenHands response:', response); // Log the response
    res.json({ response });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

app.listen(port, () => {
  console.log(`OpenHands API server listening at http://localhost:${port}`);
});