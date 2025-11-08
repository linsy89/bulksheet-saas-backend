import { Outlet } from 'react-router-dom';
import { Layout as AntLayout } from 'antd';
import Header from './Header';
import Footer from './Footer';

const { Content } = AntLayout;

const Layout = () => {
  return (
    <AntLayout className="min-h-screen">
      <Header />
      <Content className="bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Outlet />
        </div>
      </Content>
      <Footer />
    </AntLayout>
  );
};

export default Layout;
