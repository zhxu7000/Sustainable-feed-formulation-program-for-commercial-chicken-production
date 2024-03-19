import React, { useContext, useEffect, useRef, useState } from "react";
import { Button, Form, Input, Popconfirm, Table, ConfigProvider, message } from "antd";
import { EditableCell, EditableRow, EditableContext } from "./editable_table";
import { DeleteOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { useLocation } from "react-router-dom";
import { reqMaterialAttributeCRUD } from "../../../api";

function IngredientNutritionTable() {
    const [dataSource, setDataSource] = useState([
        {
            id: "0",
            attribute_name: "nutrition 0",
            value: "50",
        },
        {
            id: "1",
            attribute_name: "nutrition 1",
            value: "50",
        },
    ]);
    const [count, setCount] = useState(2);

    const defaultColumns = [
        {
            title: "Nutrient",
            dataIndex: "attribute_name",
            width: "40%",
            editable: true,
            //render: (_, record) => <a href='/'>{record.ingredient}</a>,
        },
        {
            title: "Value (%)",
            dataIndex: "value",
            width: "40%",
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
    const currentId = location.pathname.split("/")[2];
    const ingredientId = location.pathname.split("/")[4];
    const [materialName, setMaterialName] = useState("Material");

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
            attribute_name: "new nutrient",
            value: 0,
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
        const input = checkInputValue(row);
        if (input == false) {
            return;
        }
        const rowId = row.id + "";
        if (row.attribute_name != item.attribute_name || row.value != item.value) {
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
        const value = parseFloat(row.value);

        if (value > 100 || value < 0) {
            message.warning("Input Error. Value must smaller than 100, bigger than 0");
            return false;
        }
    };

    const getIngredientNutrition = async () => {
        const formData = new FormData();
        formData.append("action", "read");
        formData.append("material_id", ingredientId);
        const result = await reqMaterialAttributeCRUD(formData);
        console.log(result);
        setDataSource(result.data.data);
        setMaterialName(result.data.material_name);
    };

    const handleCreateIngredients = async (row) => {
        const formData = new FormData();
        formData.append("action", "create");
        formData.append("attribute_name", row.attribute_name);
        formData.append("value", row.value);
        formData.append("material_id", ingredientId);
        formData.append("recipe_id", currentId);
        const result = await reqMaterialAttributeCRUD(formData);
        console.log(result);
        return result;
    };

    const handleUpdateIngredients = async (row) => {
        const formData = new FormData();
        formData.append("action", "update");
        formData.append("attribute_name", row.attribute_name);
        formData.append("value", row.value);
        formData.append("attribute_id", row.id);
        const result = await reqMaterialAttributeCRUD(formData);
        console.log(result);
        return result;
    };
    const handleDeleteIngredients = async (id) => {
        const formData = new FormData();
        formData.append("action", "delete");
        formData.append("attribute_id", id);
        const result = await reqMaterialAttributeCRUD(formData);
        console.log(result);
        return result;
    };

    useEffect(() => {
        getIngredientNutrition();
    }, []);
    return (
        <div className='ingredient_nutrition_table' /* style={{width:"100%",height:"100%"}} */>
            <span className='tableName'>
                Nutrient in <span style={{ color: "red" }}>{materialName}</span>
            </span>
            <Button
                onClick={handleAdd}
                type='primary'
                style={{
                    float: "right",
                    marginBottom: 16,
                }}>
                Add a row
            </Button>
            <Table
                components={components}
                rowClassName={() => "editable-row"}
                bordered
                dataSource={dataSource}
                columns={columns}
                rowKey={(record) => record.id}
                pagination={{ pageSize: 8 }}
            />
        </div>
    );
}

export default IngredientNutritionTable;
