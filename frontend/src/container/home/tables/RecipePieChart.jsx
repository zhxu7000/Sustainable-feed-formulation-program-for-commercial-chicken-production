import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Tooltip, Legend, Cell } from 'recharts';
import { getMaterialCostWeightPercentage } from "../../../api";

const COLORS = [
    '#0088FE',  // 蓝色
    '#00C49F',  // 青色
    '#FFBB28',  // 橙色
    '#FF8042',  // 橙红色
    '#FF00FF',  // 玫瑰红
    '#800080',  // 紫色
    '#00FFFF',  // 天蓝色
    '#FF0000',  // 红色
    '#01DF3A',  // 绿色
    '#FF00BF',  // 粉红色
    '#424242',  // 深灰色
    '#F4FA58',  // 青黄色
    '#FA58D0',  // 淡粉红色
    '#2EFE64',  // 草绿色
    '#58D3F7'   // 浅天蓝色
];

const defaultData = [
    { name: 'Material A', value: 100 },
    { name: 'Material B', value: 300 },
    { name: 'Material C', value: 300 },
];

const RecipePieChart = ({ recipeId }) => {
    const [chartData, setChartData] = useState(defaultData);

    useEffect(() => {
        async function fetchData() {
            try {
                const response = await getMaterialCostWeightPercentage({ recipeId });
    
                // Check if response exists
                if (!response) {
                    console.error("Error fetching data for RecipePieChart: No response received.");
                    return; // Exit the function
                }
    
                if (Array.isArray(response)) {
                    const transformedData = response.map(item => ({
                        name: item.material_name,
                        value: item.optimal_percentage * 100
                    }));
                    setChartData(transformedData);
                } else if (response.status && response.status === "success") {
                    console.error("Error fetching data for RecipePieChart: Unexpected response format. Expected an array.");
                    console.error("Full response object:", response);
                } else {
                    const errorMessage = response.message || `Unknown error occurred. Status: ${response.status}`;
                    console.error("Error fetching data for RecipePieChart:", errorMessage);
                    console.error("Full response object:", response);
                }
            } catch (error) {
                console.error("Exception occurred while fetching data for RecipePieChart:", error);
            }
        }
        fetchData();
    }, [recipeId]);


    return (
        <PieChart width={500} height={500}>
            <Pie
                dataKey="value"
                isAnimationActive={false}
                data={chartData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                label={(entry) => `${entry.value.toFixed(2)}%`}
            >
                {
                    chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))
                }
            </Pie>
            <Tooltip />
            <Legend />
        </PieChart>
    );
};

export default RecipePieChart;
