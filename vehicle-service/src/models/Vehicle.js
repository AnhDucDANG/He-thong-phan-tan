// vehicle-service/models/Vehicle.js

const mongoose = require('mongoose');

const VehicleSchema = new mongoose.Schema({
    // ID xe (MongoDB tự tạo)

    licensePlate: {
        type: String,
        required: [true, 'Biển số xe là bắt buộc'],
        unique: true, // Rất quan trọng: Mỗi xe có 1 biển số duy nhất
        trim: true
    },
    model: {
        type: String,
        required: [true, 'Tên mẫu xe là bắt buộc']
    },
    make: String, // Hãng xe (VD: Toyota, Ford)
    year: Number, // Năm sản xuất
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
    lastUpdated: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('Vehicle', VehicleSchema);