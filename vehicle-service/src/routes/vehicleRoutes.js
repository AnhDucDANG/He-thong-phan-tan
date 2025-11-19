// vehicle-service/routes/vehicleRoutes.js

const express = require('express');
const router = express.Router(); 
const vehicleController = require('../controllers/vehicleController');

// 1. GET ALL & POST (CRUD)
router.route('/')
    .get(vehicleController.getAllVehicles) // GET http://localhost:8001/api/vehicles
    .post(vehicleController.createVehicle); // POST http://localhost:8001/api/vehicles

// 2. GET ONE, UPDATE, DELETE (CRUD)
router.route('/:id')
    .get(vehicleController.getVehicleById) // GET http://localhost:8001/api/vehicles/:id
    .put(vehicleController.updateVehicle)   // PUT http://localhost:8001/api/vehicles/:id
    .delete(vehicleController.deleteVehicle); // DELETE http://localhost:8001/api/vehicles/:id

module.exports = router;