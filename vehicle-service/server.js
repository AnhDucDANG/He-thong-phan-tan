// vehicle-service/server.js

const express = require('express');
require('dotenv').config(); // Tải biến môi trường từ file .env

const app = express();
const PORT = process.env.PORT || 8001; // Cổng mặc định 8001

// Middleware
app.use(express.json()); // Cho phép server đọc JSON từ request body

// Route kiểm tra trạng thái (Health Check)
app.get('/health', (req, res) => {
  res.status(200).json({ 
    service: "Vehicle Service", 
    status: "Running", 
    database: "Pending" // Sẽ cập nhật sau khi kết nối MongoDB
  });
});

// Bắt đầu lắng nghe
app.listen(PORT, () => {
  console.log(`Vehicle Service is running on port ${PORT}`);
});