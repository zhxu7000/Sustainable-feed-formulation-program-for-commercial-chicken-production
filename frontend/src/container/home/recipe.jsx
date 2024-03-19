import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import NutritionTable from "./tables/nutrition_table";
import RecipeTable from "./tables/recipe_table";
import RecipePieChart from "./tables/RecipePieChart";
import CostPieChart from "./tables/CostPieChart";
import { Button, Tabs } from "antd";

const Recipe = () => {
    const location = useLocation();
    const currentId = location.pathname.split("/")[2];

    /* useEffect(() => {
        // 在路由变化时执行操作
        console.log("Route changed:", location.pathname);
        // 可以执行更新逻辑或其他操作
    }, [location.pathname]); */

    return (
        <div>
            <div className='warp_recipe'>
                <NutritionTable key={currentId + "nutritionNeeded"}></NutritionTable>
                <RecipeTable key={currentId + "ingredientInrecipe"}></RecipeTable>
            </div>
            <div className="pie_charts_container">
                <div className="single_pie_chart">
                    {/* 传递recipeId到RecipePieChart */}
                    <RecipePieChart recipeId={currentId} />
                </div>
                <div className="single_pie_chart">
                    {/* 如果CostPieChart也需要recipeId, 可以传递 */}
                    <CostPieChart recipeId={currentId} />
                </div>
            </div>
        </div>
    );
};

export default Recipe;
