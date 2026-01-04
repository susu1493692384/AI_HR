/**
 * LLM Request Hooks
 * React Query hooks for LLM model configuration
 * Based on RAGFlow use-llm-request.tsx
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  IAddLlmRequestBody,
  IApiKeySavingParams,
  IDeleteLlmRequestBody,
  ISystemModelSettingSavingParams,
} from '@/interfaces/request/llm';
import {
  IFactory,
  IMyLlmValue,
  IThirdOAIModel,
  IThirdOAIModelCollection,
  ITenantInfo,
} from '@/interfaces/database/llm';
import llmService from '@/services/llm';
import { getRealModelName, buildLlmUuid } from '@/utils/llm-util';

// Query keys
export const LLM_QUERY_KEYS = {
  llmList: ['llmList'] as const,
  myLlmList: ['myLlmList'] as const,
  myLlmListDetailed: ['myLlmListDetailed'] as const,
  factoryList: ['factoryList'] as const,
  tenantInfo: ['tenantInfo'] as const,
} as const;

/**
 * Fetch all available LLM models
 */
export const useFetchLlmList = (modelType?: string) => {
  return useQuery<IThirdOAIModelCollection>({
    queryKey: [...LLM_QUERY_KEYS.llmList, modelType],
    queryFn: async (): Promise<IThirdOAIModelCollection> => {
      const response = await llmService.fetchLlmList({ model_type: modelType });
      // Handle API response format: { code: 0, data: {...} }
      if (response.code === 0) {
        return response.data || {};
      }
      // If data is directly returned (backward compatibility)
      return (response as unknown as IThirdOAIModelCollection) || {};
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Fetch my configured LLM models
 */
export const useFetchMyLlmList = () => {
  return useQuery<Record<string, IMyLlmValue>>({
    queryKey: LLM_QUERY_KEYS.myLlmList,
    queryFn: async (): Promise<Record<string, IMyLlmValue>> => {
      const response = await llmService.fetchMyLlm();
      // Handle API response format: { code: 0, data: {...} }
      if (response.code === 0) {
        return response.data || {};
      }
      // If data is directly returned (backward compatibility)
      return (response as unknown as Record<string, IMyLlmValue>) || {};
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Fetch my configured LLM models with details
 */
export const useFetchMyLlmListDetailed = () => {
  return useQuery<Record<string, IMyLlmValue>>({
    queryKey: LLM_QUERY_KEYS.myLlmListDetailed,
    queryFn: async (): Promise<Record<string, IMyLlmValue>> => {
      const response = await llmService.fetchMyLlm({ include_details: true });
      // Handle API response format: { code: 0, data: {...} }
      if (response.code === 0) {
        return response.data || {};
      }
      // If data is directly returned (backward compatibility)
      return (response as unknown as Record<string, IMyLlmValue>) || {};
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Fetch all available LLM factories
 */
export const useFetchLlmFactoryList = () => {
  return useQuery<IFactory[]>({
    queryKey: LLM_QUERY_KEYS.factoryList,
    queryFn: async (): Promise<IFactory[]> => {
      const response = await llmService.fetchFactoriesList();
      // Handle API response format: { code: 0, data: [...] }
      if (response.code === 0) {
        return response.data || [];
      }
      // If data is directly returned (backward compatibility)
      return (response as unknown as IFactory[]) || [];
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

/**
 * Fetch tenant info (system model settings)
 */
export const useFetchTenantInfo = () => {
  return useQuery<ITenantInfo>({
    queryKey: LLM_QUERY_KEYS.tenantInfo,
    queryFn: async (): Promise<ITenantInfo> => {
      const response = await llmService.fetchTenantInfo();
      // Handle API response format: { code: 0, data: {...} }
      if (response.code === 0) {
        return response.data || {} as ITenantInfo;
      }
      // If data is directly returned (backward compatibility)
      return (response as unknown as ITenantInfo) || {} as ITenantInfo;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * LLM item type with factory info
 */
export type ILlmItem = {
  name: string;
  logo: string;
  llm: Array<{ name: string; type: string; status: '0' | '1'; used_token: number }>;
  tags: string;
};

/**
 * Hook to select and process LLM list data
 */
export const useSelectLlmList = () => {
  const { data: myLlmList, isLoading: myLlmListLoading } = useFetchMyLlmList();
  const { data: factoryList, isLoading: factoryListLoading } = useFetchLlmFactoryList();

  // Provide default empty objects to prevent errors
  const myLlmListSafe: Record<string, IMyLlmValue> = myLlmList ?? {};
  const factoryListSafe: IFactory[] = factoryList ?? [];

  const processedMyLlmList: ILlmItem[] = Object.entries(myLlmListSafe).map(([key, value]) => ({
    name: key,
    logo: factoryListSafe.find((x: IFactory) => x.name === key)?.logo ?? '',
    ...value,
  }));

  const processedFactoryList = factoryListSafe.filter(
    (x: IFactory) => !Object.keys(myLlmListSafe).includes(x.name)
  );

  return {
    myLlmList: processedMyLlmList,
    factoryList: processedFactoryList,
    loading: myLlmListLoading || factoryListLoading,
  };
};

/**
 * Hook to save API key
 */
export const useSaveApiKey = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (params: IApiKeySavingParams) => {
      const response = await llmService.setApiKey(params);
      return response;
    },
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmList });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmListDetailed });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.factoryList });
    },
  });

  return {
    saveApiKey: mutation.mutateAsync,
    loading: mutation.isPending,
  };
};

/**
 * Hook to add LLM model
 */
export const useAddLlm = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (params: IAddLlmRequestBody) => {
      const response = await llmService.addLlm(params);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmList });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmListDetailed });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.factoryList });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.llmList });
    },
  });

  return {
    addLlm: mutation.mutateAsync,
    loading: mutation.isPending,
  };
};

