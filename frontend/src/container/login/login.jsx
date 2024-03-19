import React, { useEffect, useState } from "react";
import { Button, ConfigProvider, Space, Input, Label, Form, Checkbox, Divider, message } from "antd";
import { LoginWarpper } from "./style";
import logo from "../../assets/chicken-icon.png";
import { reqLogin, reqRecipeCRUD, reqRegister } from "../../api";
import { useNavigate } from "react-router-dom";

const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
};
const onClick = () => {
    const labelu = document.getElementById("username");
    const inputu = document.getElementById("username_input");
    const labelp = document.getElementById("password");
    const inputp = document.getElementById("password_input");
    const observeru = new MutationObserver(function () {
        //console.log("111");
        if (inputu.classList.contains("ant-input-status-error")) {
            //console.log("213");
            labelu.classList.add("error");
        } else {
            labelu.classList.remove("error");
        }
    });
    const observerp = new MutationObserver(function () {
        //console.log("222");
        if (inputp.parentNode.classList.contains("ant-input-affix-wrapper-status-error")) {
            //console.log(inputp.parentNode.classList.contains("ant-input-affix-wrapper-status-error"));
            labelp.classList.add("error");
        } else {
            labelp.classList.remove("error");
        }
    });
    observeru.observe(inputu, { attributes: true });
    observerp.observe(inputp.parentNode, { attributes: true });
};

