import { useState, useImperativeHandle, forwardRef, useMemo } from 'react';
import { Card, Table, message, Tag, Rate, Tooltip, Button, List, Space } from 'antd';
import { InfoCircleOutlined, CheckCircleOutlined, EditOutlined } from '@ant-design/icons';
import type { Attribute } from '../../types';
import { attributeApi } from '../../api/attribute';
import type { ColumnsType } from 'antd/es/table';

interface Step2Props {
  taskId: string;
  taskData: any;
  onNext: () => void;
}

export interface Step2Ref {
  submit: () => Promise<void>;
  hasSelection: () => boolean;
  isConfirmed: () => boolean;
}

const Step2SelectAttributes = forwardRef<Step2Ref, Step2Props>(({ taskId, taskData, onNext }, ref) => {
  // ID增强：为没有id的数据补充id字段（修复复选框bug）
  const enhancedAttributes = useMemo(() =>
    (taskData?.attributes || []).map((attr: Attribute, idx: number) => ({
      ...attr,
      id: attr.id !== undefined ? attr.id : (idx + 1),
    })), [taskData?.attributes]
  );

  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>(
    enhancedAttributes.filter((attr: Attribute) => attr.is_selected).map((attr: Attribute) => attr.id) || []
  );
  const [loading, setLoading] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [confirmedAttributes, setConfirmedAttributes] = useState<Attribute[]>([]);

  // 确认选择处理函数（调用API保存选择）
  const handleConfirm = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('⚠️ 请至少选择一个属性词');
      return;
    }

    setLoading(true);
    try {
      // 调用后端API更新属性词选择
      const response = await attributeApi.updateSelection(taskId, {
        selected_attribute_ids: selectedRowKeys,
        new_attributes: [],
        deleted_attribute_ids: [],
      });

      message.success(`✅ 已确认选择 ${response.selected_count} 个属性词！`);

      // 保存确认后的属性词列表
      const selected = enhancedAttributes.filter((attr: Attribute) => selectedRowKeys.includes(attr.id));
      setConfirmedAttributes(selected);
      setConfirmed(true);
    } catch (error: any) {
      console.error('更新选择失败:', error);
      message.error(`❌ 确认失败: ${error.message}`);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // 重新选择处理函数
  const handleReselect = () => {
    setConfirmed(false);
  };

  // 暴露方法给父组件
  useImperativeHandle(ref, () => ({
    submit: async () => {
      // 如果已确认，直接跳转到下一步
      if (confirmed) {
        onNext();
      } else {
        message.warning('⚠️ 请先确认选择');
      }
    },
    hasSelection: () => selectedRowKeys.length > 0,
    isConfirmed: () => confirmed,
  }));

  // 定义表格列 - 调整列宽以完整展示内容
  const columns: ColumnsType<Attribute> = [
    {
      title: '属性词',
      dataIndex: 'word',
      key: 'word',
      width: 180,
      render: (text: string, record: Attribute) => (
        <span>
          <span className="font-semibold">{text}</span>
          {record.recommended && (
            <Tag color="gold" className="ml-2">推荐</Tag>
          )}
        </span>
      ),
    },
    {
      title: '中文翻译',
      dataIndex: 'translation',
      key: 'translation',
      width: 200,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => {
        const typeMap: Record<string, { text: string; color: string }> = {
          original: { text: '原词', color: 'blue' },
          synonym: { text: '同义词', color: 'green' },
          related: { text: '相关词', color: 'purple' },
          variant: { text: '变体词', color: 'orange' },
          custom: { text: '自定义', color: 'red' },
        };
        const config = typeMap[type] || { text: type, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: (
        <span>
          搜索价值{' '}
          <Tooltip title="根据搜索量、竞争度、转化潜力综合评估">
            <InfoCircleOutlined />
          </Tooltip>
        </span>
      ),
      dataIndex: 'search_value_stars',
      key: 'search_value_stars',
      width: 130,
      render: (stars: number) => <Rate disabled defaultValue={stars} />,
      sorter: (a: Attribute, b: Attribute) => a.search_value_stars - b.search_value_stars,
    },
    {
      title: '使用场景',
      dataIndex: 'use_case',
      key: 'use_case',
      width: 300,
    },
  ];

  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys as number[]);
    },
  };

  return (
    <Card>
      <h2 className="text-2xl font-bold mb-4">步骤 2: 选择属性词</h2>

      {/* 阶段1：选择阶段 */}
      {!confirmed && (
        <>
          <p className="text-gray-600 mb-6">
            AI 已为您生成 {taskData?.metadata?.total_count || 0} 个相关属性词，请选择您需要的词汇
          </p>

          {/* 统计信息 */}
          <div className="mb-4 p-4 bg-blue-50 rounded-lg">
            <span className="text-blue-800">
              已选择 <strong className="text-2xl">{selectedRowKeys.length}</strong> 个属性词
            </span>
            {taskData?.metadata?.recommended_count > 0 && (
              <span className="ml-4 text-blue-600">
                （推荐选择 {taskData.metadata.recommended_count} 个）
              </span>
            )}
          </div>

          {/* 属性词表格 */}
          <Table
            rowSelection={rowSelection}
            columns={columns}
            dataSource={enhancedAttributes}
            rowKey="id"
            pagination={{
              defaultPageSize: 20,
              pageSize: 20,
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50', '100'],
              showTotal: (total) => `共 ${total} 个属性词`,
            }}
            loading={loading}
            size="middle"
          />

          {/* 确认选择按钮 */}
          <div className="mt-4 flex justify-center">
            <Button
              type="primary"
              size="large"
              icon={<CheckCircleOutlined />}
              onClick={handleConfirm}
              loading={loading}
              disabled={selectedRowKeys.length === 0}
            >
              确认选择（{selectedRowKeys.length}个）
            </Button>
          </div>

          {/* 提示信息 */}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700 mb-2">💡 <strong>选择建议</strong>:</p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• <strong>推荐词</strong>: 标记为"推荐"的词汇是 AI 根据搜索价值评估的高质量词汇</li>
              <li>• <strong>搜索价值</strong>: 星级越高，表示搜索量大、竞争适中、转化潜力好</li>
              <li>• <strong>类型多样化</strong>: 建议同时选择同义词、相关词和变体词，覆盖更多搜索场景</li>
              <li>• <strong>数量建议</strong>: 一般选择 5-15 个属性词，可生成足够丰富的搜索词组合</li>
            </ul>
          </div>
        </>
      )}

      {/* 阶段2：已确认阶段 */}
      {confirmed && (
        <>
          <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <CheckCircleOutlined className="text-green-600 text-xl mr-2" />
                <span className="text-green-800 font-semibold">
                  已确认选择 {confirmedAttributes.length} 个属性词
                </span>
              </div>
              <Button
                icon={<EditOutlined />}
                onClick={handleReselect}
              >
                重新选择
              </Button>
            </div>
          </div>

          {/* 简洁的已选列表 */}
          <List
            bordered
            dataSource={confirmedAttributes}
            renderItem={(attr) => (
              <List.Item>
                <Space size="large" className="w-full">
                  <div style={{ minWidth: '150px' }}>
                    <span className="font-semibold text-base">{attr.word}</span>
                    {attr.recommended && (
                      <Tag color="gold" className="ml-2">推荐</Tag>
                    )}
                  </div>
                  <div style={{ minWidth: '180px' }}>
                    <span className="text-gray-600">{attr.translation}</span>
                  </div>
                  <div style={{ minWidth: '100px' }}>
                    <Rate disabled defaultValue={attr.search_value_stars} style={{ fontSize: '14px' }} />
                  </div>
                  <div className="flex-1">
                    <span className="text-gray-500 text-sm">{attr.use_case}</span>
                  </div>
                </Space>
              </List.Item>
            )}
          />

          {/* 提示信息 */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              ✅ 选择已保存！点击右下角"下一步"按钮继续进行本体词选择
            </p>
          </div>
        </>
      )}
    </Card>
  );
});

Step2SelectAttributes.displayName = 'Step2SelectAttributes';

export default Step2SelectAttributes;
