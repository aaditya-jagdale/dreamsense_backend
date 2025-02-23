import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import routes from './routes/routes.js';

const app = express();

app.use(express.json());

// Middleware
app.use('/api', routes);

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