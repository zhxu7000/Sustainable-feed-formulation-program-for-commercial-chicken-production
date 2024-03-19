import React, { useState, useEffect, useRef } from "react";

import {
    DesktopOutlined,
    FileOutlined,
    PieChartOutlined,
    TeamOutlined,
    UserOutlined,
    ExclamationCircleOutlined,
} from "@ant-design/icons";
import { Breadcrumb, Card, Layout, Menu, theme, Input, Button, Modal, Space, Form } from "antd";

import { HomeWarpper } from "./style";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import logo from "../../assets/chicken-icon.png";
import { reqRecipeCRUD, reqRecipeMaterialCRUD } from "../../api";
import dayjs from "dayjs";

const { Header, Content, Footer, Sider } = Layout;

function getItem(label, key, id) {
    return {
        key,
        id,
        icon: <PieChartOutlined />,
        label,
        children: [
            { key: `${key}.recipe`, id, label: "Recipe", icon: <FileOutlined /> },
            { key: `${key}.ingredient`, id, label: "Ingredient", icon: <FileOutlined /> },
        ],
    };
}
const items = [getItem("Product 1", "1", <PieChartOutlined />), getItem("Product 2", "2", <PieChartOutlined />)];

const menuItems = (dataList) => {
    //console.log(dataList[2].name);
    const itemList = [];
    var i = 0;
    dataList.forEach((item) => {
        //console.log(item, i);
        itemList.push(getItem(item.name, i, item.id));
        i++;
    });
    //console.log("menuItem", itemList);
    return itemList;
};

