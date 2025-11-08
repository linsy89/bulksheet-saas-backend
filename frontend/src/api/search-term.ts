import { apiClient } from './client';
import type {
  GenerateSearchTermsResponse,
  BatchDeleteSearchTermsRequest,
  SearchTerm,
} from '../types';

/**
 * 搜索词生成请求参数
 */
export interface SearchTermGenerateRequest {
  options?: {
    max_length?: number;  // 默认80字符
  };
}

/**
 * 搜索词相关 API
 */
export const searchTermApi = {
  /**
   * 生成搜索词（属性词 + 本体词组合）（Stage 3）
   */
  generate: (taskId: string, data: SearchTermGenerateRequest = {}) =>
    apiClient.post<SearchTermGenerateRequest, GenerateSearchTermsResponse>(
      `/api/stage3/tasks/${taskId}/search-terms`,
      data
    ),

  /**
   * 获取搜索词列表（支持分页）（Stage 3）
   */
  getList: (taskId: string, page: number = 1, pageSize: number = 20) =>
    apiClient.get<{ search_terms: SearchTerm[]; total: number }>(
      `/api/stage3/tasks/${taskId}/search-terms?page=${page}&page_size=${pageSize}`
    ),

  /**
   * 批量删除搜索词（Stage 3）
   */
  batchDelete: (taskId: string, data: BatchDeleteSearchTermsRequest) =>
    apiClient.delete<{ message: string; deleted_count: number }>(
      `/api/stage3/tasks/${taskId}/search-terms/batch`,
      { data }
    ),
};
