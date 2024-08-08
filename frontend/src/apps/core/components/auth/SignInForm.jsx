import React, {useState} from 'react';
import TextField from '@mui/material/TextField';
import {useAuth} from "./useAuth";
import DynamicForm from "../elements/DynamicForm";
import {useNavigate} from "react-router-dom";

const SignInForm = ({className}) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const {login} = useAuth();
    const navigate = useNavigate();

    const signIn = async () => {
        try {
            if (!username || !password) {
                console.log('Username/Email and password fields are required');
                return;
            }
            await login(username, password);
            console.log('Success Login')
        } catch (error) {
            console.log(error);
        }
    };
    const signUpRedirect = () => {
        navigate('/signup/')
    }

    return (<div className={'fc'}>
        <DynamicForm className={className}
                     requestFunc={signIn}
                     submitBtnText={'Sign In'}>
            <TextField
                label="Username / Email"
                variant="outlined"
                type="text"
                helperText="Enter your username or email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                fullWidth
                margin="dense"
            />
            <TextField
                label="Password"
                variant="outlined"
                type="password"
                helperText="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                fullWidth
                margin="dense"
            />
        </DynamicForm>
        <small className={'fc mt-2 text-right'}>
            <span className={`mt-3px fs-6`}
                  onClick={() => {
                      navigate('/reset-password');
                  }}>
                Forgot password?
            </span>
            <span onClick={signUpRedirect}
                  className={`mt-3px fs-6 cursor-pointer hover-scale-2`}>
                    Create your account now.
                </span>
        </small>
    </div>);
};

export default SignInForm;
