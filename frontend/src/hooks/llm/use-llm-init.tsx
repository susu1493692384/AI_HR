/**
 * LLM Auto-Initialization Hook
 * 自动初始化 LLM 数据的 hook
 */

import { useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import llmService from '@/services/llm';
import { LLM_QUERY_KEYS } from './use-llm-request';

interface InitStatus {
  initialized: boolean;
  factory_count: number;
}

interface UseLlmInitResult {
  isChecking: boolean;
  isInitializing: boolean;
  isInitialized: boolean;
  initRequired: boolean;
  error: string | null;
  backendUnavailable: boolean;
  initialize: () => Promise<void>;
  skipInit: () => void;
}

export const useLlmInit = (): UseLlmInitResult => {
  const [isChecking, setIsChecking] = useState(true);
  const [isInitializing, setIsInitializing] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [initRequired, setInitRequired] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendUnavailable, setBackendUnavailable] = useState(false);

  const queryClient = useQueryClient();

  // Check initialization status
  const checkStatus = async () => {
    try {
      setIsChecking(true);
      setError(null);
      setBackendUnavailable(false);

      const response = await llmService.checkInitStatus();

      if (response.code === 0 && response.data) {
        const { initialized, factory_count } = response.data;
        setIsInitialized(initialized);
        setInitRequired(!initialized || factory_count === 0);
      } else {
        // If API returns error, assume initialization is required
        setInitRequired(true);
      }
    } catch (err: any) {
      console.error('Failed to check LLM init status:', err);
      // Check if it's a network/timeout error
      if (err.code === 'ECONNABORTED' || err.code === 'ERR_NETWORK' || err.message?.includes('timeout')) {
        setBackendUnavailable(true);
        setError('后端服务不可用，请确保后端服务正在运行');
      } else {
        setInitRequired(true);
        setError(err.message || 'Failed to check status');
      }
    } finally {
      setIsChecking(false);
    }
  };

  // Initialize LLM data
  const initialize = async () => {
    try {
      setIsInitializing(true);
      setError(null);
      setBackendUnavailable(false);

      // Get current user ID from localStorage for tenant_id
      const userStr = localStorage.getItem('user');
      const tenantId = userStr ? JSON.parse(userStr).id : 'default-tenant';

      const response = await llmService.initLlmData(tenantId);

      if (response.code === 0) {
        setIsInitialized(true);
        setInitRequired(false);

        // Invalidate queries to refresh data
        queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.factoryList });
        queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmList });
        queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.llmList });
      } else {
        setError(response.message || 'Initialization failed');
      }
    } catch (err: any) {
      console.error('Failed to initialize LLM data:', err);
      if (err.code === 'ECONNABORTED' || err.code === 'ERR_NETWORK' || err.message?.includes('timeout')) {
        setBackendUnavailable(true);
        setError('后端服务不可用，请确保后端服务正在运行');
      } else {
        setError(err.message || 'Initialization failed');
      }
    } finally {
      setIsInitializing(false);
    }
  };

  // Skip initialization and try to load data anyway
  const skipInit = () => {
    setInitRequired(false);
    setBackendUnavailable(false);
    setError(null);
  };

  useEffect(() => {
    checkStatus();
  }, []);

  return {
    isChecking,
    isInitializing,
    isInitialized,
    initRequired,
    error,
    backendUnavailable,
    initialize,
    skipInit,
  };
};
