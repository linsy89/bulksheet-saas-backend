import { Layout as AntLayout } from 'antd';
import { HeartFilled } from '@ant-design/icons';

const { Footer: AntFooter } = AntLayout;

const Footer = () => {
  return (
    <AntFooter className="text-center bg-gray-50 border-t">
      <div className="text-gray-600">
        © 2025 Bulksheet SaaS | Made with <HeartFilled className="text-red-500 mx-1" /> by AI
      </div>
    </AntFooter>
  );
};

export default Footer;
