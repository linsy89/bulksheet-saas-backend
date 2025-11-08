import { createBrowserRouter } from 'react-router-dom';
import Layout from './components/layout/Layout';
import HomePage from './pages/HomePage';
import WizardPage from './pages/WizardPage';
import AttributeGeneratePage from './pages/AttributeGeneratePage';
import AttributeSelectPage from './pages/AttributeSelectPage';
import EntityWordPage from './pages/EntityWordPage';
import SearchTermPage from './pages/SearchTermPage';
import ExportPage from './pages/ExportPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'wizard/:taskId?',
        element: <WizardPage />,
      },
      // 保留旧路由以兼容
      {
        path: 'attributes/generate',
        element: <AttributeGeneratePage />,
      },
      {
        path: 'attributes/select/:taskId',
        element: <AttributeSelectPage />,
      },
      {
        path: 'entity-words/:taskId',
        element: <EntityWordPage />,
      },
      {
        path: 'search-terms/:taskId',
        element: <SearchTermPage />,
      },
      {
        path: 'export/:taskId',
        element: <ExportPage />,
      },
    ],
  },
]);
