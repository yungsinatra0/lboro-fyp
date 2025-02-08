import axios from 'axios'
import router from '../router'

const api = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: true // This will allow the browser to store the cookie and send it back to the server with each request
})

// Use the interceptor to send user back to login page if their session expires as the cookie is handled automatically by the browser
api.interceptors.response.use(
    function (response) { // From Axios documentation, this will be triggered with any response status code in the 2xx range
        return response; 
    }, 
    function (error) { // From Axios documentation, this will be triggered with any response status code outside the 2xx range
        if (error.response.status === 401) { // Specifically checking for 401 Unauthorized status code
            router.push('/login')
        }

        return Promise.reject(error)
    }
)