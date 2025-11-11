// ========== 属性词相关类型 ==========

export interface Attribute {
  id: number;
  word: string;
  concept: string;
  type: 'original' | 'synonym' | 'related' | 'variant' | 'custom';
  translation: string;
  use_case: string;
  search_value: 'high' | 'medium' | 'low';
  search_value_stars: number;  // 1-5星
  recommended: boolean;
  source: 'ai' | 'user';
  is_selected: boolean;
  created_at?: string;
}

export interface AttributeMetadata {
  total_count: number;
  type_distribution: {
    original: number;
    synonym: number;
    related: number;
    variant: number;
    custom: number;
  };
  recommended_count: number;
}

// ========== 本体词相关类型 ==========

export interface EntityWord {
  id: number;
  entity_word: string;
  concept: string;
  type: 'original' | 'synonym' | 'variant';
  translation?: string;
  use_case?: string;
  search_value: 'high' | 'medium' | 'low';
  search_value_stars: number;
  recommended: boolean;
  source: 'ai' | 'user';
  is_selected: boolean;
  created_at?: string;
}

export interface EntityWordMetadata {
  total_count: number;
  selected_count: number;
  type_distribution: {
    original: number;
    synonym: number;
    variant: number;
  };
}

// ========== 搜索词相关类型 ==========

export interface SearchTerm {
  id: number;
  term: string;
  attribute_word: string;
  entity_word: string;
  length: number;
  attribute_word_id: number;
  entity_word_id: number;
  created_at?: string;
}

export interface SearchTermMetadata {
  total_count: number;
  attribute_count: number;
  entity_word_count: number;
}

// ========== 任务相关类型 ==========

export type TaskStatus =
  | 'draft'              // 属性词已生成
  | 'selected'           // 属性词已选择
  | 'entity_selected'    // 本体词已选择
  | 'combined'           // 搜索词已生成
  | 'exported';          // 已导出

export interface Task {
  task_id: string;
  concept: string;
  entity_word: string;
  status: TaskStatus;
  sku?: string;
  asin?: string;
  model?: string;
  created_at: string;
  updated_at: string;
}

// ========== API 请求/响应类型 ==========

// Stage 1: 生成属性词
export interface GenerateAttributesRequest {
  concept: string;
  entity_word?: string;
}

export interface GenerateAttributesResponse {
  concept: string;
  entity_word: string;
  task_id: string;
  attributes: Attribute[];
  metadata: AttributeMetadata;
}

// Stage 2: 更新属性词选择
export interface UpdateAttributeSelectionRequest {
  selected_attribute_ids: number[];
  new_attributes: NewAttribute[];
  deleted_attribute_ids: number[];
}

export interface NewAttribute {
  word: string;
  type: string;
  translation: string;
  use_case: string;
  search_value: string;
  search_value_stars: number;
  recommended: boolean;
}

export interface UpdateSelectionResponse {
  message: string;
  selected_count: number;
  added_count: number;
  deleted_count: number;
}

// Stage 2: 获取任务详情
export interface TaskDetailResponse {
  task: Task;
  attributes: Attribute[];
  metadata: AttributeMetadata;
}

// Stage 3: 生成本体词
export interface GenerateEntityWordsResponse {
  message: string;
  entity_words: EntityWord[];
  metadata: EntityWordMetadata;
}

// Stage 3: 更新本体词选择
export interface UpdateEntityWordSelectionRequest {
  selected_ids: number[];
  new_entity_words: NewEntityWord[];
  deleted_ids: number[];
}

export interface NewEntityWord {
  entity_word: string;
  type: string;
  translation?: string;
  use_case?: string;
  search_value: string;
  search_value_stars: number;
  recommended: boolean;
}

// Stage 3: 生成搜索词
export interface GenerateSearchTermsResponse {
  message: string;
  search_terms: SearchTerm[];
  metadata: SearchTermMetadata;
}

// Stage 3: 批量删除搜索词
export interface BatchDeleteSearchTermsRequest {
  search_term_ids: number[];
}

// Stage 4: 保存产品信息
export interface SaveProductInfoRequest {
  task_id: string;
  sku: string;
  asin: string;
  model: string;
}

// Stage 4: 导出
export interface ExportRequest {
  task_id: string;
  daily_budget: number;
  ad_group_default_bid: number;
  keyword_bid: number;
}

// ========== 手机型号枚举 ==========

export type PhoneModel =
  // iPhone 17 系列
  | 'iPhone 17 Pro Max'
  | 'iPhone 17 Pro'
  | 'iPhone 17 Air'
  | 'iPhone 17'
  // iPhone 16 系列
  | 'iPhone 16 Pro Max'
  | 'iPhone 16 Pro'
  | 'iPhone 16 Plus'
  | 'iPhone 16'
  // iPhone 15 系列
  | 'iPhone 15 Pro Max'
  | 'iPhone 15 Pro'
  | 'iPhone 15 Plus'
  | 'iPhone 15'
  // iPhone 14 系列
  | 'iPhone 14 Pro Max'
  | 'iPhone 14 Pro'
  | 'iPhone 14 Plus'
  | 'iPhone 14'
  // iPhone 13 系列
  | 'iPhone 13 Pro Max'
  | 'iPhone 13 Pro'
  | 'iPhone 13'
  | 'iPhone 13 mini'
  // iPhone 12 系列
  | 'iPhone 12 Pro Max'
  | 'iPhone 12 Pro'
  | 'iPhone 12'
  | 'iPhone 12 mini'
  // iPhone 11 系列
  | 'iPhone 11 Pro Max'
  | 'iPhone 11 Pro'
  | 'iPhone 11'
  // iPhone SE 系列
  | 'iPhone SE (2022)'
  | 'iPhone SE (2020)'
  // iPhone XS/XR 系列
  | 'iPhone XS Max'
  | 'iPhone XS'
  | 'iPhone XR';

export const PHONE_MODELS: PhoneModel[] = [
  // iPhone 17 系列 (最新款)
  'iPhone 17 Pro Max',
  'iPhone 17 Pro',
  'iPhone 17 Air',
  'iPhone 17',

  // iPhone 16 系列
  'iPhone 16 Pro Max',
  'iPhone 16 Pro',
  'iPhone 16 Plus',
  'iPhone 16',

  // iPhone 15 系列
  'iPhone 15 Pro Max',
  'iPhone 15 Pro',
  'iPhone 15 Plus',
  'iPhone 15',

  // iPhone 14 系列
  'iPhone 14 Pro Max',
  'iPhone 14 Pro',
  'iPhone 14 Plus',
  'iPhone 14',

  // iPhone 13 系列
  'iPhone 13 Pro Max',
  'iPhone 13 Pro',
  'iPhone 13',
  'iPhone 13 mini',

  // iPhone 12 系列
  'iPhone 12 Pro Max',
  'iPhone 12 Pro',
  'iPhone 12',
  'iPhone 12 mini',

  // iPhone 11 系列
  'iPhone 11 Pro Max',
  'iPhone 11 Pro',
  'iPhone 11',

  // iPhone SE 系列
  'iPhone SE (2022)',
  'iPhone SE (2020)',

  // iPhone XS/XR 系列
  'iPhone XS Max',
  'iPhone XS',
  'iPhone XR',
];
