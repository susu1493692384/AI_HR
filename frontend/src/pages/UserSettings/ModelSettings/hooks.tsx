/**
 * Model Settings Page Hooks
 * Custom hooks for model configuration page
 * Based on RAGFlow setting-model/hooks.tsx
 */

import { useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { LLMFactory } from '@/constants/llm';
import {
  IAddLlmRequestBody,
  IApiKeySavingParams,
  ISystemModelSettingSavingParams,
} from '@/interfaces/request/llm';
import { ApiKeyPostBody } from '@/interfaces/request/llm';
import {
  useAddLlm,
  useDeleteLlm,
  useDeleteFactory,
  useEnableLlm,
  useSaveApiKey,
  useSaveTenantInfo,
  useFetchTenantInfo,
  useSelectLlmOptionsByModelType,
  useComposeLlmOptionsByModelTypes as _useComposeLlmOptionsByModelTypes,
} from '@/hooks/llm/use-llm-request';
import { getRealModelName } from '@/utils/llm-util';

// Re-export for convenience
export const useComposeLlmOptionsByModelTypes = _useComposeLlmOptionsByModelTypes;

/**
 * Hook for API Key modal
 */
export const useSubmitApiKey = () => {
  const [savingParams, setSavingParams] = useState<
    Omit<IApiKeySavingParams, 'api_key'>
  >({ llm_factory: '' } as Omit<IApiKeySavingParams, 'api_key'>);
  const [editMode, setEditMode] = useState(false);
  const { saveApiKey, loading } = useSaveApiKey();
  const [apiKeyVisible, setApiKeyVisible] = useState(false);

  const queryClient = useQueryClient();

  const onApiKeySavingOk = useCallback(
    async (postBody: ApiKeyPostBody) => {
      const ret = await saveApiKey({
        ...savingParams,
        ...postBody,
      });

      if (ret.code === 0) {
        queryClient.invalidateQueries({ queryKey: ['llmList'] });
        setApiKeyVisible(false);
        setEditMode(false);
      }
    },
    [saveApiKey, savingParams, queryClient]
  );

  const onShowApiKeyModal = useCallback(
    (params: Omit<IApiKeySavingParams, 'api_key'>, isEdit = false) => {
      setSavingParams(params);
      setEditMode(isEdit);
      setApiKeyVisible(true);
    },
    [setSavingParams]
  );

  return {
    saveApiKeyLoading: loading,
    initialApiKey: '',
    llmFactory: savingParams.llm_factory,
    editMode,
    onApiKeySavingOk,
    apiKeyVisible,
    hideApiKeyModal: () => setApiKeyVisible(false),
    showApiKeyModal: onShowApiKeyModal,
  };
};

/**
 * Hook to fetch system model setting options on mount
 */
export const useFetchSystemModelSettingOnMount = () => {
  const { data: systemSetting } = useFetchTenantInfo();
  const allOptions = useSelectLlmOptionsByModelType();

  return { systemSetting, allOptions };
};

/**
 * Hook for system model settings
 */
export const useSubmitSystemModelSetting = () => {
  const { data: systemSetting } = useFetchTenantInfo();
  const { saveTenantInfo, loading } = useSaveTenantInfo();
  const [systemSettingVisible, setSystemSettingVisible] = useState(false);

  const onSystemSettingSavingOk = useCallback(
    async (
      payload: Omit<ISystemModelSettingSavingParams, 'tenant_id' | 'name'>
    ) => {
      const ret = await saveTenantInfo({
        tenant_id: systemSetting?.tenant_id || '',
        name: systemSetting?.name,
        ...payload,
      });

      if (ret.code === 0) {
        setSystemSettingVisible(false);
      }
    },
    [saveTenantInfo, systemSetting]
  );

  return {
    saveSystemModelSettingLoading: loading,
    onSystemSettingSavingOk,
    systemSettingVisible,
    hideSystemSettingModal: () => setSystemSettingVisible(false),
    showSystemSettingModal: () => setSystemSettingVisible(true),
  };
};

/**
 * Hook for local LLM (Ollama, Xinference, etc.)
 */
export const useSubmitOllama = () => {
  const [selectedLlmFactory, setSelectedLlmFactory] = useState<string>('');
  const [editMode, setEditMode] = useState(false);
  const [initialValues, setInitialValues] = useState<
    Partial<IAddLlmRequestBody> | undefined
  >();
  const { addLlm, loading } = useAddLlm();
  const [llmAddingVisible, setLlmAddingVisible] = useState(false);

  const onLlmAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const cleanedPayload: IAddLlmRequestBody = { ...payload };
      if (
        !cleanedPayload.api_key ||
        cleanedPayload.api_key.toString().trim() === ''
      ) {
        (cleanedPayload as any).api_key = undefined;
      }

      const ret = await addLlm(cleanedPayload);
      if (ret.code === 0) {
        setLlmAddingVisible(false);
        setEditMode(false);
        setInitialValues(undefined);
      }
    },
    [addLlm]
  );

  const handleShowLlmAddingModal = useCallback(
    (
      llmFactory: string,
      isEdit = false,
      _modelData?: any,
      detailedData?: any
    ) => {
      setSelectedLlmFactory(llmFactory);
      setEditMode(isEdit);

      if (isEdit && detailedData) {
        const initialVals = {
          llm_name: getRealModelName(detailedData.name),
          model_type: detailedData.type,
          api_base: detailedData.api_base || '',
          max_tokens: detailedData.max_tokens || 8192,
          api_key: '',
        };
        setInitialValues(initialVals);
      } else {
        setInitialValues(undefined);
      }
      setLlmAddingVisible(true);
    },
    []
  );

  return {
    llmAddingLoading: loading,
    editMode,
    initialValues,
    onLlmAddingOk,
    llmAddingVisible,
    hideLlmAddingModal: () => setLlmAddingVisible(false),
    showLlmAddingModal: handleShowLlmAddingModal,
    selectedLlmFactory,
  };
};

