const axios = require('axios');

// Hàm gọi sang User Service để kiểm tra User có tồn tại không
exports.validateOwner = async (ownerId) => {
  try {
    const url = `${process.env.USER_SERVICE_URL}/${ownerId}`;
    // Gọi GET /api/users/{id}
    const response = await axios.get(url);
    
    // Nếu status 200 => User tồn tại
    return response.status === 200;
  } catch (error) {
    // Nếu lỗi 404 => User không tồn tại
    if (error.response && error.response.status === 404) {
      return false;
    }
    // Các lỗi khác (mất mạng, server Lâm sập)
    console.error('Error contacting User Service:', error.message);
    throw new Error('Cannot verify owner at this time');
  }
};