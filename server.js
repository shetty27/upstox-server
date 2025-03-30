const express = require('express');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;

// Upstox API Credentials
const API_KEY = process.env.API_KEY;
const API_SECRET = process.env.API_SECRET;
const REDIRECT_URI = process.env.REDIRECT_URI;
let accessToken = null;

// Auto Login Function
async function loginToUpstox() {
    try {
        const response = await axios.get('https://api.upstox.com/v2/login/authorization/token',{
            client_id: API_KEY,
            client_secret: API_SECRET,
            redirect_uri: REDIRECT_URI,
            grant_type: "client_credentials"
        });

        accessToken = response.data.access_token;
        console.log("✅ Access Token Received:", accessToken);

        // Set Auto Refresh Token
        setTimeout(loginToUpstox, (response.data.expires_in - 60) * 1000);
    } catch (error) {
        console.error("❌ Auto Login Failed:", error.response.data);
    }
}

// Fetch Market Data
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

// Start Server & Auto Login
app.listen(PORT, async () => {
    console.log(`🚀 Server running on port ${PORT}`);
    await loginToUpstox();
});
