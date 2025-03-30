const express = require('express');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// ✅ Root Route (Server Check)
app.get('/', (req, res) => {
    res.send("✅ Server is Running! 🚀");
});

// ✅ Infinite Loop (Container को रोकने के लिए)
setInterval(() => {
    console.log("🔄 Server is Alive...");
}, 60000); // हर 60 सेकंड में Log करेगा

// ✅ Server Start करो
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
});
