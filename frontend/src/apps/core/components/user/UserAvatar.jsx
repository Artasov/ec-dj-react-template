import React from 'react';
import Avatar from '@mui/material/Avatar';
import PersonIcon from '@mui/icons-material/Person';

const UserAvatar = ({avatar, size, sx, className, zIndex = 2}) => {
    const avatarStyle = {
        width: size,
        height: size,
    };

    return (<>
        {avatar ?
            <div style={{
                ...sx,
                zIndex: zIndex
            }} className={`${className} w-min`}>
                <div className={'position-relative'} style={avatarStyle}>
                    <img className='object-fit-cover rounded-circle' style={{
                        ...avatarStyle,
                        zIndex: zIndex
                    }} src={avatar} alt="User Avatar"/>
                    <img className='object-fit-cover rounded-circle position-absolute'
                         style={{
                             fontSize: '16px',
                             width: size,
                             height: size,
                             filter: 'blur(10px)',
                             opacity: '40%',
                             bottom: '-4px',
                             right: '-4px',
                             zIndex: zIndex-1
                         }} src={avatar} alt="User Avatar"/>
                </div>
            </div>
            :
            <div style={sx} className={`${className} w-min`}>
                <div className={'position-relative'} style={avatarStyle}>
                    <Avatar sx={{
                        maxWidth: '100%',
                        maxHeight: '100%',
                        width: size,
                        height: size,
                        zIndex: zIndex,
                    }}>
                        <PersonIcon style={{
                            width: `80%`,
                            height: `80%`
                        }}/>
                    </Avatar>
                    <Avatar sx={{
                        maxWidth: '100%',
                        maxHeight: '100%',
                        position: 'absolute',
                        width: size,
                        height: size,
                        filter: 'blur(10px)',
                        opacity: '40%',
                        bottom: '-4px',
                        right: '-4px',
                        zIndex: zIndex - 1
                    }}>
                        <PersonIcon style={{
                            width: `80%`,
                            height: `80%`,
                        }}/>
                    </Avatar>
                </div>
            </div>

        }
    </>);
};

export default UserAvatar;