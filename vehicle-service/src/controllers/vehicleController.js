// vehicle-service/controllers/vehicleController.js

const Vehicle = require('../models/Vehicle');
const userService = require('../services/userService');
const USER_SERVICE_URL = process.env.USER_SERVICE_URL;
const axios = require('axios');



// 1. Lấy tất cả phương tiện
exports.getAllVehicles = async (req, res) => {
    try {
    const { status, make } = req.query;
    const filter = {};
    
    if (status) filter.status = status;
    if (make) filter.make = make;

    const vehicles = await Vehicle.find(filter).sort({ createdAt: -1 });
    res.status(200).json(vehicles);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// 2. Tạo phương tiện mới (Create)
exports.createVehicle = async (req, res) => {
    
    const vehicleData = req.body;

    // --- BƯỚC 1: VALIDATION CÁC TRƯỜNG TỪ SCHEMA ---
    const { 
        make, 
        model, 
        year, 
        licensePlate, 
        dailyRate, 
        transmission, 
        location 
    } = vehicleData;
    
    // Kiểm tra các trường BẮT BUỘC theo VehicleSchema
    if (!make || !model || !year || !licensePlate || !dailyRate || !transmission || 
        !location || !location.coordinates || location.coordinates.length !== 2) {
        
        return res.status(400).json({ 
            message: "Thiếu các thông tin bắt buộc: Hãng, Dòng xe, Năm, Biển số, Giá thuê, Hộp số hoặc Tọa độ Vị trí." 
        });
    }

    try {
        // --- BƯỚC 2: LƯU PHƯƠNG TIỆN VÀO DB ---
        
        const newVehicle = new Vehicle(vehicleData);
        const savedVehicle = await newVehicle.save();
        
        res.status(201).json({
            message: "Đăng ký xe thành công theo dữ liệu đã cung cấp.",
            data: savedVehicle
        });

    } catch (error) {
        // --- BƯỚC 3: XỬ LÝ LỖI (CHỦ YẾU LÀ LỖI DB) ---
        
        // Xử lý lỗi Mongoose validation hoặc lỗi biển số xe bị trùng (unique: true)
        if (error.name === 'ValidationError' || error.code === 11000) {
            console.error("Database Validation/Unique Error:", error.message);
            return res.status(400).json({
                message: 'Lỗi dữ liệu: Biển số xe đã tồn tại hoặc thiếu trường bắt buộc.',
                error: error.message
            });
        }
        
        console.error("Internal Server Error:", error.message);
        res.status(500).json({ 
            message: 'Lỗi server nội bộ khi lưu dữ liệu xe.', 
            error: error.message 
        });
    }
};

// 3. Lấy phương tiện theo ID (Read One)
exports.getVehicleById = async (req, res) => {
    try {
        const vehicle = await Vehicle.findById(req.params.id);
        if (!vehicle) {
            return res.status(404).json({ message: 'Vehicle not found' });
        }
        res.status(200).json(vehicle);
    } catch (error) {
        res.status(500).json({ message: 'Error retrieving vehicle', error });
    }
};

// 4. Cập nhật phương tiện (Update)
exports.updateVehicle = async (req, res) => {
    try {
    const vehicle = await Vehicle.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!vehicle) return res.status(404).json({ message: 'Vehicle not found' });
    res.status(200).json(vehicle);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// 5. Xóa phương tiện (Delete)
exports.deleteVehicle = async (req, res) => {
    try {
    // Không xóa thật, chỉ update cờ isDeleted
    const vehicle = await Vehicle.findByIdAndUpdate(req.params.id, { isDeleted: true }, { new: true });
    if (!vehicle) return res.status(404).json({ message: 'Vehicle not found' });
    res.status(200).json({ message: 'Vehicle deleted successfully (Soft delete)' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};