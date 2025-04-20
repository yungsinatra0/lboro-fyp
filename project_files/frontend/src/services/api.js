import axios from 'axios'
import router from '../router/index'

/**
 * API instance used to make requests to the backend server
 */
const api = axios.create({
    baseURL: 'http://localhost:8000', // Backend server URL
    withCredentials: true // This will allow the browser to store the cookie and send it back to the server with each request
})

/**
 * Axios interceptor to add the Authorization header to each request
 */
api.interceptors.request.use(function(config) {
    return config
})

/**
 * Axios interceptor to handle responses and errors, used to handle authentication errors
 * Redirects to login page on 401 errors (except for auth-related endpoints)
 * Prevents infinite redirect loops by excluding certain endpoints
 */
api.interceptors.response.use(
    function (response) { // Will be triggered with any response status code in the 2xx range
        return response; 
    }, 
    function (error) { // Will be triggered with any response status code outside the 2xx range

        const authEndpoints = ['/login', '/register', '/logout', '/me']

        // Preventing infinite redirect loops by checking if the request URL is not in the authEndpoints array
        // If the response status is 401 (Unauthorized) and the request URL is not in the authEndpoints array, redirect to login page
        if (error.response.status === 401 && !authEndpoints.some(endpoint => error.config.url.includes(endpoint))) { 
            router.push('/login')
        }

        return Promise.reject(error)
    }
)

export default api