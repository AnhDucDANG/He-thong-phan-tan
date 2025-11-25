

const mongoose = require('mongoose');

const VehicleSchema = new mongoose.Schema({

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

    locationId: {
    type: String, 
    required: true,
    trim: true,
    index: true // 👈 BẮT BUỘC: Tạo index cho Shard Key
  },
    // Trạng thái hiện tại của xe (Phục vụ cho chức năng Cập nhật trạng thái)
    status: {
        type: String,
        enum: ['available', 'on_rent', 'maintenance', 'out_of_service'], // Các trạng thái có thể có
        default: 'available'
    },
    description: String,
    images: [String], // Mảng chứa URL ảnh
    isDeleted: { type: Boolean, default: false },
    lastUpdated: {
        type: Date,
        default: Date.now
    },
    bookingRecords: [{
    bookingId: { type: mongoose.Schema.Types.ObjectId, ref: 'Booking' },
    startDate: { type: Date, required: true },
    endDate: { type: Date, required: true },
    status: { type: String, enum: ['active', 'completed', 'cancelled'], required: true }
  }]

}, { timestamps: true});

module.exports = mongoose.model('Vehicle', VehicleSchema);