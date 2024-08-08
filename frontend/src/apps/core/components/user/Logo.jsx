import React from 'react';


const Logo = ({height, width, className}) => {
    return (
        <img style={{height: height, width: width ? width : 'unset'}}
             className={`${className} logo d-inline-block align-top rounded-2 object-fit-cover`}
             alt="Logo"/>
    );
}

export default Logo;