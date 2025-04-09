import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import routes from './routes/routes.js';
import cron from "node-cron";
import axios from "axios";

const app = express();

app.use(express.json());

// Middleware
app.use("/api", routes);

// Schedule daily read generation at 4 AM
cron.schedule("0 4 * * *", async () => {
  try {
    console.log("🕒 Running daily read generation...");
    await axios.post(
      "http://localhost:" + (process.env.PORT || 4884) + "/api/daily-read"
    );
    console.log("✅ Daily read generation completed successfully");
  } catch (error) {
    console.error("❌ Error generating daily read:", error.message);
  }
});

// 404 Middleware
app.use((req, res) => {
    res.status(404).json({ success: false, message: 'Route not found' });
});

// Error Handling Middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ success: false, message: err.message });
});

export default app;