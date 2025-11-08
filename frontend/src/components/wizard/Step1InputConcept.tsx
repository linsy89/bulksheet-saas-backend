import { useState } from 'react';
import { Card, Form, Input, Button, message, Spin } from 'antd';
import { RocketOutlined } from '@ant-design/icons';
import { attributeApi } from '../../api/attribute';
import type { GenerateAttributesRequest } from '../../types';

interface Step1Props {
  onNext: (taskId: string, data: any) => void;
}

const Step1InputConcept = ({ onNext }: Step1Props) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: GenerateAttributesRequest) => {
    setLoading(true);
    try {
      // 调用后端API生成属性词
      const response = await attributeApi.generate(values);

      message.success(`✅ 成功生成 ${response.metadata.total_count} 个属性词！`);

      // 传递task_id和数据到下一步
      onNext(response.task_id, response);
    } catch (error: any) {
      console.error('生成属性词失败:', error);
      message.error(`❌ 生成失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <h2 className="text-2xl font-bold mb-4">步骤 1: 输入产品概念</h2>
      <p className="text-gray-600 mb-6">
        输入您的产品属性概念和核心词，AI 将为您扩展生成相关属性词
      </p>

      <Spin spinning={loading} tip="AI 正在生成属性词，预计需要 60-120 秒，请耐心等待...">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          className="max-w-xl"
        >
          <Form.Item
            label="产品属性概念"
            name="concept"
            rules={[
              { required: true, message: '请输入产品属性概念' },
              { min: 1, max: 50, message: '长度应在 1-50 个字符之间' },
            ]}
            tooltip="例如: cute（可爱）, waterproof（防水）, vintage（复古）"
          >
            <Input
              size="large"
              placeholder="例如: cute, waterproof, vintage"
              disabled={loading}
            />
          </Form.Item>

          <Form.Item
            label="产品核心词"
            name="entity_word"
            rules={[
              { required: true, message: '请输入产品核心词' },
              { min: 1, max: 50, message: '长度应在 1-50 个字符之间' },
            ]}
            tooltip="例如: phone case（手机壳）, backpack（背包）, mug（马克杯）"
          >
            <Input
              size="large"
              placeholder="例如: phone case, backpack, mug"
              disabled={loading}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              icon={<RocketOutlined />}
              loading={loading}
              block
            >
              {loading ? 'AI 生成中...' : '生成属性词'}
            </Button>
          </Form.Item>

          {/* 示例提示 */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800 mb-2">💡 <strong>示例</strong>:</p>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• 产品属性概念: <code className="bg-white px-2 py-1 rounded">cute</code></li>
              <li>• 产品核心词: <code className="bg-white px-2 py-1 rounded">phone case</code></li>
              <li>• 将生成: adorable, kawaii, lovely, sweet 等相关属性词</li>
            </ul>
          </div>
        </Form>
      </Spin>
    </Card>
  );
};

export default Step1InputConcept;
