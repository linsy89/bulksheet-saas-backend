import { apiClient } from './client';
import type { SaveProductInfoRequest, ExportRequest } from '../types';

/**
 * 导出相关 API
 */
export const exportApi = {
  /**
   * 保存产品信息（Stage 4）
   */
  saveProductInfo: (data: SaveProductInfoRequest) =>
    apiClient.post<SaveProductInfoRequest, { message: string }>(
      '/api/stage4/save-product-info',
      data
    ),

  /**
   * 导出 Bulksheet Excel 文件（Stage 4）
   */
  export: async (data: ExportRequest): Promise<Blob> => {
    const response = await apiClient.post('/api/stage4/export', data, {
      responseType: 'blob',  // 重要：接收二进制数据
    });
    return response as unknown as Blob;
  },
};
