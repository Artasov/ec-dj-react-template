import { useContext } from 'react';
import { AuthContext } from "./AuthContext";
import axiosInstance from "./axiosConfig";

export const useAuth = () => {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    const updateCurrentUser = async () => {
        const userResponse = await axiosInstance.get('/api/v1/current_user/');
        context.setUser(userResponse.data);
    }

    const login = async (username, password) => {
        console.log('LOGIN START')
        const response = await axiosInstance.post('/api/v1/token/', { username, password });
        console.log('LOGIN RESPONSE')
        localStorage.setItem('access', response.data.access);
        localStorage.setItem('refresh', response.data.refresh);
        await updateCurrentUser();
        context.setIsAuthenticated(true);  // Устанавливаем аутентификацию после успешного входа
        console.log('LOGIN END')
    };

    return { ...context, updateCurrentUser, login };
};
