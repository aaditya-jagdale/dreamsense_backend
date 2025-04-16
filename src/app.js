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
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] 🕒 Starting scheduled daily read generation...`);
  try {
    await axios.post(process.env.RENDER_URL + "/api/daily-read");
    console.log(
      `[${timestamp}] ✅ Daily read generation completed successfully`
    );
  } catch (error) {
    console.error(
      `[${timestamp}] ❌ Error generating daily read:`,
      error.message
    );
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