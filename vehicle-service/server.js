// vehicle-service/server.js

const express = require('express');
const mongoose = require('mongoose');
const connectDB = require('./src/config/database.js'); // Đường dẫn đúng;
const vehicleRoutes = require('./src/routes/vehicleRoutes');
require('dotenv').config(); 

const app = express();
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/vehicle_db';
const PORT = process.env.PORT || 8002;

// --- 1. Kết nối CSDL ---
// const connectDB = async () => {
//     try {
//         await mongoose.connect(MONGO_URI);
        
//         // **LOG KẾT NỐI THÀNH CÔNG (Cần thiết để kiểm tra Docker)**
//         console.log(`✅ MongoDB Connected: ${MONGO_URI.split('@').pop()}`); 

//         // Sau khi kết nối thành công, bạn có thể gọi hàm chèn dữ liệu mẫu (Seed Data) ở đây
//         // seedVehicles(); 

//     } catch (err) {
//         // **LOG KẾT NỐI THẤT BẠI**
//         console.error(`❌ MongoDB Connection Error: ${err.message}`);
//         // Tùy chọn: Dừng ứng dụng nếu CSDL không kết nối được
//         process.exit(1); 
//     }
// };

// --- 2. Khởi tạo Service ---
app.use(express.json());
app.use('/api/vehicles', vehicleRoutes);
// Route kiểm tra trạng thái
app.get('/health', (req, res) => {
    // Lý tưởng là kiểm tra trạng thái kết nối CSDL ở đây
    res.status(200).json({ 
        service: "Vehicle Service", 
        status: "Running", 
        database: mongoose.STATES[mongoose.connection.readyState] // Trạng thái kết nối
    });
});

app.get('/', (req, res) => {
    res.send('Welcome to the Vehicle Microservice! Access API via /api/vehicles');
});

// Khởi chạy server và CSDL
connectDB().then(() => {
    app.listen(PORT, () => {
        console.log(`Vehicle Service is running on port ${PORT}`);
        console.log(`🔗 Local Access Link: http://localhost:${PORT}`);
    });
});