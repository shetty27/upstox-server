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

// ✅ Step 2: Infinite Loop (Server को बंद होने से रोकने के लिए)
setInterval(() => {
    console.log("🔄 Server is Alive...");
}, 60000); // हर 60 सेकंड में Log करेगा

// ✅ Step 3: Server को Start करना (Continuous Process)
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});
