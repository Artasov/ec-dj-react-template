import React from 'react';
import ResetPasswordForm from "../components/auth/ResetPasswordForm";

const ResetPassword = () => {
    return (
        <div className={'fccc gap-2 h-80vh'}>
            <h1 className={'fs-2 m-0'}>Reset Password</h1>
            <ResetPasswordForm/>
        </div>
    );
};

export default ResetPassword;