/**
 * Hook to delete LLM model
 */
export const useDeleteLlm = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: IDeleteLlmRequestBody) => {
      const response = await llmService.deleteLlm(params);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmList });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmListDetailed });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.factoryList });
    },
  });
};

/**
 * Hook to enable/disable LLM model
 */
export const useEnableLlm = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: IDeleteLlmRequestBody & { enable: boolean }) => {
      const reqParam: IDeleteLlmRequestBody & { status: string } = {
        llm_factory: params.llm_factory,
        llm_name: params.llm_name,
        status: params.enable ? '1' : '0'
      };
      const response = await llmService.enableLlm(reqParam);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmList });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmListDetailed });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.factoryList });
    },
  });
};

/**
 * Hook to delete factory (all models from a provider)
 */
export const useDeleteFactory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: IDeleteLlmRequestBody) => {
      const response = await llmService.deleteFactory(params);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmList });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.myLlmListDetailed });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.factoryList });
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.llmList });
    },
  });
};

/**
 * Hook to save tenant info (system model settings)
 */
export const useSaveTenantInfo = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (params: ISystemModelSettingSavingParams) => {
      const response = await llmService.setTenantInfo(params);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LLM_QUERY_KEYS.tenantInfo });
    },
  });

  return {
    saveTenantInfo: mutation.mutateAsync,
    loading: mutation.isPending,
  };
};

/**
 * Helper function to build LLM options for select dropdown
 */
export const buildLlmOptions = (models: IThirdOAIModel[]) => {
  return models.map((model) => ({
    label: getRealModelName(model.llm_name),
    value: buildLlmUuid(model),
    disabled: !model.available,
  }));
};

/**
 * Build LLM option with icon (for display)
 */
function buildLlmOptionsWithIcon(x: IThirdOAIModel) {
  return {
    label: getRealModelName(x.llm_name),
    value: `${x.llm_name}@${x.fid}`,
    disabled: !x.available,
    is_tools: x.is_tools,
  };
}

/**
 * Build LLM option from my_llm detailed data
 */
function buildLlmOptionFromMyLlm(x: any) {
  return {
    label: getRealModelName(x.name),
    value: `${x.name}@${x.factory || x.fid}`,
    disabled: x.status !== '1',
    is_tools: x.is_tools || false,
  };
}

/**
 * Hook to select LLM options grouped by model type
 * Returns options for system model settings dropdown
 * Uses my_llms (configured models) instead of all available models
 */
export const useSelectLlmOptionsByModelType = () => {
  // Use my_llms detailed to get only configured models
  const { data: myLlmListDetailed } = useFetchMyLlmListDetailed();

  // Group options by model type
  const groupOptionsByModelType = (modelType: string) => {
    if (!myLlmListDetailed) return [];

    return Object.entries(myLlmListDetailed)
      .map(([factory, data]: [string, any]) => {
        return {
          label: factory,
          options: (data.llm || [])
            .filter((x: any) => {
              const matchesType = modelType
                ? x.type === modelType || x.model_type === modelType
                : true;
              const isEnabled = x.status === '1';
              return matchesType && isEnabled;
            })
            .map((x: any) => buildLlmOptionFromMyLlm({ ...x, factory })),
        };
      })
      .filter((x: any) => x.options.length > 0);
  };

  return {
    chat: groupOptionsByModelType('chat'),
    embedding: groupOptionsByModelType('embedding'),
    image2text: groupOptionsByModelType('image2text'),
    speech2text: groupOptionsByModelType('speech2text'),
    rerank: groupOptionsByModelType('rerank'),
    tts: groupOptionsByModelType('tts'),
    ocr: groupOptionsByModelType('ocr'),
  };
};

/**
 * Compose LLM options by multiple model types
 * Merges different types of models from the same manufacturer
 */
export const useComposeLlmOptionsByModelTypes = (modelTypes: string[]) => {
  const allOptions = useSelectLlmOptionsByModelType();

  return modelTypes.reduce<any[]>((pre, cur) => {
    const options = allOptions[cur as keyof typeof allOptions];
    if (!options) return pre;

    options.forEach((x: any) => {
      const item = pre.find((y: any) => y.label === x.label);
      if (item) {
        x.options.forEach((y: any) => {
          if (!item.options.some((z: any) => z.value === y.value)) {
            item.options.push(y);
          }
        });
      } else {
        pre.push(x);
      }
    });

    return pre;
  }, []);
};
