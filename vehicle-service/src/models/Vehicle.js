

const mongoose = require('mongoose');

const VehicleSchema = new mongoose.Schema({
    // ID xe (MongoDB tự tạo)
    ownerId: { 
    type: String, 
    required: true, 
    index: true // Tạo index để tìm xe theo chủ nhanh hơn
    },
    make: { type: String, required: true },   // Hãng (Toyota)
    model: { type: String, required: true },  // Dòng (Camry)
    year: { type: Number, required: true }, // Năm sản xuất

    licensePlate: {
        type: String,
        required: [true, 'Biển số xe là bắt buộc'],
        unique: true, // Rất quan trọng: Mỗi xe có 1 biển số duy nhất
        trim: true
    },
   
    
    dailyRate: {
        type: Number,
        required: [true, 'Giá thuê ngày là bắt buộc'],
        min: [100000, 'Giá thuê phải lớn hơn 100.000 VNĐ']
    },
    status: {
        type: String,
        enum: ['available', 'on_rent', 'maintenance'], // Các trạng thái có thể có
        default: 'available'
    },
    description: String,
    images: [String], // Mảng chứa URL ảnh
    isDeleted: { type: Boolean, default: false },
    lastUpdated: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('Vehicle', VehicleSchema);