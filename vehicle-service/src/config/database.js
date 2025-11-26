
const mongoose = require('mongoose');

const connectDB = async () => {
    try {
        // Sử dụng biến môi trường MONGO_URI
        await mongoose.connect(process.env.MONGO_URI);
        
        console.log(`✅ MongoDB Connected: ${mongoose.connection.host}`);
        // Bạn có thể thêm logic seed data ở đây nếu muốn

    } catch (err) {
        console.error(`❌ MongoDB Connection Error: ${err.message}`);
        process.exit(1);
    }
};

module.exports = connectDB;
