import React, {Component} from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import Header from './apps/core/components/Header/Header';
import 'bootstrap/dist/css/bootstrap.min.css';
import './apps/core/static/css/bootstrap_overwrite.css';
import './apps/core/static/css/style.css';
import './apps/core/static/css/wide-classes.css';
import './apps/core/static/css/base.css';
import {AuthProvider} from './apps/core/components/auth/AuthContext';
import 'react-toastify/dist/ReactToastify.css';
import './apps/core/static/css/ReactToastify.css';

import SignIn from "./apps/core/pages/auth/SignIn";


class App extends Component {
    render() {
        return (
            <Router>
                <AuthProvider>
                    <ToastAndMain/>
                </AuthProvider>
            </Router>
        );
    }
}

const ToastAndMain = () => {
    return (
        <>
            <div className={`App h-100 fc disable-tap-select`}>
                <Header/>
                <main className={`overflow-y-auto no-scrollbar w-100`}>
                    <Routes>
                        <Route path="/" element={<SignIn/>}/>
                    </Routes>
                </main>
            </div>
        </>
    );
};

export default App;
