const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Upstox API Credentials
const API_KEY = process.env.API_KEY;
const API_SECRET = process.env.API_SECRET;
const REDIRECT_URI = process.env.REDIRECT_URI;
let accessToken = null;

// Step 1: Redirect User to Upstox for Authentication
app.get('/auth/login', (req, res) => {
    const authUrl = `https://api.upstox.com/v2/login/authorize?client_id=${API_KEY}&redirect_uri=${REDIRECT_URI}&response_type=code`;
    res.redirect(authUrl);
});

// Step 2: Handle Upstox Redirect and Exchange Auth Code for Access Token
app.get('/auth/callback', async (req, res) => {
    const authCode = req.query.code;
    if (!authCode) {
        return res.status(400).json({ error: "Auth code missing!" });
    }

    try {
        const response = await axios.post('https://api.upstox.com/v2/login/authorization/token', {
            code: authCode,
            client_id: API_KEY,
            client_secret: API_SECRET,
            redirect_uri: REDIRECT_URI,
            grant_type: "authorization_code"
        });

        accessToken = response.data.access_token;
        console.log("✅ Access Token:", accessToken);

        res.json({ message: "Authorization successful!", access_token: accessToken });
    } catch (error) {
        console.error("❌ Token Exchange Failed:", error.response.data);
        res.status(500).json({ error: "Token Exchange Failed" });
    }
});

// Step 3: Fetch Market Data from Upstox
app.get('/market-data', async (req, res) => {
    if (!accessToken) {
        return res.status(401).json({ error: "Not authenticated" });
    }

    try {
        const response = await axios.get("https://api.upstox.com/v2/market-quote/NSE_EQ|INFY", {
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
