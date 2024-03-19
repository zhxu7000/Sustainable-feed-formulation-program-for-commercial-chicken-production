import React, { useContext, useEffect, useRef, useState } from "react";
import { Button, Form, Input, Popconfirm, Table, message } from "antd";
import { EditableCell, EditableRow, EditableContext } from "./editable_table";
import { DeleteOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { reqMaterialAttributeCRUD, reqRecipeMaterialCRUD } from "../../../api";

function IngredientTable() {
    const [dataSource, setDataSource] = useState([
        {
            id: "0",
            material_name: "ingredient 0",
            max_weight_kg_per_ton: 100,
            min_weight_kg_per_ton: 3,
            max_percentage: 20,
            min_percentage: 10,
            price_per_kg: 100,
        },
        {
            id: "1",
            material_name: "ingredient 0",
            max_weight_kg_per_ton: 100,
            min_weight_kg_per_ton: 3,
            max_percentage: 20,
            min_percentage: 10,
            price_per_kg: 100,
        },
    ]);
    const [count, setCount] = useState(2);

    const defaultColumns = [
        {
            title: "Ingredient",
            dataIndex: "material_name",
            width: "20%",
            editable: true,
            render: (_, record) => {
                return (
                    <Link
                        onClick={() => {
                            handleClickIngredients(record);
                        }}>
                        {record.material_name}
                    </Link>
                );
            },
        },
        {
            title: "Max Weight(kg per ton)",
            dataIndex: "max_weight_kg_per_ton",
            width: "16%",
            editable: true,
        },
        {
            title: "Min Weight(kg per ton)",
            dataIndex: "min_weight_kg_per_ton",
            width: "16%",
            editable: true,
        },
        {
            title: "Max percentage(%)",
            dataIndex: "max_percentage",
            width: "16%",
            editable: true,
        },
        {
            title: "Min percentage(%)",
            dataIndex: "min_percentage",
            width: "16%",
            editable: true,
        },
        {
            title: "Price($ per kg)",
            dataIndex: "price_per_kg",
            width: "11%",
            editable: true,
        },
        {
            title: "",
            dataIndex: "operation",
            width: "5%",
            render: (_, record) =>
                dataSource.length >= 1 ? (
                    <Popconfirm title='Sure to delete?' onConfirm={() => handleDelete(record.id)}>
                        <a>
                            <DeleteOutlined style={{ color: "#979797" }} />
                        </a>
                    </Popconfirm>
                ) : null,
        },
    ];
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

    const location = useLocation();
    const navigate = useNavigate();
    const currentId = location.pathname.split("/")[2];
    const ingredientId = location.pathname.split("/")[4];

    const handleDelete = async (id) => {
        id = id + "";
        console.log("into delete", id);
        if (id.includes("new")) {
            const newData = dataSource.filter((item) => item.id !== id);
            setDataSource(newData);
            return;
        }
        const result = await handleDeleteIngredients(id);
        if (result.data.status == "success") {
            const newData = dataSource.filter((item) => item.id != id);
            setDataSource(newData);
        } else {
            message.warning("Data Delete Failed");
        }
    };

    const handleAdd = () => {
        const newData = {
            id: "new" + count,
            material_name: "new ingredients",
            max_weight_kg_per_ton: 1000,
            min_weight_kg_per_ton: 0,
            max_percentage: 100,
            min_percentage: 0,
            price_per_kg: 0,
        };
        setDataSource([...dataSource, newData]);
        setCount(count + 1);
    };
    const handleSave = async (row) => {
        const newData = [...dataSource];
        const index = newData.findIndex((item) => row.id === item.id);
        const item = newData[index];
        console.log("row", row);
        console.log("item", item);
        var result = null;
        const rowId = row.id + "";
        const input = checkInputValue(row);
        if (input == false) {
            return;
        }
        if (
            row.material_name != item.material_name ||
            row.max_weight_kg_per_ton != item.max_weight_kg_per_ton ||
            row.min_weight_kg_per_ton != item.min_weight_kg_per_ton ||
            row.max_percentage != item.max_percentage ||
            row.min_percentage != item.min_percentage ||
            row.price_per_kg != item.price
        ) {
            console.log("changed");
            if (rowId.includes("new")) {
                result = await handleCreateIngredients(row);
                console.log(result.data.status);
                if (result.data.status == "success") {
                    console.log("id", result.data.data.id);
                    row.id = result.data.data.id;
                }
            } else {
                console.log("should update");
                result = await handleUpdateIngredients(row);
            }
            if (result.data.status == "success") {
                newData.splice(index, 1, {
                    ...row,
                });
                console.log(newData);
                setDataSource(newData);
            } else {
                message.warning("Data Save Failed");
            }
        }
    };

    const checkInputValue = (row) => {
        const max_percentage = parseFloat(row.max_percentage);
        const min_percentage = parseFloat(row.min_percentage);
        const max_weight_kg_per_ton = parseFloat(row.max_weight_kg_per_ton);
        const min_weight_kg_per_ton = parseFloat(row.min_weight_kg_per_ton);

        if (max_percentage > 100 || max_percentage < min_percentage) {
            message.warning("Input Error. Max_percentage must smaller than 100, bigger than Min_percentage");
            return false;
        }
        if (min_percentage < 0 || min_percentage > max_percentage) {
            message.warning("Input Error. Min_percentage must bigger than 0, smaller than Max_percentage");
            return false;
        }
        if (max_weight_kg_per_ton > 1000 || max_weight_kg_per_ton < min_weight_kg_per_ton) {
            console.log(max_weight_kg_per_ton, min_weight_kg_per_ton);
            message.warning(
                "Input Error. Max_weight_kg_per_ton must smaller than 1000, bigger than Min_weight_kg_per_ton"
            );
            return false;
        }
        if (min_weight_kg_per_ton < 0 || min_weight_kg_per_ton > max_weight_kg_per_ton) {
            message.warning(
                "Input Error. Min_weight_kg_per_ton must bigger than 0, smaller than Max_weight_kg_per_ton"
            );
            return false;
        }
    };

    const handleGetIngredients = async () => {
        const formData = new FormData();
        formData.append("action", "read");
        formData.append("recipe_id", currentId);
        const result = await reqRecipeMaterialCRUD(formData);
        console.log(result);
        setDataSource(result.data.data);
    };

    const handleCreateIngredients = async (row) => {
        const formData = new FormData();
        formData.append("action", "create");
        formData.append("material_name", row.material_name);
        formData.append("max_weight_kg_per_ton", row.max_weight_kg_per_ton);
        formData.append("min_weight_kg_per_ton", row.min_weight_kg_per_ton);
        formData.append("max_percentage", row.max_percentage);
        formData.append("min_percentage", row.min_percentage);
        formData.append("price", row.price_per_kg);
        formData.append("recipe_id", currentId);
        const result = await reqRecipeMaterialCRUD(formData);
        console.log(result);
        return result;
    };

    const handleUpdateIngredients = async (row) => {
        const formData = new FormData();
        formData.append("action", "update");
        formData.append("material_name", row.material_name);
        formData.append("max_weight_kg_per_ton", row.max_weight_kg_per_ton);
        formData.append("min_weight_kg_per_ton", row.min_weight_kg_per_ton);
        formData.append("max_percentage", row.max_percentage);
        formData.append("min_percentage", row.min_percentage);
        formData.append("price", row.price_per_kg);
        formData.append("material_id", row.id);
        const result = await reqRecipeMaterialCRUD(formData);
        console.log(result);
        return result;
    };
    const handleDeleteIngredients = async (id) => {
        const formData = new FormData();
        formData.append("action", "delete");
        formData.append("material_id", id);
        const result = await reqRecipeMaterialCRUD(formData);
        console.log(result);
        return result;
    };
    const handleClickIngredients = (row) => {
        console.log("navi");
        navigate(`/product/${currentId}/ingredient/${row.id}`, { replace: true });
    };

    useEffect(() => {
        handleGetIngredients();
    }, []);

    return (
        <div className='ingredient_table' /* style={{width:"100%",height:"100%"}} */>
            <span className='tableName'>Available ingredients</span>
            <Button
                onClick={handleAdd}
                type='primary'
                style={{
                    float: "right",
                    marginBottom: 16,
                }}>
                New Ingredients
            </Button>
            <Table
                components={components}
                rowClassName={() => "editable-row"}
                bordered
                dataSource={dataSource}
                columns={columns}
                rowKey={(record) => record.id}
                pagination={{ pageSize: 7 }}
            />
        </div>
    );
}

export default IngredientTable;