/**
 * Hook for Volc Engine
 */
export const useSubmitVolcEngine = () => {
  const { addLlm, loading } = useAddLlm();
  const [volcAddingVisible, setVolcAddingVisible] = useState(false);

  const onVolcAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const ret = await addLlm(payload);
      if (ret.code === 0) {
        setVolcAddingVisible(false);
      }
    },
    [addLlm]
  );

  return {
    volcAddingLoading: loading,
    onVolcAddingOk,
    volcAddingVisible,
    hideVolcAddingModal: () => setVolcAddingVisible(false),
    showVolcAddingModal: () => setVolcAddingVisible(true),
  };
};

/**
 * Hook for Tencent Hunyuan
 */
export const useSubmitHunyuan = () => {
  const { addLlm, loading } = useAddLlm();
  const [HunyuanAddingVisible, setHunyuanAddingVisible] = useState(false);

  const onHunyuanAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const ret = await addLlm(payload);
      if (ret.code === 0) {
        setHunyuanAddingVisible(false);
      }
    },
    [addLlm]
  );

  return {
    HunyuanAddingLoading: loading,
    onHunyuanAddingOk,
    HunyuanAddingVisible,
    hideHunyuanAddingModal: () => setHunyuanAddingVisible(false),
    showHunyuanAddingModal: () => setHunyuanAddingVisible(true),
  };
};

/**
 * Hook for Google Cloud
 */
export const useSubmitGoogle = () => {
  const { addLlm, loading } = useAddLlm();
  const [GoogleAddingVisible, setGoogleAddingVisible] = useState(false);

  const onGoogleAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const ret = await addLlm(payload);
      if (ret.code === 0) {
        setGoogleAddingVisible(false);
      }
    },
    [addLlm]
  );

  return {
    GoogleAddingLoading: loading,
    onGoogleAddingOk,
    GoogleAddingVisible,
    hideGoogleAddingModal: () => setGoogleAddingVisible(false),
    showGoogleAddingModal: () => setGoogleAddingVisible(true),
  };
};

/**
 * Hook for Tencent Cloud
 */
export const useSubmitTencentCloud = () => {
  const { addLlm, loading } = useAddLlm();
  const [TencentCloudAddingVisible, setTencentCloudAddingVisible] = useState(false);

  const onTencentCloudAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const ret = await addLlm(payload);
      if (ret.code === 0) {
        setTencentCloudAddingVisible(false);
      }
    },
    [addLlm]
  );

  return {
    TencentCloudAddingLoading: loading,
    onTencentCloudAddingOk,
    TencentCloudAddingVisible,
    hideTencentCloudAddingModal: () => setTencentCloudAddingVisible(false),
    showTencentCloudAddingModal: () => setTencentCloudAddingVisible(true),
  };
};

/**
 * Hook for XunFei Spark
 */
export const useSubmitSpark = () => {
  const { addLlm, loading } = useAddLlm();
  const [SparkAddingVisible, setSparkAddingVisible] = useState(false);

  const onSparkAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const ret = await addLlm(payload);
      if (ret.code === 0) {
        setSparkAddingVisible(false);
      }
    },
    [addLlm]
  );

  return {
    SparkAddingLoading: loading,
    onSparkAddingOk,
    SparkAddingVisible,
    hideSparkAddingModal: () => setSparkAddingVisible(false),
    showSparkAddingModal: () => setSparkAddingVisible(true),
  };
};

/**
 * Hook for Baidu Yiyan
 */
export const useSubmityiyan = () => {
  const { addLlm, loading } = useAddLlm();
  const [yiyanAddingVisible, setyiyanAddingVisible] = useState(false);

  const onyiyanAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const ret = await addLlm(payload);
      if (ret.code === 0) {
        setyiyanAddingVisible(false);
      }
    },
    [addLlm]
  );

  return {
    yiyanAddingLoading: loading,
    onyiyanAddingOk,
    yiyanAddingVisible,
    hideyiyanAddingModal: () => setyiyanAddingVisible(false),
    showyiyanAddingModal: () => setyiyanAddingVisible(true),
  };
};

