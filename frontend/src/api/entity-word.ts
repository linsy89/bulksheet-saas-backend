import { apiClient } from './client';
import type {
  EntityWord,
  EntityWordMetadata,
} from '../types';

// 匹配后端API的请求/响应类型
export interface EntityWordGenerateRequest {
  options?: {
    max_count?: number;  // 5-20, 默认15
  };
}

export interface EntityWordGenerateResponse {
  task_id: string;
  entity_words: EntityWord[];
  metadata: EntityWordMetadata;
  status: string;
  updated_at: string;
}

export interface EntityWordSelectionRequest {
  selected_entity_word_ids: number[];
  new_entity_words: Array<{ entity_word: string }>;
  deleted_entity_word_ids: number[];
}

export interface EntityWordSelectionResponse {
  task_id: string;
  status: string;
  updated_at: string;
  metadata: {
    selected_count: number;
    total_count: number;
    changes: {
      selected: number;
      added: number;
      deleted: number;
    };
  };
}

/**
 * 本体词相关 API
 */
export const entityWordApi = {
  /**
   * 生成本体词变体（Stage 3 API 1）
   */
  generate: (taskId: string, data: EntityWordGenerateRequest = {}) =>
    apiClient.post<EntityWordGenerateRequest, EntityWordGenerateResponse>(
      `/api/stage3/tasks/${taskId}/entity-words/generate`,
      data
    ),

  /**
   * 获取本体词列表（Stage 3 API 2）
   */
  getList: (taskId: string, includeDeleted = false) =>
    apiClient.get<{ task_id: string; entity_words: EntityWord[]; metadata: EntityWordMetadata }>(
      `/api/stage3/tasks/${taskId}/entity-words?include_deleted=${includeDeleted}`
    ),

  /**
   * 更新本体词选择状态（Stage 3 API 3）
   */
  updateSelection: (taskId: string, data: EntityWordSelectionRequest) =>
    apiClient.put<EntityWordSelectionRequest, EntityWordSelectionResponse>(
      `/api/stage3/tasks/${taskId}/entity-words/selection`,
      data
    ),
};