const Home = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const [modal, contextHolder] = Modal.useModal();

    const username = localStorage.getItem("username");

    const [menuItem, setMenuItem] = useState([]);
    const [collapsed, setCollapsed] = useState(false);
    const [selectedKey, setSelectedKey] = useState("0.recipe");
    const [recipeName, setRecipeName] = useState();

    const currentId = location.pathname.split("/")[2];
    const inputRef = useRef(null);

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
        await handleCreateRecipe(values);
        getRecipe();
        setIsModalOpen(false);
    };
    const onFinishFailed = (errorInfo) => {
        console.log("Failed:", errorInfo);
    };
    //Modal and its Form

    const getRecipe = async () => {
        const formData = new FormData();
        formData.append("action", "get");
        //formData.append("recipe_name", "Liu");
        const result = await reqRecipeCRUD(formData);
        console.log(result);
        setMenuItem(menuItems(result.data.data));
    };
    const reqFirstIngredients = async (id) => {
        const formData = new FormData();
        formData.append("action", "get_first");
        formData.append("recipe_id", id);
        const result = await reqRecipeMaterialCRUD(formData);
        console.log(result);
        return result;
    };

    const checkNavRoute = () => {
        var key = -1;
        menuItem.forEach((item) => {
            //console.log(item);
            if (item.id == currentId) {
                key = item.key;
            }
        });
        //console.log(key);
        const selected = `${key}.${location.pathname.split("/")[3]}`;
        setSelectedKey(selected);
        const item = menuItem.find((item) => item.id == currentId);
        console.log(item);
        setRecipeName(item.label);
    };
    useEffect(() => {
        console.log("comDIdmount");
        getRecipe();
    }, []);

    useEffect(() => {
        //console.log("变化", menuItem.length);
        if (menuItem.length > 0) {
            checkNavRoute();
            //console.log(menuItem);
        }
    }, [menuItem]);

    const onClick = async (e) => {
        //console.log(e);
        const id = menuItem[e.keyPath[1]].id;
        //console.log(menuItem[e.keyPath[1]], id);
        if (e.key.includes("recipe")) {
            navigate(`/product/${id}/recipe`, { replace: true });
            setSelectedKey(e.key);
            console.log(menuItem[e.keyPath[1]].label);
            setRecipeName(menuItem[e.keyPath[1]].label);
        }
        if (e.key.includes("ingredient")) {
            const result = await reqFirstIngredients(id);
            console.log(result);
            var ingredients = 0;
            if (result.data.status == "success") {
                ingredients = result.data.data.id;
            }
            navigate(`/product/${id}/ingredient/${ingredients}`, { replace: true });
            setSelectedKey(e.key);
            setRecipeName(menuItem[e.keyPath[1]].label);
        }
    };

    const handleClickUser = () => {
        navigate(`/product/${currentId}/user`, { replace: true });
    };

    const handleRecipeName = async (e) => {
        console.log(e.target.value);
        const formData = new FormData();
        formData.append("action", "update");
        formData.append("recipe_name", e.target.value);
        formData.append("recipe_id", currentId);
        const result = await reqRecipeCRUD(formData);
        //console.log(result);
        if (result.data.status == "success") {
            getRecipe();
        }
    };
    const handleClickDeleteRecipe = () => {
        modal.confirm({
            title: "Confirm",
            icon: <ExclamationCircleOutlined />,
            content: "Are you sure to delete this recipe ?",
            okText: "Yes",
            cancelText: "No",
            onOk: () => {
                handleDeleteRecipe();
            },
        });
    };
    const handleCreateRecipe = async (value) => {
        const formData = new FormData();
        formData.append("action", "create");
        formData.append("recipe_name", value.recipeName);
        const result = await reqRecipeCRUD(formData);
        console.log(result);
        if (result.data.status == "success") {
            navigate(`/product/${result.data.data.id}/recipe`, { replace: true });
        }
    };
    const handleDeleteRecipe = async () => {
        const formData = new FormData();
        formData.append("action", "delete");
        formData.append("recipe_id", currentId);
        const result = await reqRecipeCRUD(formData);
        console.log(result);
        if (result.data.status == "success") {
            await getRecipe();
            const id = menuItem[0].id;
            navigate(`/product/${id}/recipe`, { replace: true });
        }
    };

    const handleImportExcel = async () => {
        // Use a file input to trigger file selection
        const fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.accept = ".xls,.xlsx";

        // Function to get a cookie by name
        const getCookie = (name) => {
            let cookieValue = null;
            if (document.cookie && document.cookie !== "") {
                const cookies = document.cookie.split(";");
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === name + "=") {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };

        // Fetch the CSRF token from the cookie
        const csrftoken = getCookie("csrftoken");

        fileInput.onchange = async (event) => {
            const file = event.target.files[0];
            const formData = new FormData();
            formData.append("excel_file", file);

            const response = await fetch(`/api/import_excel/?recipe_id=${currentId}`, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": csrftoken,
                },
                credentials: "include", // ensure cookies like CSRF token are sent with the request
            });
            const result = await response.json();
            console.log(result);

            if (result.status === "success") {
                // Get the current product ID from the URL
                let currentURL = window.location.pathname; // e.g., "/product/50/recipe"
                let parts = currentURL.split("/");
                let currentID = parseInt(parts[2], 10); // 50

                // Increase the product ID by 1
                let newID = currentID;
                let newURL = `/product/${newID}/recipe`;

                // Navigate to the new URL
                window.location.href = newURL;
            } else {
                console.error("Error importing Excel:", result.message);
            }
        };
        fileInput.click();
    };

    const handleExportExcel = async () => {
        try {
            const response = await fetch(`/api/export_excel/?recipe_id=${currentId}`, { method: "GET" });

            if (response.ok) {
                const blob = await response.blob();

                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = "desired_filename_here.xlsx"; // Modify filename if needed
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                console.error("Server responded with status:", response.status);
            }
        } catch (error) {
            console.error("Error during fetching or downloading:", error);
        }
    };

    const handleDownloadPDF = async () => {
        try {
            const response = await fetch(`/api/download_pdf/?recipe_id=${currentId}`, { method: "GET" });

            if (response.status === 200) {
                const blob = await response.blob(); // 正确地转换响应为blob
                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = "recipe.pdf";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                console.error("Error downloading PDF:", response.statusText);
            }
        } catch (error) {
            console.error("An error occurred:", error);
        }
    };

    return (
        <HomeWarpper>
            <Layout style={{ height: "100%" }}>
                <Header className='header'>
                    <div className='web'>
                        <img src={logo} alt='logo' className='logo'></img>
                        <span className='webName'>Animal Feed</span>
                    </div>

                    <div className='Nav'>
                        {localStorage.getItem("admin") == localStorage.getItem("csrf") ? (
                            <div className='borderButton'>
                                <a onClick={handleClickUser} className='button'>
                                    User Manage
                                </a>
                            </div>
                        ) : (
                            ""
                        )}
                        <div className='borderButton'>
                            <a onClick={showModal} className='button'>
                                New Feed
                            </a>
                        </div>
                        <div className='borderButton'>
                            <a onClick={handleDownloadPDF} className='button'>
                                Download PDF
                            </a>
                        </div>
                        <div className='borderButton'>
                            <a onClick={handleImportExcel} className='button'>
                                Import Excel
                            </a>
                        </div>
                        <div className='borderButton'>
                            <a onClick={handleExportExcel} className='button'>
                                Export Excel
                            </a>
                        </div>
                        <p className='userName'>{username}</p>
                    </div>
                </Header>
                <Layout className='layout'>
                    <Sider
                        collapsible
                        collapsed={collapsed}
                        /* onCollapse={(value) => {
                            this.setState({ collapsed: value });
                        }} */
                        onCollapse={(value) => setCollapsed(value)}>
                        <div className='demo-logo-vertical' />
                        <Menu
                            key={currentId}
                            className='menu'
                            onClick={onClick}
                            //defaultOpenKeys={selectedKey}
                            defaultSelectedKeys={["0.recipe"]}
                            selectedKeys={selectedKey}
                            mode='inline'
                            items={menuItem}
                        />
                    </Sider>
                    <Card className='recipe'>
                        {location.pathname.split("/")[3] == "user" ? (
                            <div className='recipeTitle'>
                                <span className='recipeName'>User Management</span>
                                {contextHolder}
                            </div>
                        ) : (
                            <div className='recipeTitle'>
                                {currentId == 1 ? (
                                    <span className='recipeName'>{recipeName}</span>
                                ) : (
                                    <Input
                                        className='recipeName'
                                        key={recipeName}
                                        placeholder='Input Recipe Name'
                                        bordered={false}
                                        defaultValue={recipeName}
                                        onPressEnter={handleRecipeName}
                                    />
                                )}
                                {currentId == 1 ? (
                                    ""
                                ) : (
                                    <Button className='deleteButton' type='primary' onClick={handleClickDeleteRecipe}>
                                        Delete Feeds
                                    </Button>
                                )}
                                {contextHolder}
                            </div>
                        )}

                        <Outlet></Outlet>
                    </Card>
                    {/* <Content>
                                <Breadcrumb>
                                    <Breadcrumb.Item>User</Breadcrumb.Item>
                                    <Breadcrumb.Item>Bill</Breadcrumb.Item>
                                </Breadcrumb>
                                <div>
                                    Bill is a cat.
                                </div>
                            </Content> */}
                </Layout>
                {/* <Footer></Footer> */}
            </Layout>
            <Modal
                title='Create Recipe'
                okText='Create From Template'
                open={isModalOpen}
                onOk={handleOk}
                onCancel={handleCancel}>
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
                        label='Recipe name'
                        name='recipeName'
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
        </HomeWarpper>
    );
};

export default Home;
