import Home from "../container/home/home";
import Login from "../container/login/login";
import Recipe from "../container/home/recipe";
import Ingredient from "../container/home/ingredient";
import { RouterAuth } from "./routerAuth";
import React from "react";
import { Navigate, createBrowserRouter } from "react-router-dom";
import User from "../container/home/user/user";

const router = createBrowserRouter([
    {
        path: "/",
        element: <Navigate to={`/product/${localStorage.getItem("first")}/recipe`}></Navigate>,
        /* children: [
      {
        path: "login",
        element: <Login />,
      },
      {
        path: "home",
        element: <Home />,
      },
    ], */
    },
    {
        path: "/login",
        element: <Login></Login>,
    },
    {
        path: "/product/:id",
        element: (
            <RouterAuth>
                <Home />
            </RouterAuth>
        ),
        children: [
            {
                path: "recipe",
                element: <Recipe />,
            },
            {
                path: "ingredient/:id",
                element: <Ingredient />,
            },
            {
                path: "user",
                element: <User></User>,
            },
        ],
    },
]);

export default router;
