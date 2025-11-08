import { useState, useImperativeHandle, forwardRef } from 'react';
import { Card, Form, Input, Select, InputNumber, Button, message, Divider } from 'antd';
import { SaveOutlined, DownloadOutlined, CheckCircleOutlined, EditOutlined } from '@ant-design/icons';
import { exportApi } from '../../api/export';
import type { SaveProductInfoRequest, ExportRequest } from '../../types';
import { PHONE_MODELS } from '../../types';

interface Step4Props {
  taskId: string;
  onComplete?: () => void;
}

export interface Step4Ref {
  submit: () => Promise<void>;
  isSaved: () => boolean;
}

const Step4Export = forwardRef<Step4Ref, Step4Props>(({ taskId, onComplete }, ref) => {
  const [form] = Form.useForm();
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [savedProductInfo, setSavedProductInfo] = useState<SaveProductInfoRequest | null>(null);

  // 保存产品信息
  const handleSaveProductInfo = async () => {
    try {
      const values = await form.validateFields(['sku', 'asin', 'model']);

      setSaving(true);
      const productInfo: SaveProductInfoRequest = {
        task_id: taskId,
        sku: values.sku,
        asin: values.asin,
        model: values.model,
      };

      await exportApi.saveProductInfo(productInfo);

      message.success('✅ 产品信息已保存！');
      setSavedProductInfo(productInfo);
      setSaved(true);
    } catch (error: any) {
      if (error.errorFields) {
        message.warning('⚠️ 请填写完整的产品信息');
      } else {
        console.error('保存产品信息失败:', error);
        message.error(`❌ 保存失败: ${error.message}`);
      }
    } finally {
      setSaving(false);
    }
  };

  // 重新编辑产品信息
  const handleReEdit = () => {
    setSaved(false);
  };

  // 导出 Bulksheet
  const handleExport = async () => {
    try {
      const values = await form.validateFields(['daily_budget', 'ad_group_default_bid', 'keyword_bid']);

      setExporting(true);
      const exportRequest: ExportRequest = {
        task_id: taskId,
        daily_budget: values.daily_budget,
        ad_group_default_bid: values.ad_group_default_bid,
        keyword_bid: values.keyword_bid,
      };

      const blob = await exportApi.export(exportRequest);

      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `bulksheet_${taskId}_${Date.now()}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      message.success('🎉 Bulksheet 下载成功！');

      if (onComplete) {
        onComplete();
      }
    } catch (error: any) {
      if (error.errorFields) {
        message.warning('⚠️ 请填写完整的预算信息');
      } else {
        console.error('导出失败:', error);
        message.error(`❌ 导出失败: ${error.message}`);
      }
    } finally {
      setExporting(false);
    }
  };

  // 暴露方法给父组件
  useImperativeHandle(ref, () => ({
    submit: async () => {
      await handleExport();
    },
    isSaved: () => saved,
  }));

  return (
    <Card>
      <h2 className="text-2xl font-bold mb-4">步骤 4: 填写产品信息并导出</h2>
      <p className="text-gray-600 mb-6">填写产品和广告预算信息，即可下载 Bulksheet 文件</p>

      <Form
        form={form}
        layout="vertical"
        className="max-w-3xl"
        initialValues={{
          daily_budget: 1.5,
          ad_group_default_bid: 0.45,
          keyword_bid: 0.45,
        }}
      >
        {/* 阶段1：产品信息输入 */}
        {!saved && (
          <>
            <Divider orientation="left">📦 产品信息</Divider>

            <Form.Item
              label="产品 SKU"
              name="sku"
              rules={[
                { required: true, message: '请输入产品SKU' },
                { min: 1, max: 100, message: 'SKU长度应在1-100字符之间' },
              ]}
            >
              <Input placeholder="例如: ABC-12345" size="large" />
            </Form.Item>

            <Form.Item
              label="ASIN"
              name="asin"
              rules={[
                { required: true, message: '请输入ASIN' },
                { len: 10, message: 'ASIN必须是10位字符' },
                { pattern: /^[A-Z0-9]{10}$/, message: 'ASIN只能包含大写字母和数字' },
              ]}
            >
              <Input
                placeholder="10位ASIN码（例如: B08L5TNJHG）"
                size="large"
                maxLength={10}
                style={{ textTransform: 'uppercase' }}
              />
            </Form.Item>

            <Form.Item
              label="手机型号"
              name="model"
              rules={[{ required: true, message: '请选择手机型号' }]}
            >
              <Select placeholder="选择手机型号" size="large">
                {PHONE_MODELS.map((model) => (
                  <Select.Option key={model} value={model}>
                    {model}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                size="large"
                icon={<SaveOutlined />}
                onClick={handleSaveProductInfo}
                loading={saving}
                block
              >
                保存产品信息
              </Button>
            </Form.Item>

            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                💡 保存产品信息后，您可以继续填写广告预算并导出 Bulksheet
              </p>
            </div>
          </>
        )}

        {/* 阶段2：已保存产品信息 + 预算输入 */}
        {saved && savedProductInfo && (
          <>
            <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  <CheckCircleOutlined className="text-green-600 text-xl mr-2" />
                  <span className="text-green-800 font-semibold">产品信息已保存</span>
                </div>
                <Button
                  icon={<EditOutlined />}
                  onClick={handleReEdit}
                  size="small"
                >
                  重新编辑
                </Button>
              </div>

              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">SKU: </span>
                  <span className="font-semibold">{savedProductInfo.sku}</span>
                </div>
                <div>
                  <span className="text-gray-600">ASIN: </span>
                  <span className="font-semibold">{savedProductInfo.asin}</span>
                </div>
                <div>
                  <span className="text-gray-600">型号: </span>
                  <span className="font-semibold">{savedProductInfo.model}</span>
                </div>
              </div>
            </div>

            <Divider orientation="left">💰 广告预算设置</Divider>

            <div className="grid grid-cols-3 gap-4">
              <Form.Item
                label="每日预算 ($)"
                name="daily_budget"
                rules={[
                  { required: true, message: '请输入每日预算' },
                  { type: 'number', min: 0.01, message: '预算必须大于0' },
                ]}
              >
                <InputNumber
                  placeholder="1.5"
                  size="large"
                  className="w-full"
                  min={0.01}
                  step={0.1}
                  precision={2}
                />
              </Form.Item>

              <Form.Item
                label="广告组出价 ($)"
                name="ad_group_default_bid"
                rules={[
                  { required: true, message: '请输入广告组出价' },
                  { type: 'number', min: 0.01, message: '出价必须大于0' },
                ]}
              >
                <InputNumber
                  placeholder="0.45"
                  size="large"
                  className="w-full"
                  min={0.01}
                  step={0.05}
                  precision={2}
                />
              </Form.Item>

              <Form.Item
                label="关键词出价 ($)"
                name="keyword_bid"
                rules={[
                  { required: true, message: '请输入关键词出价' },
                  { type: 'number', min: 0.01, message: '出价必须大于0' },
                ]}
              >
                <InputNumber
                  placeholder="0.45"
                  size="large"
                  className="w-full"
                  min={0.01}
                  step={0.05}
                  precision={2}
                />
              </Form.Item>
            </div>

            <Form.Item>
              <Button
                type="primary"
                size="large"
                icon={<DownloadOutlined />}
                onClick={handleExport}
                loading={exporting}
                block
              >
                导出 Bulksheet Excel 文件
              </Button>
            </Form.Item>

            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700 mb-2">💡 <strong>导出说明</strong>:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 文件将包含所有生成的搜索词和关键词</li>
                <li>• Excel 格式符合亚马逊广告 Bulksheet 规范</li>
                <li>• 可直接上传到亚马逊广告后台批量创建广告活动</li>
                <li>• 预算和出价信息将应用到所有广告组和关键词</li>
              </ul>
            </div>
          </>
        )}
      </Form>
    </Card>
  );
});

Step4Export.displayName = 'Step4Export';

export default Step4Export;
