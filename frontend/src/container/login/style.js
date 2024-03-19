import { ColorFactory } from "antd/es/color-picker/color";
import { styled } from "styled-components";

export const LoginWarpper = styled.div`
    font-size: 30px;
    height: 100%;
    display: flex;
    flex-direction: column;
    //justify-content: center;
    align-items: center;
    .title {
        //position: absolute;
        margin-top: 30px;
        align-self: center;
    }
    .web {
        margin-top: 50px;
        display: flex;
        align-items: center;
        margin-right: 15px;
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

    .container {
        position: relative;
        width: 400px;
        height: 550px;
        //background-color: aquamarine;
        //3d
        perspective: 1000px;
        transform-style: preserve-3d;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .front,
    .back {
        position: absolute;
        margin-top: 30px;
        width: 400px;
        height: 500px;
        border-radius: 20px;
        /* background-color: #0984e3;
        background-size: cover;
        background-position: center; */
        border: 1px solid transparent;
        border-color: #d9d9d9;
        box-shadow: 0 2px 0 rgba(0, 0, 0, 0.02);
        display: flex;
        justify-content: center;
        align-items: center;
        //3d
        perspective: 1000px;
        transform-style: preserve-3d;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
        opacity: 0.99;
        //
        //transform: rotateY(60deg);
        transition: 0.7s ease-in-out;
    }
    .front {
        /* background-image: url("./img/Metaverse-1.png"); */
        .formItem {
            margin-bottom: 40px;
        }
    }
    .back {
        /* background-image: url("./img/Metaverse-3.jpg"); */
        transform: rotateY(180deg);
        .formItem {
            margin-bottom: 20px;
        }
        //display: none;
    }
    .content {
        transform: translateZ(60px);
        font-size: large;
        font-size: 40px;
        display: flex;
        //color: white;
        flex-direction: column;
        align-items: center;
        h3 {
            font-size: 30px;
            font-weight: 600;
            letter-spacing: 10px;
            //margin-right: 150px;
            text-transform: uppercase;
            margin-bottom: 35px;
            color: var(--llm);
        }
        .formItem {
            .warpInput {
                width: 300px;
            }
            .warpInput:focus-within {
                .label {
                    color: #4096ff;
                }
            }

            .label {
                position: absolute;
                top: -10px;
                left: 10px;
                background-color: #fff;
                padding: 0 5px;
                font-size: 13px;
                z-index: 2;
                color: #6f7780;
            }
            input {
                height: 50px;
            }
            .username {
                height: 58.5px;
            }
            .error {
                color: red !important;
            }
        }
        .loginButton {
            height: 50px;
            width: 300px;
            font-size: 18px;
        }
    }

    .change {
        display: flex;
        flex-direction: column;
        align-items: center;
        // margin-top: 100px;
        /* p {
            font-size: 20px;
            margin-bottom: 20px;
        }
        .change-button {
            width: 250px;
            height: 55px;
        } */
        .loginButton {
            height: 50px;
            width: 320px;
            font-size: 18px;
            color: var(--llm);
        }
    }

    /* height: 100vh; */
`;
