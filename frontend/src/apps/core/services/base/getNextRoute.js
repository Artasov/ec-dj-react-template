export const getNextRoute = () => {
    const params = new URLSearchParams(location.search);
    return params.get('next') || '/';
};