/**
 * Hook for Fish Audio
 */
export const useSubmitFishAudio = () => {
  const { addLlm, loading } = useAddLlm();
  const [FishAudioAddingVisible, setFishAudioAddingVisible] = useState(false);

  const onFishAudioAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const ret = await addLlm(payload);
      if (ret.code === 0) {
        setFishAudioAddingVisible(false);
      }
    },
    [addLlm]
  );

  return {
    FishAudioAddingLoading: loading,
    onFishAudioAddingOk,
    FishAudioAddingVisible,
    hideFishAudioAddingModal: () => setFishAudioAddingVisible(false),
    showFishAudioAddingModal: () => setFishAudioAddingVisible(true),
  };
};

/**
 * Hook for Bedrock
 */
export const useSubmitBedrock = () => {
  const { addLlm, loading } = useAddLlm();
  const [bedrockAddingVisible, setBedrockAddingVisible] = useState(false);

  const onBedrockAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const ret = await addLlm(payload);
      if (ret.code === 0) {
        setBedrockAddingVisible(false);
      }
    },
    [addLlm]
  );

  return {
    bedrockAddingLoading: loading,
    onBedrockAddingOk,
    bedrockAddingVisible,
    hideBedrockAddingModal: () => setBedrockAddingVisible(false),
    showBedrockAddingModal: () => setBedrockAddingVisible(true),
  };
};

/**
 * Hook for Azure OpenAI
 */
export const useSubmitAzure = () => {
  const { addLlm, loading } = useAddLlm();
  const [AzureAddingVisible, setAzureAddingVisible] = useState(false);

  const onAzureAddingOk = useCallback(
    async (payload: IAddLlmRequestBody) => {
      const ret = await addLlm(payload);
      if (ret.code === 0) {
        setAzureAddingVisible(false);
      }
    },
    [addLlm]
  );

  return {
    AzureAddingLoading: loading,
    onAzureAddingOk,
    AzureAddingVisible,
    hideAzureAddingModal: () => setAzureAddingVisible(false),
    showAzureAddingModal: () => setAzureAddingVisible(true),
  };
};

/**
 * Hook for MinerU
 */
export const useSubmitMinerU = () => {
  const { addLlm, loading } = useAddLlm();
  const [mineruVisible, setMineruVisible] = useState(false);

  const onMineruOk = useCallback(
    async (payload: any) => {
      const cfg: any = {
        ...payload,
        mineru_delete_output: payload.mineru_delete_output ?? true ? '1' : '0',
      };
      if (payload.mineru_backend !== 'vlm-http-client') {
        delete cfg.mineru_server_url;
      }
      const req: IAddLlmRequestBody = {
        llm_factory: LLMFactory.MinerU,
        llm_name: payload.llm_name,
        model_type: 'ocr',
        api_key: cfg,
        api_base: '',
        max_tokens: 0,
      };
      const ret = await addLlm(req);
      if (ret.code === 0) {
        setMineruVisible(false);
      }
    },
    [addLlm]
  );

  return {
    mineruVisible,
    hideMineruModal: () => setMineruVisible(false),
    showMineruModal: () => setMineruVisible(true),
    onMineruOk,
    mineruLoading: loading,
  };
};

/**
 * Hook to handle delete LLM
 */
export const useHandleDeleteLlm = (llmFactory: string) => {
  const deleteLlmMutation = useDeleteLlm();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [pendingDeleteName, setPendingDeleteName] = useState<string>('');

  const handleDeleteLlm = (name: string) => {
    setPendingDeleteName(name);
    setShowDeleteConfirm(true);
  };

  const onConfirmDelete = async () => {
    await deleteLlmMutation.mutateAsync({ llm_factory: llmFactory, llm_name: pendingDeleteName });
    setShowDeleteConfirm(false);
    setPendingDeleteName('');
  };

  return { handleDeleteLlm, showDeleteConfirm, setShowDeleteConfirm, onConfirmDelete };
};

/**
 * Hook to handle enable LLM
 */
export const useHandleEnableLlm = (llmFactory: string) => {
  const enableLlmMutation = useEnableLlm();

  const handleEnableLlm = async (name: string, enable: boolean) => {
    await enableLlmMutation.mutateAsync({
      llm_factory: llmFactory,
      llm_name: name,
      enable
    });
  };

  return { handleEnableLlm };
};

/**
 * Hook to handle delete factory
 */
export const useHandleDeleteFactory = (llmFactory: string) => {
  const deleteFactoryMutation = useDeleteFactory();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleDeleteFactory = () => {
    setShowDeleteConfirm(true);
  };

  const onConfirmDelete = async () => {
    await deleteFactoryMutation.mutateAsync({ llm_factory: llmFactory, llm_name: '' });
    setShowDeleteConfirm(false);
  };

  return {
    handleDeleteFactory,
    showDeleteConfirm,
    setShowDeleteConfirm,
    onConfirmDelete,
  };
};
