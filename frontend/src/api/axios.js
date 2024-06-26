import axios from "axios";
import { useNavigate } from "react-router-dom";
const request = axios.create({
  baseURL: "https://dog-go.store/",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

const refreshToken = async () => {
  try {
    const response = await request.post(
      "api/v1/user/simple/jwt_refresh_token",
      {}
    );
    const newAccessToken = response.data.access;
    console.log("새로운 액세스 토큰:", newAccessToken);
    localStorage.setItem("token", newAccessToken);
    return newAccessToken;
  } catch (error) {

    throw error;
  }
};

request.interceptors.request.use(
  async (config) => {
    const accessToken = localStorage.getItem("token");
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

request.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return request(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newAccessToken = await refreshToken();
        processQueue(null, newAccessToken);
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return request(originalRequest);

      } catch (error) {
        if(error.response.status === 400){
          localStorage.removeItem("token")
          alert("로그인이 만료되었습니다. 다시 로그인 해주세요.")
          useNavigate("/login")
        }
     
        throw error;

      }
    }
    return Promise.reject(error);
  }
);

export default request;
