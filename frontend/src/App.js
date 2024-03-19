import React from 'react';
import { Button, ConfigProvider, Space } from 'antd';
import { Outlet, NavLink } from 'react-router-dom';

class App extends React.Component{
  render(){
    return (
    <div>
      {/* <Button type='primary'>123</Button>
      <NavLink to="/home">home</NavLink>
      <NavLink to="/login">login</NavLink> */}
        {/* <ConfigProvider
          theme={{
            token: {
              // Seed Token，影响范围大
              colorPrimary: '#00b96b',
              borderRadius: 2,

              // 派生变量，影响范围小
              colorBgContainer: '#f6ffed',
            },
          }}
        >
          <Space>
            <Button type="primary">Primary</Button>
            <Button>Default</Button>
          </Space>
        </ConfigProvider> */}
        {/* <Outlet>
          
        </Outlet> */}
    </div>
    )
  }
}

export default App;
