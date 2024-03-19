import { message } from "antd";
import axios from "axios";

const requests = axios.create({
    timeout: 50000,
    //baseURL: 'http://localhost:8000/'
    //headers: { "X-CSRFToken": localStorage.getItem("csrf") },
});
requests.interceptors.request.use(
    function (config) {
        const { method, data } = config;
        /* if (method.toLocaleLowerCase() === 'post') {
            if (data instanceof Object) {
                config.data = qs.stringify(data)
            }
        } */
        config.headers.set("X-CSRFToken", localStorage.getItem("csrf"));
        console.log("header", config.headers);
        return config;
    },
    function (error) {
        console.log("error in request");
        return Promise.reject(error);
    }
);

requests.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        //message.warning(error);
        console.log("error in response");
        return Promise.reject(error);
    }
);

export default requests;
