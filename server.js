require('dotenv').config();
const express = require('express');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;

// ✅ Default Route (Root Route)
app.get('/', (req, res) => {
    res.json({ message: "🚀 Upstox Server is Running..." });
});

// ✅ Check if Server is Running
app.get('/ping', (req, res) => {
    res.json({ message: "🔄 Server is Alive..." });
});

// Start Server
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});

// Upstox API Credentials
const API_KEY = process.env.API_KEY;
const API_SECRET = process.env.API_SECRET;
const REDIRECT_URI = process.env.REDIRECT_URI;
let accessToken = null;

// Route to Get Auth Code
app.get('/login', (req, res) => {
    const authURL = `https://api.upstox.com/v2/login/authorization/dialog?client_id=${API_KEY}&redirect_uri=${REDIRECT_URI}&response_type=code`;
    res.redirect(authURL);
});

// Route to Handle Redirect and Get Access Token
app.get('/auth/callback', async (req, res) => {
    const authCode = req.query.code;
    if (!authCode) return res.status(400).json({ error: "Auth Code missing" });

    try {
        const response = await axios.post('https://api.upstox.com/v2/login/authorization/token', {
            client_id: API_KEY,
            client_secret: API_SECRET,
            code: authCode,
            redirect_uri: REDIRECT_URI,
            grant_type: "authorization_code"
        });

        accessToken = response.data.access_token;
        res.json({ message: "✅ Access Token Received", accessToken });
    } catch (error) {
        res.status(500).json({ error: "❌ Failed to get access token", details: error.response.data });
    }
});

// Route to Fetch Market Data
app.get('/market-data', async (req, res) => {
    if (!accessToken) {
        return res.status(401).json({ error: "Not authenticated" });
    }

    try {
        const response = await axios.get("https://api.upstox.com/market-data", {
            headers: { Authorization: `Bearer ${accessToken}` }
        });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "Failed to fetch market data" });
    }
});

// Start Server
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});
