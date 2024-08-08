import React, {useEffect} from 'react';
import {useNavigate} from 'react-router-dom';
import {useAuth} from "../../components/auth/useAuth";
import {AuthContext} from "../../components/auth/AuthContext";
import SignInForm from "../../components/auth/SignInForm";

const SignIn = () => {
    const {user, isAuthenticated} = useAuth(AuthContext);
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated === null) return;
        if (isAuthenticated) {
            navigate('/profile/');
        }
    }, [isAuthenticated, navigate]);

    return (
        <div className={'maxw-600px w-90 mx-auto'}>
            <SignInForm/>
        </div>
    );
};

export default SignIn;
