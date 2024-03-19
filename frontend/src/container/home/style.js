import { ColorFactory } from "antd/es/color-picker/color";
import { styled } from "styled-components";

export const HomeWarpper = styled.div`
    color: red;
    font-size: 30px;
    height: 100%;
    /* height: 100vh; */
    .layout {
        height: 100%;

        .ant-layout-sider-trigger {
            background-color: var(--lm);
        }
        .ant-layout-sider-children {
            background-color: var(--w);
        }
        /* .ant-menu-submenu-selected {
            .ant-menu-submenu-title {
                color: white;
            }
        } */
        /*.menu {
            background-color: var(--m);
            color: var(--w);
            span {
                font-size: 17px;
            }
            .ant-menu-sub {
                background-color: var(--lm);
            }
             ul {
                background-color: var(--m) !important;
            }
            li {
                color: var(--dm);
                background-color: var(--lm) !important;
            } 
        } */
    }
    .header {
        height: 100px;
        color: white;
        display: flex;
        align-items: center;
        padding-left: 20px;
        background-color: #fdfdfd;
        //background: #fafafa;
        justify-content: space-between;
        .web {
            display: flex;
            align-items: center;
            .logo {
                height: 80px;
            }
            .webName {
                margin-left: 30px;
                font-size: 30px;
                color: var(--llm);
                font-weight: 600;
                letter-spacing: 1px;
            }
        }

        .Nav {
            display: flex;
            justify-content: space-between;
            font-size: 30px;
            color: var(--llm);
            .userName {
                display: inline-block;
                margin-left: 150px;
                font-size: 20px;
            }
        }
    }
    .recipe {
        height: 100%;
        width: 100%;
        //background-color: #fdfdfd;
        .recipeTitle {
            display: flex;
            height: 50px;
            //justify-content: center;
            align-items: center;
            margin-bottom: 20px;
            .deleteButton {
                height: 40px;
                width: 150px;
            }
        }
        .calculateBtn {
            //position: absolute;
            margin-top: 30px;
            height: 45px;
            width: 150px;
            //margin-right: 70%;
            //right: 52%;
            font-size: 16px;
            //transform: translate(-208px, 6px);
        }
        .recipeName {
            font-size: 25px;
        }
    }

    .ant-layout-sider-trigger {
        //position: relative;
    }
    .borderButton {
        position: relative;
        height: 60px;
        width: 200px;
        .button {
            position: relative;
            height: 100%;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            font-size: 18px;
            color: var(--dm);
            margin-right: 20px;
            font-size: 24px;
            font-weight: 600;
            letter-spacing: 1px;
            &:hover {
                color: rgb(18, 39, 59);
            }
        }
        .button::after,
        .button::before {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            bottom: 0;
            width: 100%;
            height: 100%;
            border: 2px solid rgb(46, 70, 92);
            transition: all 0.3s ease;
            opacity: 0;
        }
        .button:hover::before {
            opacity: 1;
            transform: translate(-5px, -5px);
        }
        .button:hover::after {
            opacity: 1;
            transform: translate(5px, 5px);
        }
    }

    //tables
    .warp_recipe {
        position: relative;
        display: flex;
        //align-items: center;
        justify-content: space-between;
        .nutrition_table {
            position: relative;
            width: 48%;
        }
        .ingredient_table {
            width: 58%;
        }
        .ingredient_nutrition_table {
            width: 38%;
        }
        .tableName {
            margin-left: 7px;
            font-size: 23px;
        }
        .btn_with_tabs {
            position: absolute;
            right: 0;
            top: 16px;
            z-index: 5;
        }
    }
    .pie_charts_container {
        display: flex;
        justify-content: space-between; /* 为两个饼图之间留出一定的间距 */
        margin-top: 30px;  /* 与上方的内容保持30像素的间距 */
    }
    
    .single_pie_chart {
        flex: 1; /* 这使得每个饼图容器都占用可用空间的一半 */
        display: flex;
        justify-content: center;
    }
    
    .price {
        span {
            font-size: 18px;
        }
    }

    //user table
    .user_table {
        .user_btns {
            position: absolute;
            right: 30px;
            top: 35px;
        }
        .user_delete_btn {
            width: 150px;
            height: 45px;
        }
    }
`;
