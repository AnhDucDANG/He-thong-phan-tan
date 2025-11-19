# vehicle-service/Dockerfile

# Sử dụng Node.js phiên bản LTS (Long-Term Support)
FROM node:20-alpine

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép package.json và package-lock.json (để tận dụng cache)
COPY package*.json ./

# Cài đặt dependencies (chỉ dependencies chính, không phải devDependencies như nodemon)
RUN npm install --omit=dev

# Sao chép toàn bộ mã nguồn vào thư mục làm việc
COPY . .

# Mở cổng cho ứng dụng (cổng 8001 đã định nghĩa trong server.js)
EXPOSE 8001

# Lệnh khởi động ứng dụng
CMD ["node", "server.js"]