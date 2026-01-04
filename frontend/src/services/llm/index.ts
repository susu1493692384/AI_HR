/**
 * LLM Service
 * API service for LLM model configuration
 * 连接到后端 AI HR 系统 API
 */

import { api } from '@/services/api';
import type { AxiosResponse } from 'axios';
import {
  IAddLlmRequestBody,
  IApiKeySavingParams,
  IDeleteLlmRequestBody,
  ILlmListParams,
  ISystemModelSettingSavingParams,
} from '@/interfaces/request/llm';
import {
  IFactory,
  IMyLlmValue,
  IResponse,
  IThirdOAIModelCollection,
  ITenantInfo,
} from '@/interfaces/database/llm';

// LLM API 路径
const LLM_API_PATHS = {
  // Get all available LLM models
  llmList: '/llm/list',
  // Get my configured LLM models
  myLlm: '/llm/my_llms',
  // Get all available LLM factories
  factoriesList: '/llm/factories',
  // Set API key for a provider
  setApiKey: '/llm/set_api_key',
  // Add a new LLM model
  addLlm: '/llm/add_llm',
  // Delete an LLM model
  deleteLlm: '/llm/delete_llm',
  // Enable/disable an LLM model
  enableLlm: '/llm/enable_llm',
  // Delete a factory (all models from a provider)
  deleteFactory: '/llm/delete_factory',
  // Get tenant info (system model settings)
  tenantInfo: '/llm/tenant_info',
  // Set tenant info (system model settings)
  setTenantInfo: '/llm/set_tenant_info',
  // Check init status
  checkInitStatus: '/llm-init/check-init-status',
  // Initialize LLM data
  initLlmData: '/llm-init/init-llm-data',
};

/**
 * Get all available LLM models
 */
export const fetchLlmList = async (params?: ILlmListParams) => {
  const response: AxiosResponse<IResponse<IThirdOAIModelCollection>> = await api.get(
    LLM_API_PATHS.llmList,
    { params }
  );
  return response.data;
};

/**
 * Get my configured LLM models
 */
export const fetchMyLlm = async (params?: { include_details?: boolean }) => {
  const response: AxiosResponse<IResponse<Record<string, IMyLlmValue>>> = await api.get(
    LLM_API_PATHS.myLlm,
    { params }
  );
  return response.data;
};

/**
 * Get all available LLM factories
 */
export const fetchFactoriesList = async () => {
  const response: AxiosResponse<IResponse<IFactory[]>> = await api.get(LLM_API_PATHS.factoriesList);
  return response.data;
};

/**
 * Set API key for a provider
 */
export const setApiKey = async (params: IApiKeySavingParams) => {
  const response: AxiosResponse<IResponse<number>> = await api.post(LLM_API_PATHS.setApiKey, params);
  return response.data;
};

/**
 * Add a new LLM model
 */
export const addLlm = async (params: IAddLlmRequestBody) => {
  const response: AxiosResponse<IResponse<number>> = await api.post(LLM_API_PATHS.addLlm, params);
  return response.data;
};

/**
 * Delete an LLM model
 */
export const deleteLlm = async (params: IDeleteLlmRequestBody) => {
  const response: AxiosResponse<IResponse<number>> = await api.post(LLM_API_PATHS.deleteLlm, params);
  return response.data;
};

/**
 * Enable/disable an LLM model
 */
export const enableLlm = async (params: IDeleteLlmRequestBody & { status?: string }) => {
  const response: AxiosResponse<IResponse<number>> = await api.post(LLM_API_PATHS.enableLlm, params);
  return response.data;
};

/**
 * Delete a factory (all models from a provider)
 */
export const deleteFactory = async (params: IDeleteLlmRequestBody) => {
  const response: AxiosResponse<IResponse<number>> = await api.post(LLM_API_PATHS.deleteFactory, params);
  return response.data;
};

/**
 * Get tenant info (system model settings)
 */
export const fetchTenantInfo = async () => {
  const response: AxiosResponse<IResponse<ITenantInfo>> = await api.get(LLM_API_PATHS.tenantInfo);
  return response.data;
};

/**
 * Set tenant info (system model settings)
 */
export const setTenantInfo = async (params: ISystemModelSettingSavingParams) => {
  const response: AxiosResponse<IResponse<number>> = await api.post(LLM_API_PATHS.setTenantInfo, params);
  return response.data;
};

/**
 * Check LLM initialization status
 */
export const checkInitStatus = async () => {
  const response: AxiosResponse<IResponse<{ initialized: boolean; factory_count: number }>> = await api.get(LLM_API_PATHS.checkInitStatus);
  return response.data;
};

/**
 * Initialize LLM data
 */
export const initLlmData = async (tenantId: string = 'default-tenant') => {
  const response: AxiosResponse<IResponse<{ tenant_id: string }>> = await api.post(`${LLM_API_PATHS.initLlmData}?tenant_id=${tenantId}`);
  return response.data;
};

// Export as default service object
const llmService = {
  fetchLlmList,
  fetchMyLlm,
  fetchFactoriesList,
  setApiKey,
  addLlm,
  deleteLlm,
  enableLlm,
  deleteFactory,
  fetchTenantInfo,
  setTenantInfo,
  checkInitStatus,
  initLlmData,
};

export default llmService;
