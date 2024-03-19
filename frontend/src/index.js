import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { RouterProvider } from "react-router-dom";
import "./index.css";
import { ConfigProvider, theme } from "antd";
import router from "./router";
import { defaultTheme } from "antd/es/theme/context";

ReactDOM.createRoot(document.getElementById("root")).render(
    <ConfigProvider
        theme={{
            token: {
                colorPrimary: "#5b9bbc",
                fontFamily: "Segoe UI Symbol",
                //colorLink: "#212b30",
                //borderRadius: 2,
                //colorBgContainer: "#f6ffed",
            },
        }}>
        <RouterProvider router={router} />
    </ConfigProvider>
);

/* const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); */

//ReactDOM.render(<App></App>,document.getElementById("root"))
