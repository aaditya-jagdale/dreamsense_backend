// Import express
import app from "./app.js";

// Import routes
const PORT = process.env.PORT || 4884;

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
})
