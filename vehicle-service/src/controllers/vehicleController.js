// vehicle-service/controllers/vehicleController.js

const Vehicle = require('../models/Vehicle');

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
    try {
        const newVehicle = new Vehicle(req.body);
        const savedVehicle = await newVehicle.save();
        res.status(201).json(savedVehicle);
    } catch (error) {
        res.status(400).json({ message: 'Error creating vehicle', error });
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