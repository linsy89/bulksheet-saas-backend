import { apiClient } from './client';
import type {
  GenerateAttributesRequest,
  GenerateAttributesResponse,
  UpdateAttributeSelectionRequest,
  UpdateSelectionResponse,
  TaskDetailResponse,
} from '../types';

/**
 * 属性词相关 API
 */
export const attributeApi = {
  /**
   * 生成属性词（Stage 1）
   */
  generate: (data: GenerateAttributesRequest) =>
    apiClient.post<GenerateAttributesRequest, GenerateAttributesResponse>(
      '/api/stage1/generate',
      data
    ),

  /**
   * 获取任务详情（包含属性词列表）（Stage 2）
   */
  getTaskDetail: (taskId: string) =>
    apiClient.get<TaskDetailResponse>(`/api/stage2/tasks/${taskId}`),

  /**
   * 更新属性词选择状态（Stage 2）
   */
  updateSelection: (taskId: string, data: UpdateAttributeSelectionRequest) =>
    apiClient.put<UpdateAttributeSelectionRequest, UpdateSelectionResponse>(
      `/api/stage2/tasks/${taskId}/selection`,
      data
    ),
};
