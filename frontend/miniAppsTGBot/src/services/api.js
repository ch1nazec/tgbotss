import axios from "axios";


const api = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    },
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('user_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error);
    }
)


api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          localStorage.removeItem('user_token');
          break;
        case 403:
          console.error('Forbidden action.');
          break;
        case 500:
          console.error('Internal Server Error. Try again later.');
          break;
      }
    }
    return Promise.reject(error);
  }
);

export default api;