const Login = () => {
    const [isChange, setIsChange] = useState(false);
    const navigate = useNavigate();

    const onLoginFinish = async (values) => {
        console.log("Success:", values);
        const formData = new FormData();
        formData.append("username", values.username);
        formData.append("password", values.password);
        let result = await reqLogin(formData);
        console.log(result.data);
        if (result.data.status == "success") {
            localStorage.setItem("username", values.username);
            localStorage.setItem("csrf", result.data.csrf_token);
            if (result.data.admin == true) {
                localStorage.setItem("admin", result.data.csrf_token);
            }
            if (values.email != null) {
                let createResult = await handleCreateRecipe();
            }
            let resultRecipe = await reqFirstRecipe();
            localStorage.setItem("first", resultRecipe.data.data.id);
            navigate(`/product/${resultRecipe.data.data.id}/recipe`);
        } else {
            message.warning("Sign In Failed");
        }
    };

    const onRegisterFinish = async (values) => {
        console.log("Success:", values);
        const formData = new FormData();
        formData.append("username", values.username);
        formData.append("password1", values.password);
        formData.append("password2", values.password);
        formData.append("email", values.email);
        let result = await reqRegister(formData);
        console.log(result.data);
        if (result.data.status == "success") {
            onLoginFinish(values);
        } else {
            message.warning("Sign In Failed");
        }
    };

    const handleCreateRecipe = async () => {
        const formData = new FormData();
        formData.append("action", "create");
        formData.append("recipe_name", "default recipe");
        const result = await reqRecipeCRUD(formData);
        console.log(result);
        return result;
    };

    const reqFirstRecipe = async () => {
        const formData = new FormData();
        formData.append("action", "get_first");
        const result = await reqRecipeCRUD(formData);
        console.log(result);
        return result;
    };

    const changeForm = () => {
        let login = document.querySelector(".front");
        let signup = document.querySelector(".back");
        if (isChange == false) {
            console.log("login", login);
            login.style.transform = "rotateY(-180deg)";
            signup.style.transform = "rotateY(0deg)";
            setIsChange(true);
        } else {
            login.style.transform = "rotateY(0deg)";
            signup.style.transform = "rotateY(180deg)";
            setIsChange(false);
        }
    };

    useEffect(() => {
        console.log("comDIdmount");
        onClick();
    }, []);

    return (
        <LoginWarpper>
            {/* <h2 className='title'>Animal Recipe</h2> */}
            <div className='web'>
                <img src={logo} alt='logo' className='logo'></img>
                <span className='webName'>Animal Feeds</span>
            </div>
            <div className='container'>
                <div className='front'>
                    <div className='content'>
                        <h3>Login</h3>
                        <Form
                            name='basic'
                            labelCol={{
                                span: 8,
                            }}
                            wrapperCol={{
                                span: 16,
                            }}
                            style={{
                                maxWidth: 600,
                            }}
                            initialValues={{
                                remember: true,
                            }}
                            onFinish={onLoginFinish}
                            onFinishFailed={onFinishFailed}
                            autoComplete='off'>
                            <Form.Item
                                name='username'
                                className='formItem'
                                rules={[
                                    {
                                        required: true,
                                        message: "Please input your password!",
                                    },
                                ]}>
                                <div className='warpInput'>
                                    <Input className='username' id='username_input' onClick={onClick}></Input>
                                    <span id='username' className='label'>
                                        Username
                                    </span>
                                </div>
                            </Form.Item>

                            <Form.Item
                                name='password'
                                className='formItem'
                                rules={[
                                    {
                                        required: true,
                                        message: "Please input your password!",
                                    },
                                ]}>
                                <div className='warpInput'>
                                    <Input.Password id='password_input' /* onFocus={onClick} */></Input.Password>
                                    <span id='password' className='label'>
                                        Password
                                    </span>
                                </div>
                            </Form.Item>

                            <Form.Item
                            /* wrapperCol={{
                        offset: 8,
                        span: 16,
                    }} */
                            >
                                <Button className='loginButton' type='primary' htmlType='submit'>
                                    Sign In
                                </Button>
                            </Form.Item>
                        </Form>
                    </div>
                </div>
                <div className='back'>
                    <div className='content'>
                        <h3 style={{ marginBottom: "20px" }}>SignUp</h3>
                        <Form
                            name='basic'
                            labelCol={{
                                span: 8,
                            }}
                            wrapperCol={{
                                span: 16,
                            }}
                            style={{
                                maxWidth: 600,
                            }}
                            initialValues={{
                                remember: true,
                            }}
                            onFinish={onRegisterFinish}
                            onFinishFailed={onFinishFailed}
                            autoComplete='off'>
                            <Form.Item
                                name='email'
                                className='formItem'
                                rules={[
                                    {
                                        required: true,
                                        message: "Please input your Email!",
                                    },
                                    {
                                        pattern: "@uni.sydney.edu.au",
                                        message: "Must use a University of Sydney email address",
                                    },
                                ]}>
                                <div className='warpInput'>
                                    <Input className='username' id='username_input' onClick={onClick}></Input>
                                    <span id='username' className='label'>
                                        Email
                                    </span>
                                </div>
                            </Form.Item>
                            <Form.Item
                                name='username'
                                className='formItem'
                                rules={[
                                    {
                                        required: true,
                                        message: "Please input your Username!",
                                    },
                                ]}>
                                <div className='warpInput'>
                                    <Input className='username' id='username_input' onClick={onClick}></Input>
                                    <span id='username' className='label'>
                                        Username
                                    </span>
                                </div>
                            </Form.Item>

                            <Form.Item
                                name='password'
                                className='formItem'
                                rules={[
                                    {
                                        required: true,
                                        message: "Please input your password!",
                                    },
                                ]}>
                                <div className='warpInput'>
                                    <Input.Password id='password_input' /* onFocus={onClick} */></Input.Password>
                                    <span id='password' className='label'>
                                        Password
                                    </span>
                                </div>
                            </Form.Item>

                            <Form.Item
                            /* wrapperCol={{
                        offset: 8,
                        span: 16,
                    }} */
                            >
                                <Button className='loginButton' type='primary' htmlType='submit'>
                                    Sign Up
                                </Button>
                            </Form.Item>
                        </Form>
                    </div>
                </div>
            </div>
            <Divider plain>{isChange == false ? "Don't have an account?" : "Already one of us?"}</Divider>
            <div className='change'>
                {/* <p>{isChange == true ? "Don't have an account?" : "Already one of us?"}</p> */}
                <Button onClick={changeForm} className='loginButton'>
                    {isChange == false ? "SIGNUP" : "SIGNIN"}
                </Button>
            </div>
        </LoginWarpper>
    );
};

export default Login;
