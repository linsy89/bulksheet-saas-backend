import { Link } from 'react-router-dom';
import { Button } from 'antd';
import {
  RocketOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';

const HomePage = () => {
  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center">
      <div className="max-w-3xl mx-auto text-center px-4">
        {/* Hero Section */}
        <h1 className="text-7xl font-bold text-gray-900 mb-6 leading-tight">
          一键生成<br/>亚马逊广告关键词
        </h1>

        <p className="text-3xl text-gray-600 mb-12">
          从 1 个概念到 1000 个关键词
        </p>

        {/* CTA Button */}
        <Link to="/wizard">
          <Button
            type="primary"
            size="large"
            icon={<RocketOutlined />}
            className="h-20 px-16 text-2xl font-bold shadow-2xl hover:shadow-3xl mb-16"
            style={{ fontSize: '24px' }}
          >
            开始创建
          </Button>
        </Link>

        {/* Features - Simple badges */}
        <div className="flex items-center justify-center space-x-8 text-gray-600">
          <div className="flex items-center space-x-2">
            <ThunderboltOutlined className="text-2xl text-yellow-500" />
            <span className="text-lg">AI 智能生成</span>
          </div>

          <div className="flex items-center space-x-2">
            <ClockCircleOutlined className="text-2xl text-blue-500" />
            <span className="text-lg">5 分钟完成</span>
          </div>

          <div className="flex items-center space-x-2">
            <CheckCircleOutlined className="text-2xl text-green-500" />
            <span className="text-lg">符合亚马逊规范</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
