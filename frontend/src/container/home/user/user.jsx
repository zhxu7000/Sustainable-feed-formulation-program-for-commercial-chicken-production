import { SearchOutlined } from "@ant-design/icons";
import React, { useEffect, useRef, useState } from "react";
import Highlighter from "react-highlight-words";
import { Button, Input, Space, Table, Popconfirm, Modal, Form } from "antd";
import { reqRecipeCRUD, reqRegister, reqUser } from "../../../api";
import dayjs from "dayjs";

const data = [
    {
        id: "1",
        username: "John Brown",
        last_login: 32,
        email: "New York No. 1 Lake Park",
    },
    {
        id: "2",
        username: "Joe Black",
        last_login: 42,
        email: "London No. 1 Lake Park",
    },
    {
        id: "3",
        username: "Jim Green",
        last_login: 32,
        email: "Sydney No. 1 Lake Park",
    },
    {
        id: "4",
        username: "Jim Red",
        last_login: 32,
        email: "London No. 2 Lake Park",
    },
];

const User = () => {
    const [searchText, setSearchText] = useState("");
    const [searchedColumn, setSearchedColumn] = useState("");
    const [selectionType, setSelectionType] = useState("checkbox");
    const [userData, setUserData] = useState([
        {
            id: "1",
            username: "John Brown",
            last_login: 32,
            email: "New York No. 1 Lake Park",
        },
        {
            id: "2",
            username: "Joe Black",
            last_login: 42,
            email: "London No. 1 Lake Park",
        },
    ]);
    const searchInput = useRef(null);
    const handleSearch = (selectedKeys, confirm, dataIndex) => {
        confirm();
        setSearchText(selectedKeys[0]);
        setSearchedColumn(dataIndex);
    };
    const handleReset = (clearFilters) => {
        clearFilters();
        setSearchText("");
    };
    const getColumnSearchProps = (dataIndex) => ({
        filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters, close }) => (
            <div
                style={{
                    padding: 8,
                }}
                onKeyDown={(e) => e.stopPropagation()}>
                <Input
                    ref={searchInput}
                    placeholder={`Search ${dataIndex}`}
                    value={selectedKeys[0]}
                    onChange={(e) => setSelectedKeys(e.target.value ? [e.target.value] : [])}
                    onPressEnter={() => handleSearch(selectedKeys, confirm, dataIndex)}
                    style={{
                        marginBottom: 8,
                        display: "block",
                    }}
                />
                <Space>
                    <Button
                        type='primary'
                        onClick={() => handleSearch(selectedKeys, confirm, dataIndex)}
                        icon={<SearchOutlined />}
                        size='small'
                        style={{
                            width: 90,
                        }}>
                        Search
                    </Button>
                    <Button
                        onClick={() => clearFilters && handleReset(clearFilters)}
                        size='small'
                        style={{
                            width: 90,
                        }}>
                        Reset
                    </Button>
                    <Button
                        type='link'
                        size='small'
                        onClick={() => {
                            confirm({
                                closeDropdown: false,
                            });
                            setSearchText(selectedKeys[0]);
                            setSearchedColumn(dataIndex);
                        }}>
                        Filter
                    </Button>
                    <Button
                        type='link'
                        size='small'
                        onClick={() => {
                            close();
                        }}>
                        close
                    </Button>
                </Space>
            </div>
        ),
        filterIcon: (filtered) => (
            <SearchOutlined
                style={{
                    color: filtered ? "#1677ff" : undefined,
                }}
            />
        ),
        onFilter: (value, record) => record[dataIndex].toString().toLowerCase().includes(value.toLowerCase()),
        onFilterDropdownOpenChange: (visible) => {
            if (visible) {
                setTimeout(() => searchInput.current?.select(), 100);
            }
        },
        render: (text) =>
            searchedColumn === dataIndex ? (
                <Highlighter
                    highlightStyle={{
                        backgroundColor: "#ffc069",
                        padding: 0,
                    }}
                    searchWords={[searchText]}
                    autoEscape
                    textToHighlight={text ? text.toString() : ""}
                />
            ) : (
                text
            ),
    });

    const [selectedKeys, setSelectedKeys] = useState([]);

    const rowSelection = {
        onChange: (selectedRowKeys, selectedRows) => {
            console.log(`selectedRowKeys: ${selectedRowKeys}`, "selectedRows: ", selectedRows);
            setSelectedKeys(selectedRowKeys);
        },
        getCheckboxProps: (record) => ({
            disabled: record.name === "Disabled User",
            // Column configuration not to be checked
            name: record.name,
        }),
    };

    const columns = [
        {
            title: "Name",
            dataIndex: "username",
            key: "username",
            width: "25%",
            ...getColumnSearchProps("username"),
        },
        {
            title: "Email",
            dataIndex: "email",
            key: "email",
            width: "50%",
            ...getColumnSearchProps("email"),
        },
        {
            title: "Last Login Time",
            dataIndex: "last_login",
            key: "last_login",
            ...getColumnSearchProps("last_login"),
            render: (text, record, index) =>
                text != null ? dayjs(text).format("YYYY-MM-DD HH:mm:ss") : "No login ever",
            /* sorter: (a, b) => a.address.length - b.address.length,
            sortDirections: ["descend", "ascend"], */
        },
    ];

    const getUser = async () => {
        const formData = new FormData();
        formData.append("action", "read");
        const result = await reqUser(formData);
        console.log(result);
        setUserData(result.data.data);
    };

    const deleteUser = async () => {
        const formData = new FormData();
        const user_list = selectedKeys;
        formData.append("action", "delete");
        formData.append("user_list", user_list);
        const result = await reqUser(formData);
        console.log(result);
        setSelectedKeys([]);
        getUser();
    };

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
        const formData = new FormData();
        formData.append("username", values.username);
        formData.append("password1", values.password);
        formData.append("password2", values.password);
        formData.append("email", values.email);
        let result = await reqRegister(formData);
        console.log(result.data);
        if ((result.data.status = "success")) {
            let createResult = await handleCreateRecipe(result.data.id);
        }
        setIsModalOpen(false);
        getUser();
    };

    const handleCreateRecipe = async (id) => {
        const formData = new FormData();
        formData.append("action", "create");
        formData.append("recipe_name", "default recipe");
        formData.append("user_id", id);
        console.log(id);
        const result = await reqRecipeCRUD(formData);
        console.log(result);
        return result;
    };

    const onFinishFailed = (errorInfo) => {
        console.log("Failed:", errorInfo);
    };
    //Modal and its Form

    useEffect(() => {
        console.log("comDIdmount");
        getUser();
        deleteUser();
    }, []);

    return (
        <div className='user_table'>
            <div className='user_btns'>
                <Button type='primary' onClick={showModal} className='user_delete_btn'>
                    Add User
                </Button>
                {selectedKeys.length == 0 ? (
                    ""
                ) : (
                    /* <Button
                        style={{ marginLeft: "30px", backgroundColor: "red", color: "white" }}
                        onClick={deleteUser}
                        className='user_delete_btn'>
                        Delete User
                    </Button> */
                    <Popconfirm
                        title='Delete the task'
                        description='Are you sure to delete thhose User?'
                        onConfirm={deleteUser}
                        /* onCancel={cancel} */
                        okText='Yes'
                        cancelText='No'>
                        <Button className='user_delete_btn' style={{ marginLeft: "30px" }} danger>
                            Delete
                        </Button>
                    </Popconfirm>
                )}
            </div>

            <Table
                rowSelection={{
                    type: selectionType,
                    ...rowSelection,
                }}
                columns={columns}
                dataSource={userData}
                rowKey={(record) => record.id}
            />

            <Modal title='Create New User' okText='Create' open={isModalOpen} onOk={handleOk} onCancel={handleCancel}>
                <Form
                    name='basic'
                    form={form}
                    initialValues={{
                        remember: true,
                    }}
                    onFinish={onFinish}
                    onFinishFailed={onFinishFailed}
                    autoComplete='off'>
                    <Form.Item
                        label='User Name'
                        name='username'
                        rules={[
                            {
                                required: true,
                                message: "Please input your recipe name!",
                            },
                        ]}>
                        <Input />
                    </Form.Item>
                    <Form.Item
                        label='Email'
                        name='email'
                        rules={[
                            {
                                required: true,
                                message: "Please input your recipe name!",
                            },
                        ]}>
                        <Input />
                    </Form.Item>
                    <Form.Item
                        label='Password'
                        name='password'
                        rules={[
                            {
                                required: true,
                                message: "Please input your recipe name!",
                            },
                        ]}>
                        <Input />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default User;
