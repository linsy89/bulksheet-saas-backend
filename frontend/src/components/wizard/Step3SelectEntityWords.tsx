import { useState, useImperativeHandle, forwardRef, useMemo, useEffect } from 'react';
import { Card, Table, message, Tag, Rate, Tooltip, Button, List, Space, Spin, Statistic, Row, Col } from 'antd';
import { InfoCircleOutlined, CheckCircleOutlined, EditOutlined, LoadingOutlined, ThunderboltOutlined } from '@ant-design/icons';
import type { EntityWord, SearchTerm } from '../../types';
import { entityWordApi } from '../../api/entity-word';
import { searchTermApi } from '../../api/search-term';
import type { ColumnsType } from 'antd/es/table';

interface Step3Props {
  taskId: string;
  onNext: () => void;
}

export interface Step3Ref {
  submit: () => Promise<void>;
  hasSelection: () => boolean;
  isConfirmed: () => boolean;
}

const Step3SelectEntityWords = forwardRef<Step3Ref, Step3Props>(({ taskId, onNext }, ref) => {
  const [entityWords, setEntityWords] = useState<EntityWord[]>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [confirmedEntityWords, setConfirmedEntityWords] = useState<EntityWord[]>([]);
  const [generatingSearchTerms, setGeneratingSearchTerms] = useState(false);
  const [searchTerms, setSearchTerms] = useState<SearchTerm[]>([]);
  const [searchTermsGenerated, setSearchTermsGenerated] = useState(false);

  // ID增强：确保所有数据都有id字段
  const enhancedEntityWords = useMemo(() =>
    entityWords.map((ew, idx) => ({
      ...ew,
      id: ew.id !== undefined ? ew.id : (idx + 1),
    })), [entityWords]
  );

  // 组件加载时自动生成本体词
  useEffect(() => {
    const generateEntityWords = async () => {
      setGenerating(true);
      try {
        const response = await entityWordApi.generate(taskId);
        setEntityWords(response.entity_words);

        // 默认选中所有推荐的本体词
        const recommendedIds = response.entity_words
          .filter(ew => ew.recommended)
          .map(ew => ew.id);
        setSelectedRowKeys(recommendedIds);

        message.success(`✅ 成功生成 ${response.entity_words.length} 个本体词变体！`);
      } catch (error: any) {
        console.error('生成本体词失败:', error);
        message.error(`❌ 生成失败: ${error.message}`);
      } finally {
        setGenerating(false);
      }
    };

    generateEntityWords();
  }, [taskId]);

  // 确认选择处理函数（确认后自动生成搜索词）
  const handleConfirm = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('⚠️ 请至少选择一个本体词');
      return;
    }

    setLoading(true);
    try {
      const response = await entityWordApi.updateSelection(taskId, {
        selected_entity_word_ids: selectedRowKeys,
        new_entity_words: [],
        deleted_entity_word_ids: [],
      });

      message.success(`✅ 已确认选择 ${response.metadata.selected_count} 个本体词！`);

      // 保存确认后的本体词列表
      const selected = enhancedEntityWords.filter(ew => selectedRowKeys.includes(ew.id));
      setConfirmedEntityWords(selected);
      setConfirmed(true);

      // 自动生成搜索词
      await generateSearchTerms();
    } catch (error: any) {
      console.error('更新选择失败:', error);
      message.error(`❌ 确认失败: ${error.message}`);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // 生成搜索词（笛卡尔积：属性词 × 本体词）
  const generateSearchTerms = async () => {
    setGeneratingSearchTerms(true);
    try {
      const response = await searchTermApi.generate(taskId);
      setSearchTerms(response.search_terms);
      setSearchTermsGenerated(true);

      message.success(
        `🎉 成功生成 ${response.search_terms.length} 个搜索词！` +
        `（${response.metadata.attribute_count} × ${response.metadata.entity_word_count}）`
      );
    } catch (error: any) {
      console.error('生成搜索词失败:', error);
      message.error(`❌ 生成搜索词失败: ${error.message}`);
    } finally {
      setGeneratingSearchTerms(false);
    }
  };

  // 重新选择处理函数
  const handleReselect = () => {
    setConfirmed(false);
  };

  // 暴露方法给父组件
  useImperativeHandle(ref, () => ({
    submit: async () => {
      if (confirmed) {
        onNext();
      } else {
        message.warning('⚠️ 请先确认选择');
      }
    },
    hasSelection: () => selectedRowKeys.length > 0,
    isConfirmed: () => confirmed,
  }));

  // 定义表格列
  const columns: ColumnsType<EntityWord> = [
    {
      title: '本体词',
      dataIndex: 'entity_word',
      key: 'entity_word',
      width: 200,
      render: (text: string, record: EntityWord) => (
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
          variant: { text: '变体词', color: 'orange' },
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
      sorter: (a: EntityWord, b: EntityWord) => a.search_value_stars - b.search_value_stars,
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

  // 生成中状态
  if (generating) {
    return (
      <Card>
        <div className="text-center py-12">
          <Spin
            indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />}
            tip="AI 正在生成本体词变体，预计需要 30-60 秒，请耐心等待..."
            size="large"
          >
            <div className="mt-8" />
          </Spin>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="text-2xl font-bold mb-4">步骤 3: 选择本体词</h2>

      {/* 阶段1：选择阶段 */}
      {!confirmed && (
        <>
          <p className="text-gray-600 mb-6">
            AI 已为您生成 {enhancedEntityWords.length} 个本体词变体，请选择您需要的词汇
          </p>

          {/* 统计信息 */}
          <div className="mb-4 p-4 bg-blue-50 rounded-lg">
            <span className="text-blue-800">
              已选择 <strong className="text-2xl">{selectedRowKeys.length}</strong> 个本体词
            </span>
            <span className="ml-4 text-blue-600">
              （将生成 {selectedRowKeys.length} × 属性词数量 个搜索词）
            </span>
          </div>

          {/* 本体词表格 */}
          <Table
            rowSelection={rowSelection}
            columns={columns}
            dataSource={enhancedEntityWords}
            rowKey="id"
            pagination={{
              defaultPageSize: 20,
              pageSize: 20,
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50'],
              showTotal: (total) => `共 ${total} 个本体词`,
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
              <li>• <strong>类型多样化</strong>: 建议同时选择原词、同义词和变体词，覆盖更多搜索场景</li>
              <li>• <strong>数量建议</strong>: 一般选择 3-8 个本体词，与属性词组合生成丰富的搜索词</li>
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
                  已确认选择 {confirmedEntityWords.length} 个本体词
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
            dataSource={confirmedEntityWords}
            renderItem={(ew) => (
              <List.Item>
                <Space size="large" className="w-full">
                  <div style={{ minWidth: '180px' }}>
                    <span className="font-semibold text-base">{ew.entity_word}</span>
                    {ew.recommended && (
                      <Tag color="gold" className="ml-2">推荐</Tag>
                    )}
                  </div>
                  <div style={{ minWidth: '180px' }}>
                    <span className="text-gray-600">{ew.translation}</span>
                  </div>
                  <div style={{ minWidth: '100px' }}>
                    <Rate disabled defaultValue={ew.search_value_stars} style={{ fontSize: '14px' }} />
                  </div>
                  <div className="flex-1">
                    <span className="text-gray-500 text-sm">{ew.use_case}</span>
                  </div>
                </Space>
              </List.Item>
            )}
          />

          {/* 搜索词生成区域 */}
          <div className="mt-6">
            <h3 className="text-xl font-bold mb-4 flex items-center">
              <ThunderboltOutlined className="text-yellow-500 mr-2" />
              搜索词生成结果
            </h3>

            {generatingSearchTerms && (
              <div className="text-center py-8">
                <Spin
                  indicator={<LoadingOutlined style={{ fontSize: 36 }} spin />}
                  tip="正在生成搜索词组合，请稍候..."
                />
              </div>
            )}

            {!generatingSearchTerms && searchTermsGenerated && (
              <>
                {/* 统计信息 */}
                <div className="mb-6">
                  <Row gutter={16}>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="总搜索词数"
                          value={searchTerms.length}
                          suffix="个"
                          valueStyle={{ color: '#3f8600' }}
                        />
                      </Card>
                    </Col>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="有效搜索词"
                          value={searchTerms.filter(st => st.length <= 80).length}
                          suffix="个"
                          valueStyle={{ color: '#1890ff' }}
                        />
                      </Card>
                    </Col>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="组合方式"
                          value={`${confirmedEntityWords.length}`}
                          suffix={`本体词 × 属性词`}
                          valueStyle={{ color: '#cf1322' }}
                        />
                      </Card>
                    </Col>
                  </Row>
                </div>

                {/* 搜索词列表（分页展示前50个） */}
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-3">
                    以下是生成的部分搜索词示例（显示前50个）：
                  </p>
                  <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                    <div className="grid grid-cols-2 gap-2">
                      {searchTerms.slice(0, 50).map((st, idx) => (
                        <div
                          key={st.id || idx}
                          className={`px-3 py-2 rounded ${
                            st.length <= 80 ? 'bg-white border border-gray-200' : 'bg-red-50 border border-red-200'
                          }`}
                        >
                          <span className="text-sm font-mono">{st.term}</span>
                          {st.length > 80 && (
                            <Tag color="red" className="ml-2 text-xs">超长</Tag>
                          )}
                        </div>
                      ))}
                    </div>
                    {searchTerms.length > 50 && (
                      <div className="mt-4 text-center text-gray-500">
                        ... 还有 {searchTerms.length - 50} 个搜索词未显示
                      </div>
                    )}
                  </div>
                </div>

                {/* 提示信息 */}
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-800">
                    ✅ 搜索词生成完成！点击右下角"下一步"按钮继续填写产品信息并导出
                  </p>
                </div>
              </>
            )}
          </div>
        </>
      )}
    </Card>
  );
});

Step3SelectEntityWords.displayName = 'Step3SelectEntityWords';

export default Step3SelectEntityWords;
