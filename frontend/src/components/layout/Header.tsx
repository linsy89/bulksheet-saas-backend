import { Link } from 'react-router-dom';
import { Layout as AntLayout, Button } from 'antd';
import { RocketOutlined, HomeOutlined } from '@ant-design/icons';

const { Header: AntHeader } = AntLayout;

const Header = () => {
  return (
    <AntHeader className="bg-white shadow-md px-8 flex items-center justify-between h-16">
      <Link to="/" className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
        <RocketOutlined className="text-3xl text-blue-600" />
        <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Bulksheet SaaS
        </span>
      </Link>

      <nav className="flex items-center space-x-2">
        <Link to="/">
          <Button type="text" icon={<HomeOutlined />}>
            首页
          </Button>
        </Link>
        <Link to="/attributes/generate">
          <Button type="primary" icon={<RocketOutlined />}>
            开始使用
          </Button>
        </Link>
      </nav>
    </AntHeader>
  );
};

export default Header;
