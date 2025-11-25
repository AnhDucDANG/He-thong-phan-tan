const mongoose = require('mongoose');
const Vehicle = require('./Vehicle'); // Import model Vehicle của bạn

const mongoURI = 'mongodb://localhost:27017/vehicles'; // Thay bằng URI của bạn

mongoose.connect(mongoURI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(async () => {
    console.log('MongoDB Connected');

    const vehiclesToInsert = [];
    const makes = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes'];
    const models = ['Camry', 'City', 'Everest', 'X5', 'C-Class'];
    const locations = ['HA_NOI', 'DA_NANG', 'HO_CHI_MINH'];

    for (let i = 1; i <= 50; i++) {
      vehiclesToInsert.push({
        make: makes[i % makes.length],
        model: models[i % models.length],
        year: 2020 + (i % 5),
        licensePlate: `ABC${i.toString().padStart(5, '0')}`, // Tạo biển số duy nhất
        dailyRate: 500000 + (i * 10000),
        locationId: locations[i % locations.length],
        status: 'available',
        description: `Xe thứ ${i} rất tốt.`,
        images: []
      });
    }

    try {
      await Vehicle.insertMany(vehiclesToInsert);
      console.log('Đã chèn thành công 50 bản ghi xe!');
    } catch (err) {
      console.error('Lỗi khi chèn dữ liệu:', err);
    } finally {
      mongoose.connection.close();
    }
  })
  .catch(err => console.log(err));