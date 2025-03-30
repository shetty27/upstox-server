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

// ✅ Step 1: Root Route (Check if Server is Running)
app.get('/', (req, res) => {
    res.send("✅ Server is Running! 🚀");
});

// ✅ Step 2: Upstox Authorization Callback Route
app.get('/auth/callback', async (req, res) => {
    const authCode = req.query.code;
    if (!authCode) {
        return res.status(400).json({ error: "Authorization Code Not Found" });
    }

    try {
        // 🔹 Auth Code से Access Token लेना
        const response = await axios.post('https://api.upstox.com/v2/login/authorization/token', {
            client_id: API_KEY,
            client_secret: API_SECRET,
            redirect_uri: REDIRECT_URI,
            grant_type: "authorization_code",
            code: authCode
        });

        accessToken = response.data.access_token;
        console.log("✅ Access Token:", accessToken);

        res.json({ message: "Login Successful!", accessToken });

    } catch (error) {
        console.error("❌ Auth Token Error:", error.response?.data || error.message);
        res.status(500).json({ error: "Failed to get Access Token" });
    }
});

// ✅ Step 3: Server को Start करना (Continuous Process)
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});
