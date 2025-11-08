import { useState, useRef } from 'react';
import { Steps, Card, Button, Space, Statistic, Row, Col, message } from 'antd';
import {
  EditOutlined,
  CheckOutlined,
  AppstoreOutlined,
  DownloadOutlined,
  LeftOutlined,
  RightOutlined,
} from '@ant-design/icons';
import Step1InputConcept from '../components/wizard/Step1InputConcept';
import Step2SelectAttributes, { type Step2Ref } from '../components/wizard/Step2SelectAttributes';
import Step3SelectEntityWords, { type Step3Ref } from '../components/wizard/Step3SelectEntityWords';
import Step4Export, { type Step4Ref } from '../components/wizard/Step4Export';

const WizardPage = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [taskId, setTaskId] = useState<string>('');
  const [taskData, setTaskData] = useState<any>(null);
  const [nextLoading, setNextLoading] = useState(false);

  // Ref 用于访问 Step2, Step3, Step4 的方法
  const step2Ref = useRef<Step2Ref>(null);
  const step3Ref = useRef<Step3Ref>(null);
  const step4Ref = useRef<Step4Ref>(null);

  // 处理步骤1完成
  const handleStep1Complete = (newTaskId: string, data: any) => {
    setTaskId(newTaskId);
    setTaskData(data);
    setCurrentStep(1); // 自动进入下一步
  };

  // 处理步骤2完成
  const handleStep2Complete = () => {
    setCurrentStep(2); // 自动进入步骤3
  };

  // 处理步骤3完成
  const handleStep3Complete = () => {
    setCurrentStep(3); // 自动进入步骤4
  };

  const steps = [
    {
      title: '输入概念',
      icon: <EditOutlined />,
      content: <Step1InputConcept onNext={handleStep1Complete} />,
    },
    {
      title: '选择属性词',
      icon: <CheckOutlined />,
      content: taskData ? (
        <Step2SelectAttributes
          ref={step2Ref}
          taskId={taskId}
          taskData={taskData}
          onNext={handleStep2Complete}
        />
      ) : (
        <Card>
          <div className="text-center py-8 text-gray-400">
            <p>请先完成步骤1</p>
          </div>
        </Card>
      ),
    },
    {
      title: '选择本体词',
      icon: <AppstoreOutlined />,
      content: taskId ? (
        <Step3SelectEntityWords
          ref={step3Ref}
          taskId={taskId}
          onNext={handleStep3Complete}
        />
      ) : (
        <Card>
          <div className="text-center py-8 text-gray-400">
            <p>请先完成步骤2</p>
          </div>
        </Card>
      ),
    },
    {
      title: '导出广告表',
      icon: <DownloadOutlined />,
      content: taskId ? (
        <Step4Export ref={step4Ref} taskId={taskId} />
      ) : (
        <Card>
          <div className="text-center py-8 text-gray-400">
            <p>请先完成步骤3</p>
          </div>
        </Card>
      ),
    },
  ];

  const handleNext = async () => {
    // 步骤2需要检查是否已确认
    if (currentStep === 1) {
      if (!step2Ref.current) {
        message.error('步骤2组件未加载');
        return;
      }

      // 检查是否已确认选择
      if (!step2Ref.current.isConfirmed()) {
        message.warning('⚠️ 请先确认选择属性词');
        return;
      }

      setNextLoading(true);
      try {
        await step2Ref.current.submit();
        // submit 成功后会自动调用 onNext，不需要这里手动跳转
      } catch (error) {
        // 错误已在 Step2 中处理
      } finally {
        setNextLoading(false);
      }
      return;
    }

    // 步骤3需要检查是否已确认
    if (currentStep === 2) {
      if (!step3Ref.current) {
        message.error('步骤3组件未加载');
        return;
      }

      // 检查是否已确认选择
      if (!step3Ref.current.isConfirmed()) {
        message.warning('⚠️ 请先确认选择本体词');
        return;
      }

      setNextLoading(true);
      try {
        await step3Ref.current.submit();
        // submit 成功后会自动调用 onNext，不需要这里手动跳转
      } catch (error) {
        // 错误已在 Step3 中处理
      } finally {
        setNextLoading(false);
      }
      return;
    }

    // 其他步骤直接跳转
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="py-8">
      <div className="max-w-7xl mx-auto">
        <Row gutter={24}>
          {/* 主内容区 */}
          <Col xs={24} lg={17}>
            {/* 进度条 */}
            <Card className="mb-6">
              <Steps
                current={currentStep}
                items={steps.map((step, index) => ({
                  key: `step-${index}`,
                  title: step.title,
                  icon: step.icon,
                }))}
              />
            </Card>

            {/* 步骤内容 */}
            <div className="mb-6">
              {steps[currentStep].content}
            </div>

            {/* 底部按钮 */}
            <Card>
              <Space className="w-full justify-between">
                <Button
                  size="large"
                  icon={<LeftOutlined />}
                  onClick={handlePrev}
                  disabled={currentStep === 0}
                >
                  上一步
                </Button>

                {currentStep < steps.length - 1 ? (
                  <Button
                    type="primary"
                    size="large"
                    icon={<RightOutlined />}
                    onClick={handleNext}
                    loading={nextLoading}
                    iconPosition="end"
                  >
                    下一步
                  </Button>
                ) : (
                  <Button
                    type="primary"
                    size="large"
                    icon={<DownloadOutlined />}
                    onClick={async () => {
                      if (!step4Ref.current) {
                        message.error('步骤4组件未加载');
                        return;
                      }

                      // 检查是否已保存产品信息
                      if (!step4Ref.current.isSaved()) {
                        message.warning('⚠️ 请先保存产品信息');
                        return;
                      }

                      setNextLoading(true);
                      try {
                        await step4Ref.current.submit();
                      } catch (error) {
                        // 错误已在 Step4 中处理
                      } finally {
                        setNextLoading(false);
                      }
                    }}
                    loading={nextLoading}
                  >
                    导出 Excel
                  </Button>
                )}
              </Space>
            </Card>
          </Col>

          {/* 右侧信息卡片 */}
          <Col xs={24} lg={7}>
            <Card title="📊 当前任务" className="sticky top-4">
              {taskData ? (
                <>
                  <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-1">产品概念</p>
                    <p className="text-lg font-semibold">{taskData.concept}</p>
                  </div>

                  <div className="mb-6">
                    <p className="text-sm text-gray-600 mb-1">产品核心词</p>
                    <p className="text-lg font-semibold">{taskData.entity_word}</p>
                  </div>

                  <div className="border-t pt-4">
                    {taskData.metadata && (
                      <Statistic
                        title="生成的属性词"
                        value={taskData.metadata.total_count}
                        className="mb-4"
                        valueStyle={{ color: '#1890ff' }}
                      />
                    )}
                  </div>

                  {taskId && (
                    <div className="mt-6 p-3 bg-green-50 rounded-lg">
                      <p className="text-xs text-green-800">
                        ✅ Task ID: {taskId.slice(0, 8)}...
                      </p>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <p>请先完成步骤1</p>
                </div>
              )}

              <div className="mt-6 p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-blue-800">
                  💡 提示: 您可以随时返回上一步修改选择
                </p>
              </div>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default WizardPage;
