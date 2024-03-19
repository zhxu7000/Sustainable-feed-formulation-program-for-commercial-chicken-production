import React, { useState, useEffect, useRef } from "react";
import IngredientTable from "./tables/ingredient_table";
import IngredientNutritionTable from "./tables/ingredient_nutrition_table";
import { useLocation } from "react-router-dom";

const Ingredient = () => {
    const location = useLocation();
    const currentId = location.pathname.split("/")[4];

    useEffect(() => {
        // 在路由变化时执行操作
        console.log("Route changed:", location.pathname);
        // 可以执行更新逻辑或其他操作
    }, [location.pathname]);

    return (
        <div className='warp_recipe'>
            <IngredientTable key={currentId + "ingredients"}></IngredientTable>
            <IngredientNutritionTable key={currentId + "ingredientNutritionTable"}></IngredientNutritionTable>
        </div>
    );
};

export default Ingredient;
