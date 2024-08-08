import React, {createContext, useEffect, useState} from 'react';
import axiosInstance from "./axiosConfig";
import {useNavigate} from "react-router-dom";

export const AuthContext = createContext(undefined);

export const AuthProvider = ({children}) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const access = localStorage.getItem('access');
        if (access) {
            axiosInstance.get('/api/v1/current_user/')
                .then(response => {
                    setUser(response.data);
                    console.log('USER')
                    console.log(response.data)
                    setIsAuthenticated(true);
                })
                .catch(() => {
                    navigate('/signin/');
                    localStorage.removeItem('access');
                    localStorage.removeItem('refresh');
                    setIsAuthenticated(false);
                });
        } else {
            setIsAuthenticated(false);
        }
    }, [user]);

    const frontendLogout = () => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        setUser(null);
        setIsAuthenticated(false);
    };

    const logout = () => {
        axiosInstance.post('/api/v1/logout/')
            .then(response => {
                frontendLogout();
                console.log('Logout success.');
            })
            .catch(() => {
                console.log('Logout error.');
            });
    };

    return (
        <AuthContext.Provider value={{
            user,
            setUser,
            isAuthenticated,
            logout,
            frontendLogout,
            setIsAuthenticated,
        }}>
            {children}
        </AuthContext.Provider>
    );
};
