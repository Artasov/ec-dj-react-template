import React, {useState} from 'react';
import {Button, CircularProgress, FormControl, TextField} from '@mui/material';

const DynamicForm = ({
                         children,
                         className,
                         requestFunc,
                         submitBtnText,
                         submitBtnClassName,
                         loadingClassName,
                         submitDisabled = false
                     }) => {
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (submitDisabled) return;
        setLoading(true);
        try {
            await requestFunc().then(() => {
                setLoading(false);
            });
        } catch (error) {
        }
        setLoading(false);
    };

    const clonedChildren = React.Children.map(children, child => {
        if (!React.isValidElement(child)) return child;

        const {name} = child.props;
        // Проверка, является ли элемент TextField (или другим компонентом, который может иметь свойство helperText)
        if (child.type === TextField) {
            return React.cloneElement(child, {
                disabled: loading,
                helperText: child.props.helperText,
            });
        }
        return React.cloneElement(child, {
            disabled: loading,
        });
    });

    return (
        <form className={`fcc gap-1 pt-2 ${className}`} onSubmit={handleSubmit} noValidate>
            {clonedChildren}
            <FormControl>
                <Button
                    type="submit"
                    disabled={loading || submitDisabled}
                    startIcon={loading &&
                        <CircularProgress size={24}/>}
                >
                    {loading ? 'Loading...' : submitBtnText}
                </Button>
            </FormControl>
        </form>
    );
};

export default DynamicForm;
