import React, { useContext, useEffect, useRef, useState } from "react";
import { Button, Form, Input, Popconfirm, Table, message, Tabs, Modal, Select } from "antd";
import { DeleteOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { useLocation } from "react-router-dom";
import { reqAttributeCRUD, reqBestRecipeCRUD, reqRecipeRatioCRUD } from "../../../api";
import { EditableContext, EditableRow, EditableCell } from "./editable_table";

function NutritionTable() {
    const [dataSource, setDataSource] = useState([
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

    const [count, setCount] = useState(2);
    const [defaultColumns, setDefaultColumns] = useState([
        {
            title: "Nutrition",
            dataIndex: "attribute_name",
            width: "35%",
            editable: true,
        },
        {
            title: "Max /kg",
            dataIndex: "max_value",
            width: "20%",
            editable: true,
        },
        {
            title: "Min /kg",
            dataIndex: "min_value",
            width: "20%",
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
    ]);

    const ratioColumns = [
        {
            title: "Ratio",
            dataIndex: "attribute_name",
            width: "55%",
            render: (_, record) => {
                return (
                    <span>
                        {record.nutrition_1_name} / {record.nutrition_2_name}
                    </span>
                );
            },
        },
        {
            title: "Max",
            dataIndex: "max_value",
            width: "20%",
            render: (_, record) => {
                let val1 = 0;
                let val2 = 0;
                dataSource.forEach((item) => {
                    if (item.id == record.nutrition_1_id) {
                        val1 = item.max_value;
                    }
                    if (item.id == record.nutrition_2_id) {
                        val2 = item.max_value;
                    }
                });
                return <span>{(val1 / val2).toFixed(4)}</span>;
            },
        },
        {
            title: "Min",
            dataIndex: "min_value",
            width: "20%",
            render: (_, record) => {
                let val1 = 0;
                let val2 = 0;
                dataSource.forEach((item) => {
                    if (item.id == record.nutrition_1_id) {
                        val1 = item.min_value;
                    }
                    if (item.id == record.nutrition_2_id) {
                        val2 = item.min_value;
                    }
                });
                return <span>{(val1 / val2).toFixed(4)}</span>;
            },
        },
        {
            title: "",
            dataIndex: "operation",
            render: (_, record) =>
                dataSource.length >= 1 ? (
                    <Popconfirm title='Sure to delete?' onConfirm={() => handleDeleteRatio(record.id)}>
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
    let columns = defaultColumns.map((col) => {
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

    const handleDelete = async (id) => {
        id = id + "";
        console.log("into delete", id);
        if (id.includes("new")) {
            const newData = dataSource.filter((item) => item.id !== id);
            setDataSource(newData);
            return;
        }
        const result = await handleDeleteNutritionNeed(id);
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
            attribute_name: "new nutririon" + count,
            max_value: 1000,
            min_value: 0,
        };
        setDataSource([...dataSource, newData]);
        setCount(count + 1);
        console.log("handleadd", newData.id);
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
            row.attribute_name != item.attribute_name ||
            row.min_value != item.min_value ||
            row.max_value != item.max_value
        ) {
            console.log("changed");
            if (rowId.includes("new")) {
                result = await handleCreateNutritionNeed(row);
                console.log(result.data.status);
                if (result.data.status == "success") {
                    console.log("id", result.data.data.id);
                    row.id = result.data.data.id;
                }
            } else {
                result = await handleUpdateNutritionNeed(row);
            }
            if (result.data.status == "success") {
                newData.splice(index, 1, {
                    ...row,
                });
                console.log(newData);
                setDataSource(newData);
                message.success("Success");
            } else {
                message.warning("Data Save Failed");
            }
        }
    };

    const checkInputValue = (row) => {
        const max_value = parseFloat(row.max_value);
        const min_value = parseFloat(row.min_value);

        if (max_value > 1000 || max_value < min_value) {
            message.warning("Input Error. Max_value must smaller than 100, bigger than Min_value");
            return false;
        }
        if (min_value < 0 || min_value > max_value) {
            message.warning("Input Error. Min_value must bigger than 0, smaller than Max_value");
            return false;
        }
    };

    const location = useLocation();
    const currentId = location.pathname.split("/")[2];

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

        setDataSource(modifiedData);
    };

    const getBestRecipe = async () => {
        const formData = new FormData();
        formData.append("action", "read");
        formData.append("recipe_id", currentId);
        const result = await reqBestRecipeCRUD(formData);
        console.log(result);
        setNutritionSource(result.data.nutrition);
    };

    const handleCreateNutritionNeed = async (row) => {
        const maxAllowedValue = 999.99;
        const formData = new FormData();
        formData.append("action", "create");
        formData.append("attribute_name", row.attribute_name);
        formData.append("max_value", Math.min(row.max_value, maxAllowedValue));
        formData.append("min_value", Math.min(row.min_value, maxAllowedValue));
        formData.append("recipe_id", currentId);
        const result = await reqAttributeCRUD(formData);
        console.log(result.data);
        return result;
    };
    const handleUpdateNutritionNeed = async (row) => {
        const maxAllowedValue = 999.99;
        const formData = new FormData();
        console.log(row.id);
        formData.append("action", "update");
        formData.append("attribute_name", row.attribute_name);
        formData.append("max_value", Math.min(maxAllowedValue, row.max_value));
        formData.append("min_value", Math.min(maxAllowedValue, row.min_value));
        formData.append("limit_id", row.id);
        const result = await reqAttributeCRUD(formData);
        console.log(result.data);
        return result;
    };
    const handleDeleteNutritionNeed = async (id) => {
        const formData = new FormData();
        console.log(id);
        formData.append("action", "delete");
        formData.append("limit_id", id);
        const result = await reqAttributeCRUD(formData);
        console.log(result.data);
        return result;
    };

    const [ratioData, setRatioData] = useState([
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

    const getRatios = async () => {
        const formData = new FormData();
        formData.append("action", "read");
        formData.append("recipe_id", currentId);
        const result = await reqRecipeRatioCRUD(formData);
        console.log(result);
        setRatioData(result.data.data);
    };

    const handleCreateRatio = async (value) => {
        const formData = new FormData();
        formData.append("action", "create");
        formData.append("nutrition1_id", value.material_1);
        formData.append("nutrition2_id", value.material_2);
        formData.append("recipe_id", currentId);
        const result = await reqRecipeRatioCRUD(formData);
        console.log(result.data);
        return result;
    };
    const handleDeleteRatio = async (id) => {
        const formData = new FormData();
        console.log(id);
        formData.append("action", "delete");
        formData.append("ratio_id", id);
        const result = await reqRecipeRatioCRUD(formData);
        console.log(result.data);
        if (result.data.status == "success") {
            getRatios();
        }
        return result;
    };

    useEffect(() => {
        getRecipeNutrition();
        getRatios();
        getBestRecipe();
    }, []);

    const [currentTab, setCurrentTab] = useState(1);

    const onChangeTab = (key) => {
        console.log(key);
        setCurrentTab(key);
    };
    const handleAddRatio = () => {
        showModal();
    };
    const [showActual, setShowActual] = useState(false);
    const [fruits, setFruit] = useState(["Banana", "Orange", "Apple", "Mango"]);
    const handleShowActualValue = () => {
        setShowActual(!showActual);
    };
    useEffect(() => {
        console.log("showActual has been updated:", showActual);
        if (showActual == true) {
            var changeColumns = [...defaultColumns];
            changeColumns.splice(2, 0, {
                title: <span style={{ color: "var(--m)" }}>Actual</span>,
                dataIndex: "max_value",
                width: "20%",
                render: (_, record) => {
                    const nutrient = nutritionSource.find((item) => item.nutrition_name == record.attribute_name);
                    if (nutrient.value * 10 == record.min_value) {
                        return <span style={{ color: "red" }}>{nutrient.value * 10} (Min)</span>;
                    }
                    if (nutrient.value * 10 == record.max_value) {
                        return <span style={{ color: "red" }}>{nutrient.value * 10} (Max)</span>;
                    }
                    return nutrient.value * 10;
                },
            });
            setDefaultColumns(changeColumns);
            console.log(defaultColumns);
        } else {
            var changeColumns = [...defaultColumns];
            if (defaultColumns.length > 4) {
                changeColumns.splice(2, 1);
                setDefaultColumns(changeColumns);
            }
        }
    }, [showActual]);
    /* useEffect(() => {
        console.log(showActual);
    }, [defaultColumns]); */

    //Model and its Form
    const [isModalOpen, setIsModalOpen] = useState(false);

    const [form] = Form.useForm();
    const showModal = () => {
        setIsModalOpen(true);
    };

    const handleOk = () => {
        form.submit();
    };

    const handleCancel = () => {
        setIsModalOpen(false);
    };
    const onFinish = async (values) => {
        console.log("Success:", values);
        const result = await handleCreateRatio(values);
        if ((result.data.status = "success")) {
            setIsModalOpen(false);
            getRatios();
        }
    };
    const onFinishFailed = (errorInfo) => {
        console.log("Failed:", errorInfo);
    };
    //Modal and its Form

    const items = [
        {
            key: 1,
            label: <span className='tableName'>Nutrient needed</span>,
            children: (
                <Table
                    key={"table"}
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
            key: 2,
            label: <span className='tableName'>Nutrient ratios</span>,
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
            {/* <span className='tableName'>Nutritional needed</span> */}
            <div className='btn_with_tabs'>
                {currentTab == 1 ? (
                    <div>
                        <Button onClick={handleAdd} type='primary'>
                            Add a row
                        </Button>
                        <Button onClick={handleShowActualValue} type='primary' style={{ marginLeft: "10px" }}>
                            {showActual ? "Close Actual Value" : "Show Actual Value"}
                        </Button>
                    </div>
                ) : (
                    <Button onClick={handleAddRatio} type='primary'>
                        Add a ratio
                    </Button>
                )}
            </div>
            <Tabs defaultActiveKey='1' items={items} onChange={onChangeTab} />
            {/* <Table
                components={components}
                rowClassName={() => "editable-row"}
                bordered
                dataSource={dataSource}
                columns={columns}
                rowKey={(record) => record.id}
            /> */}
            <Modal title='Create Ratio' okText='Create' open={isModalOpen} onOk={handleOk} onCancel={handleCancel}>
                <Form
                    name='basic'
                    form={form}
                    initialValues={{
                        remember: true,
                    }}
                    labelCol={{ span: 7 }}
                    onFinish={onFinish}
                    onFinishFailed={onFinishFailed}
                    autoComplete='off'>
                    <Form.Item
                        label='Ratio Numerator'
                        name='material_1'
                        rules={[
                            {
                                required: true,
                                message: "Please input your recipe name!",
                            },
                        ]}>
                        <Select
                            fieldNames={{ label: "attribute_name", value: "id" }}
                            //style={{ width: 120 }}
                            options={dataSource}
                        />
                    </Form.Item>
                    <Form.Item
                        label='Ratio Denominator'
                        name='material_2'
                        rules={[
                            {
                                required: true,
                                message: "Please input your recipe name!",
                            },
                        ]}>
                        <Select
                            fieldNames={{ label: "attribute_name", value: "id" }}
                            //style={{ width: 120 }}
                            options={dataSource}
                        />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
}

export default NutritionTable;
