import React, { useContext, useEffect, useRef, useState } from "react";
import { Button, Form, Input, Popconfirm, Table, Tabs, InputNumber } from "antd";
import { EditableCell, EditableRow, EditableContext } from "./editable_table";
import { reqAttributeCRUD, reqBestRecipeCRUD, reqCalculate, reqRecipeRatioCRUD, reqSetTonne } from "../../../api";
import { useLocation } from "react-router-dom";

function RecipeTable() {
    const [dataSource, setDataSource] = useState([
        {
            id: "0",
            material_name: "ingredient 0",
            value: 20,
        },
        {
            id: "1",
            material_name: "ingredient 1",
            value: 80,
        },
    ]);
    const [count, setCount] = useState(2);
    const handleDelete = (key) => {
        const newData = dataSource.filter((item) => item.key !== key);
        setDataSource(newData);
    };
    const defaultColumns = [
        {
            title: "Ingredient",
            dataIndex: "material_name",
            width: "40%",
        },
        {
            title: "Value (%)",
            dataIndex: "value",
            width: "30%",
        },
        {
            title: `Total Weight(kg)`,
            dataIndex: "value",
            width: "30%",
            render: (_, record) => {
                return (record.value * tonValue * 10).toFixed(3);
            },
        },
        /*  {
            title: "operation",
            dataIndex: "operation",
            render: (_, record) =>
                dataSource.length >= 1 ? (
                    <Popconfirm title='Sure to delete?' onConfirm={() => handleDelete(record.key)}>
                        <a>Delete</a>
                    </Popconfirm>
                ) : null,
        }, */
    ];

    const [nutritionSource, setNutritionSource] = useState([
        {
            id: "0",
            nutrition_name: "nutririon 0",
            value: 10,
        },
        {
            id: "1",
            nutrition_name: "nutririon 1",
            value: 30,
        },
    ]);
    const [nutritionLimit, setNutritionLimit] = useState([
        {
            id: "0",
            attribute_name: "nutririon 0",
            max_value: 10,
            min_value: 5,
        },
        {
            id: "1",
            attribute_name: "nutririon 1",
            max_value: 30,
            min_value: 0,
        },
    ]);
    const nutritionColumns = [
        {
            title: "Nutrition",
            dataIndex: "nutrition_name",
            width: "55%",
            editable: true,
        },
        {
            title: "Value(kg)",
            dataIndex: "value",
            width: "20%",
            render: (_, record) => {
                const nutrient = nutritionLimit.find((item) => item.attribute_name == record.nutrition_name);
                console.log(nutrient.min_value, record.value);
                if (nutrient.min_value == record.value * 10) {
                    return <span style={{ color: "red" }}>{record.value * 10} (Min value)</span>;
                }
                if (nutrient.max_value == record.value * 10) {
                    return <span style={{ color: "red" }}>{record.value * 10} (Max value)</span>;
                }
                return record.value * 10;
            },
        },
    ];

    const [ratioData, setRatioData] = useState([
        {
            id: "0",
            nutrition_1_id: 57,
            nutrition_2_id: 60,
            nutrition_1_name: "nutririon 0",
            nutrition_2_name: "nutririon 1",
        },
    ]);

    const ratioColumns = [
        {
            title: "Ratio",
            dataIndex: "attribute_name",
            width: "60%",
            render: (_, record) => {
                return (
                    <span>
                        {record.nutrition_1_name} / {record.nutrition_2_name}
                    </span>
                );
            },
        },
        {
            title: "Value",
            dataIndex: "value",
            width: "30%",
            render: (_, record) => {
                let val1 = 0;
                let val2 = 0;
                nutritionSource.forEach((item) => {
                    if (item.nutrition_id == record.nutrition_1_id) {
                        val1 = item.value;
                    }
                    if (item.nutrition_id == record.nutrition_2_id) {
                        val2 = item.value;
                    }
                });
                console.log(val1, val2);
                return <span>{(val1 / val2).toFixed(4)}</span>;
            },
        },
    ];

    const handleAdd = () => {
        const newData = {
            key: count,
            ingredient: `ingredient ${count}`,
        };
        setDataSource([...dataSource, newData]);
        setCount(count + 1);
    };
    const handleSave = (row) => {
        const newData = [...dataSource];
        const index = newData.findIndex((item) => row.key === item.key);
        const item = newData[index];
        newData.splice(index, 1, {
            ...item,
            ...row,
        });
        /* console.log("item",item)
        console.log("row", row);
        console.log(newData) */
        setDataSource(newData);
    };
    const components = {
        body: {
            row: EditableRow,
            cell: EditableCell,
        },
    };
    const columns = defaultColumns.map((col) => {
        if (!col.editable) {
            return col;
        }
        return {
            ...col,
            onCell: (record) => ({
                record,
                editable: col.editable,
                dataIndex: col.dataIndex,
                title: col.title,
                handleSave,
            }),
        };
    });

    const onChange = (key) => {
        console.log(key);
    };

    const location = useLocation();
    const currentId = location.pathname.split("/")[2];
    const [price, setPrice] = useState(0);
    const [prePrice, setPrePrice] = useState(0);
    const [tonValue, setTonValue] = useState(1);

    const getBestRecipe = async () => {
        const formData = new FormData();
        formData.append("action", "read");
        formData.append("recipe_id", currentId);
        const result = await reqBestRecipeCRUD(formData);
        console.log(result);
        setDataSource(result.data.data);
        setPrice(result.data.price);
        setPrePrice(result.data.price_pre);
        setNutritionSource(result.data.nutrition);
    };

    const getRecipeNutrition = async () => {
        const formData = new FormData();
        formData.append("action", "read");
        formData.append("recipe_id", currentId);
        const result = await reqAttributeCRUD(formData);
        console.log(result);
        const modifiedData = result.data.data.map((item) => ({
            ...item,
            max_value: item.max_value,
            min_value: item.min_value,
        }));

        setNutritionLimit(modifiedData);
    };

    const getRatios = async () => {
        const formData = new FormData();
        formData.append("action", "read");
        formData.append("recipe_id", currentId);
        const result = await reqRecipeRatioCRUD(formData);
        console.log(result);
        setRatioData(result.data.data);
    };

    const onChangeTon = async (value) => {
        const formData = new FormData();
        formData.append("action", "create");
        formData.append("tonne", value);
        formData.append("recipe_id", currentId); // Add this line to include the recipe_id
        const result = await reqSetTonne(formData);
        console.log(result);
        setTonValue(value);
    };
    const handleCalculate = async () => {
        const formData = new FormData();
        formData.append("recipe_id", currentId);
        const result = await reqCalculate(formData);
        console.log(result);
        if (result.data.status == "success") {
            getBestRecipe();
        }
    };

    useEffect(() => {
        getBestRecipe();
        getRatios();
        getRecipeNutrition();
    }, []);

    const items = [
        {
            key: "1",
            label: <span className='tableName'>Optimal diet</span>,
            children: (
                <Table
                    components={components}
                    rowClassName={() => "editable-row"}
                    bordered
                    dataSource={dataSource}
                    columns={columns}
                    rowKey={(record) => record.id}
                />
            ),
        },
        {
            key: "2",
            label: <span className='tableName'>Nutrient</span>,
            children: (
                <Table
                    components={components}
                    rowClassName={() => "editable-row"}
                    bordered
                    dataSource={nutritionSource}
                    columns={nutritionColumns}
                    rowKey={(record) => record.id}
                />
            ),
        },
        {
            key: "3",
            label: <span className='tableName'>Nutrient Ratios</span>,
            children: (
                <Table
                    components={components}
                    rowClassName={() => "editable-row"}
                    bordered
                    dataSource={ratioData}
                    columns={ratioColumns}
                    rowKey={(record) => record.id}
                />
            ),
        },
    ];

    return (
        <div className='nutrition_table' /* style={{width:"100%",height:"100%"}} */>
            {/* <span className='tableName'>Optimal Feeds</span> */}
            <Button onClick={handleAdd} type='primary' style={{ float: "right", marginBottom: 16, display: "none" }}>
                Add a row
            </Button>
            <Tabs defaultActiveKey='1' items={items} onChange={onChange} />
            {/* <Table
                components={components}
                rowClassName={() => "editable-row"}
                bordered
                dataSource={dataSource}
                columns={columns}
            /> */}
            <div className='price'>
                <span>Price: {price} $ / tonne</span>
                <span style={{ marginLeft: "30px", marginRight: "30px", color: "grey" }}>
                    Previous Price:{prePrice} $ / tonne
                </span>
                <span style={price - prePrice > 0 ? { color: "red" } : { color: "green" }}>
                    Gap Price:{price - prePrice} $ / tonne
                </span>
                <br></br>
                <span>Total Price:{tonValue * price} $ / </span>
                <InputNumber
                    style={{ width: "60px", marginLeft: "2px", marginRight: "5px" }}
                    min={1}
                    defaultValue={1}
                    onChange={onChangeTon}
                />
                <span>tonne</span>
            </div>
            <Button onClick={handleCalculate} className='calculateBtn' type='primary'>
                Calculate
            </Button>
        </div>
    );
}

export default RecipeTable;
