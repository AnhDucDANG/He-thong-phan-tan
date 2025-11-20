// vehicle-service/controllers/vehicleController.js

const Vehicle = require('../models/Vehicle');
const USER_SERVICE_URL = process.env.USER_SERVICE_URL;
const axios = require('axios');



// 1. Lấy tất cả phương tiện
exports.getAllVehicles = async (req, res) => {
    try {
        const vehicles = await Vehicle.find();
        res.status(200).json(vehicles);
    } catch (error) {
        res.status(500).json({ message: 'Error retrieving vehicles', error });
    }
};

// 2. Tạo phương tiện mới (Create)
exports.createVehicle = async (req, res) => {
    // 1. Lấy ownerId từ request body
    const { ownerId, ...vehicleData } = req.body; 

    try {
        // --- LOGIC GIAO TIẾP VÀ XÁC THỰC SERVICE-TO-SERVICE ---
        
        // Kiểm tra xem ownerId có được cung cấp không
        if (!ownerId) {
            return res.status(400).json({ message: "Owner ID is required." });
        }
        
        console.log(`Verifying owner ID: ${ownerId} via Tailscale at ${USER_SERVICE_URL}...`);
        
        // 2. Gửi yêu cầu GET đến User Service (Đây là nơi dùng await)
        const userResponse = await axios.get(`${USER_SERVICE_URL}/api/users/${ownerId}`);

        // 3. Xử lý phản hồi: Nếu User Service không tìm thấy ownerId
        if (userResponse.status !== 200 || !userResponse.data) {
             return res.status(404).json({ message: "Owner ID not found in User Service." });
        }
        
        // --- KẾT THÚC GIAO TIẾP ---

        // 4. Lưu phương tiện vào DB (nếu xác thực thành công)
        const newVehicle = new Vehicle(req.body);
        const savedVehicle = await newVehicle.save();
        res.status(201).json(savedVehicle);

    } catch (error) {
        // Xử lý lỗi từ axios (Service của Lâm không chạy, 404, 500, v.v.)
        if (error.response && error.response.status === 404) {
             return res.status(404).json({ message: "Owner ID not found in User Service or API path incorrect." });
        }
        
        // Xử lý lỗi Mongoose/Internal Server Error khác
        console.error("Error details:", error.message);
        res.status(400).json({ 
            message: 'Error creating vehicle or verifying owner', 
            error: error.message || error 
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
        const updatedVehicle = await Vehicle.findByIdAndUpdate(
            req.params.id,
            req.body,
            { new: true, runValidators: true }
        );
        if (!updatedVehicle) {
            return res.status(404).json({ message: 'Vehicle not found' });
        }
        res.status(200).json(updatedVehicle);
    } catch (error) {
        res.status(400).json({ message: 'Error updating vehicle', error });
    }
};

// 5. Xóa phương tiện (Delete)
exports.deleteVehicle = async (req, res) => {
    try {
        const deletedVehicle = await Vehicle.findByIdAndDelete(req.params.id);
        if (!deletedVehicle) {
            return res.status(404).json({ message: 'Vehicle not found' });
        }
        res.status(200).json({ message: 'Vehicle successfully deleted' });
    } catch (error) {
        res.status(500).json({ message: 'Error deleting vehicle', error });
    }
};