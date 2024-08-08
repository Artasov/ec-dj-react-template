import React from 'react';
import './header.css';
import Logo from "../user/Logo";

export const headerHeight = 80;

const Header = () => {

    return (
        <header className={`frbc gap-4 px-4`} style={{height: headerHeight}}>
            <Logo height={45}/>
            <div className={'frcc gap-4'} style={{marginTop: "5px"}}>

            </div>
        </header>
    );
};

export default Header;
