import React, { useState } from 'react';
import axios from 'axios';

// ĐỊNH NGHĨA URL LOGIN (Cần trỏ tới API Gateway hoặc User Service của Lâm)
// Giả sử User Service/API Gateway chạy ở cổng 8000
const LOGIN_URL = 'http://localhost:8002'; 
//http://localhost:8002/api/users/login

function LoginPage() {
    // Quản lý trạng thái form
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showPassword, setShowPassword] = useState(false);

    // Xử lý logic Đăng nhập
    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Gửi yêu cầu POST đến User Service
            const response = await axios.post(LOGIN_URL, { 
                email: email, 
                password: password 
            });

            // Lấy token và lưu vào LocalStorage (Sau này dùng để gọi Service khác)
            const token = response.data.token;
            localStorage.setItem('authToken', token);

            // Xử lý thành công: Chuyển hướng hoặc hiển thị thông báo
            alert("Đăng nhập thành công! Token đã được lưu.");
            // Ví dụ: Chuyển hướng người dùng đến trang quản lý xe
            // window.location.href = '/vehicles'; 

        } catch (err) {
            // Xử lý lỗi: Hiển thị thông báo lỗi từ server (nếu có)
            const errorMessage = err.response 
                ? err.response.data.message || 'Lỗi: Sai email hoặc mật khẩu.'
                : 'Lỗi kết nối đến Server. Vui lòng kiểm tra cổng API.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    // --- JSX CODE (Chuyển đổi từ HTML tĩnh) ---
    return (
        <div className="relative flex h-auto min-h-screen w-full flex-col group/design-root overflow-x-hidden">
            <div className="layout-container flex h-full grow flex-col">
                <div className="flex flex-1 justify-center items-center py-5 px-4 md:px-10 lg:px-20">
                    <div className="layout-content-container flex flex-col lg:flex-row max-w-6xl flex-1 bg-white dark:bg-slate-900 rounded-xl shadow-lg overflow-hidden">
                        
                        {/* Khu vực Form Đăng nhập */}
                        <div className="w-full lg:w-1/2 p-8 sm:p-12 flex flex-col justify-center">
                            <div className="max-w-md mx-auto w-full">
                                <div className="flex flex-col gap-3 mb-6">
                                    <p className="text-[#0d141c] dark:text-white text-3xl sm:text-4xl font-black leading-tight tracking-[-0.033em]">Chào mừng trở lại</p>
                                    <p className="text-[#49739c] dark:text-slate-400 text-base font-normal leading-normal">Đăng nhập để quản lý và đặt xe của bạn</p>
                                </div>
                                <div className="pb-3">
                                    <div className="flex border-b border-[#cedbe8] dark:border-slate-700 gap-8">
                                        <a className="flex flex-col items-center justify-center border-b-[3px] border-b-primary text-[#0d141c] dark:text-white pb-[13px] pt-4" href="#">
                                            <p className="text-sm font-bold leading-normal tracking-[0.015em]">Đăng nhập</p>
                                        </a>
                                        <a className="flex flex-col items-center justify-center border-b-[3px] border-b-transparent text-[#49739c] dark:text-slate-400 pb-[13px] pt-4" href="#">
                                            <p className="text-sm font-bold leading-normal tracking-[0.015em]">Đăng ký</p>
                                        </a>
                                    </div>
                                </div>

                                {/* BẮT ĐẦU FORM */}
                                <form className="flex flex-col gap-4 mt-4" onSubmit={handleLogin}>
                                    
                                    {/* Hiển thị lỗi */}
                                    {error && (
                                        <div className="p-3 bg-red-100 text-red-700 rounded-lg text-sm">
                                            {error}
                                        </div>
                                    )}

                                    {/* Email/Số điện thoại */}
                                    <div className="flex flex-col">
                                        <label className="flex flex-col min-w-40 flex-1">
                                            <p className="text-[#0d141c] dark:text-slate-200 text-base font-medium leading-normal pb-2">Email hoặc Số điện thoại</p>
                                            <input 
                                                className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#0d141c] dark:text-white focus:outline-0 focus:ring-0 border border-[#cedbe8] dark:border-slate-600 bg-background-light dark:bg-background-dark focus:border-primary h-14 placeholder:text-[#49739c] dark:placeholder:text-slate-500 p-[15px] text-base font-normal leading-normal" 
                                                placeholder="Nhập email hoặc số điện thoại của bạn" 
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                            />
                                        </label>
                                    </div>
                                    
                                    {/* Mật khẩu */}
                                    <div className="flex flex-col">
                                        <label className="flex flex-col min-w-40 flex-1">
                                            <p className="text-[#0d141c] dark:text-slate-200 text-base font-medium leading-normal pb-2">Mật khẩu</p>
                                            <div className="flex w-full flex-1 items-stretch">
                                                <input 
                                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-l-lg text-[#0d141c] dark:text-white focus:outline-0 focus:ring-0 border border-[#cedbe8] dark:border-slate-600 bg-background-light dark:bg-background-dark focus:border-primary h-14 placeholder:text-[#49739c] dark:placeholder:text-slate-500 p-[15px] border-r-0 pr-2 text-base font-normal leading-normal" 
                                                    placeholder="Nhập mật khẩu của bạn" 
                                                    type={showPassword ? "text" : "password"} // Thay đổi type
                                                    value={password}
                                                    onChange={(e) => setPassword(e.target.value)}
                                                />
                                                <div 
                                                    className="text-[#49739c] dark:text-slate-400 flex border border-[#cedbe8] dark:border-slate-600 bg-background-light dark:bg-background-dark items-center justify-center px-[15px] rounded-r-lg border-l-0"
                                                    onClick={() => setShowPassword(!showPassword)} // Thêm sự kiện click
                                                >
                                                    {/* Lưu ý: Cần thêm gói Material Icons vào dự án */}
                                                    <span className="material-symbols-outlined cursor-pointer">
                                                        {showPassword ? 'visibility_off' : 'visibility'}
                                                    </span>
                                                </div>
                                            </div>
                                        </label>
                                    </div>
                                    
                                    {/* Ghi nhớ và Quên mật khẩu */}
                                    <div className="flex items-center justify-between mt-2">
                                        <div className="flex items-center gap-2">
                                            <input className="form-checkbox h-4 w-4 rounded text-primary focus:ring-primary border-slate-300 dark:border-slate-600 bg-background-light dark:bg-background-dark" id="remember" type="checkbox"/>
                                            <label className="text-sm text-[#49739c] dark:text-slate-400" htmlFor="remember">Ghi nhớ đăng nhập</label>
                                        </div>
                                        <a className="text-sm font-medium text-primary hover:underline" href="#">Quên mật khẩu?</a>
                                    </div>
                                    
                                    {/* Nút Đăng nhập */}
                                    <button 
                                        className="w-full mt-4 h-14 rounded-lg bg-primary text-white text-base font-bold flex items-center justify-center hover:bg-primary/90 transition-colors" 
                                        type="submit"
                                        disabled={loading} // Vô hiệu hóa khi đang loading
                                    >
                                        {loading ? 'Đang xử lý...' : 'Đăng nhập'}
                                    </button>
                                    
                                    {/* Các nút Đăng nhập bên thứ ba */}
                                    <div className="relative flex items-center my-4">
                                        <div className="flex-grow border-t border-slate-300 dark:border-slate-700"></div>
                                        <span className="flex-shrink mx-4 text-sm text-slate-400 dark:text-slate-500">Hoặc tiếp tục với</span>
                                        <div className="flex-grow border-t border-slate-300 dark:border-slate-700"></div>
                                    </div>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        {/* Lưu ý: Cần thay thế các URL ảnh thật cho Google và Facebook */}
                                        <button className="w-full h-12 rounded-lg bg-white dark:bg-slate-800 text-[#0d141c] dark:text-white text-sm font-medium border border-slate-300 dark:border-slate-600 flex items-center justify-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors" type="button">
                                            <img alt="Google logo" className="h-5 w-5" src="https://vi.wikipedia.org/wiki/T%E1%BA%ADp_tin:Google_%22G%22_logo.svg#/media/T%E1%BA%ADp_tin:Google_%22G%22_logo.svg"/>
                                            <span>Google</span>
                                        </button>
                                        <button className="w-full h-12 rounded-lg bg-white dark:bg-slate-800 text-[#0d141c] dark:text-white text-sm font-medium border border-slate-300 dark:border-slate-600 flex items-center justify-center gap-2 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors" type="button">
                                            <img alt="Facebook logo" className="h-5 w-5" src="https://upload.wikimedia.org/wikipedia/commons/c/cd/Facebook_logo_%28square%29.png"/>
                                            <span>Facebook</span>
                                        </button>
                                    </div>
                                </form>
                                {/* KẾT THÚC FORM */}

                            </div>
                        </div>
                        
                        {/* Khu vực Ảnh minh họa */}
                        <div className="hidden lg:flex w-1/2 bg-slate-50 dark:bg-background-dark p-4 items-center justify-center">
                            <div className="w-full h-full gap-1 overflow-hidden aspect-[2/3] rounded-lg flex">
                                <div className="w-full bg-center bg-no-repeat bg-cover aspect-auto rounded-lg flex-1" style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=1966&auto=format&fit=crop")' }}></div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;