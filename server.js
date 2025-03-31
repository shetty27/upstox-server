require('dotenv').config();
const express = require('express');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;

// ✅ Upstox API Credentials
const API_KEY = process.env.API_KEY;
const API_SECRET = process.env.API_SECRET;
const REDIRECT_URI = process.env.REDIRECT_URI;
let accessToken = null;

// ✅ Root Route (Check if Server is Running)
app.get('/', (req, res) => {
    res.send("🚀 Upstox Server is Running...");
});

// ✅ Get Auth Code (Step 1)
app.get('/auth', (req, res) => {
    const authUrl = `https://api.upstox.com/v2/login/authorization/dialog?client_id=${API_KEY}&redirect_uri=${REDIRECT_URI}&response_type=code`;
    res.redirect(authUrl);
});

// ✅ Callback Route (Step 2: Get Access Token)
app.get('/auth/callback', async (req, res) => {
    const authCode = req.query.code;
    if (!authCode) {
        return res.status(400).send("❌ Auth Code Missing!");
    }

    try {
        const response = await axios.post('https://api.upstox.com/v2/login/authorization/token', {
            client_id: API_KEY,
            client_secret: API_SECRET,
            redirect_uri: REDIRECT_URI,
            grant_type: "authorization_code",
            code: authCode
        });

        accessToken = response.data.access_token;
        res.send(`✅ Access Token: ${accessToken}`);
    } catch (error) {
        console.error("❌ Error Fetching Access Token:", error.response?.data || error.message);
        res.status(500).send("❌ Failed to Get Access Token");
    }
});

// ✅ Fetch Market Data
app.get('/market-data', async (req, res) => {
    if (!accessToken) {
        return res.status(401).json({ error: "❌ Not Authenticated" });
    }

    try {
        const response = await axios.get("https://api.upstox.com/market-data", {
            headers: { Authorization: `Bearer ${accessToken}` }
        });
        res.json(response.data);
    } catch (error) {
        console.error("❌ Error Fetching Market Data:", error.response?.data || error.message);
        res.status(500).json({ error: "❌ Failed to Fetch Market Data" });
    }
});

// ✅ Start Server
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});
