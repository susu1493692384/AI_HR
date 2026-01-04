/**
 * Model Settings Page
 * Main component for LLM model configuration
 * Based on RAGFlow setting-model/index.tsx
 */

import React, { useCallback, useMemo, useEffect } from 'react';
import { LLMFactory } from '@/constants/llm';
import { isLocalLlmFactory } from '@/utils/llm-util';
import { ILlmItem } from '@/hooks/llm/use-llm-request';
import { useFetchMyLlmListDetailed, useSelectLlmList, useDeleteFactory, useEnableLlm } from '@/hooks/llm/use-llm-request';
import { useLlmInit } from '@/hooks/llm/use-llm-init';
import {
  useSubmitApiKey,
  useSubmitSystemModelSetting,
  useSubmitOllama,
} from './hooks';
import SystemSetting from './components/SystemSetting';
import UsedModel from './components/UsedModel';
import AvailableModels from './components/AvailableModels';
import ApiKeyModal from './modal/ApiKeyModal';
import OllamaModal from './modal/OllamaModal';

const ModelSettings: React.FC = () => {
  // Auto-initialization hook
  const { isChecking, isInitializing, initRequired, error: initError, backendUnavailable, initialize, skipInit } = useLlmInit();

  // Fetch real data from API
  const { myLlmList, factoryList, loading } = useSelectLlmList();
  const { data: detailedLlmList } = useFetchMyLlmListDetailed();

  // Debug: log myLlmList to see what models are loaded
  console.log('myLlmList:', myLlmList);
  console.log('detailedLlmList:', detailedLlmList);

  // Convert detailedLlmList to ILlmItem format for display
  const myLlmListFromDetailed: ILlmItem[] = useMemo(() => {
    if (!detailedLlmList) return [];
    return Object.entries(detailedLlmList).map(([key, value]: [string, any]) => ({
      name: key,
      logo: factoryList.find((f: any) => f.name === key)?.logo ?? '',
      tags: value.tags || '',
      llm: value.llm || []
    }));
  }, [detailedLlmList, factoryList]);

  // Delete factory and enable LLM mutations
  const deleteFactoryMutation = useDeleteFactory();
  const enableLlmMutation = useEnableLlm();

  // System settings hook
  const { saveSystemModelSettingLoading, onSystemSettingSavingOk } =
    useSubmitSystemModelSetting();

  // API Key modal hook
  const {
    saveApiKeyLoading,
    initialApiKey,
    llmFactory,
    editMode,
    onApiKeySavingOk,
    apiKeyVisible,
    hideApiKeyModal,
    showApiKeyModal,
  } = useSubmitApiKey();

  // Ollama/Local LLM modal hook
  const {
    llmAddingVisible,
    hideLlmAddingModal,
    showLlmAddingModal,
    onLlmAddingOk,
    llmAddingLoading,
    editMode: llmEditMode,
    initialValues: llmInitialValues,
    selectedLlmFactory,
  } = useSubmitOllama();

  // Auto-initialize if required
  useEffect(() => {
    if (initRequired && !isInitializing) {
      initialize();
    }
  }, [initRequired, isInitializing, initialize]);

  // Modal map for special providers
  const ModalMap = useMemo(
    () => ({
      [LLMFactory.Bedrock]: () => console.log('Show Bedrock modal'),
      [LLMFactory.VolcEngine]: () => console.log('Show VolcEngine modal'),
      [LLMFactory.TencentHunYuan]: () => console.log('Show Hunyuan modal'),
      [LLMFactory.XunFeiSpark]: () => console.log('Show Spark modal'),
      [LLMFactory.BaiduYiYan]: () => console.log('Show Yiyan modal'),
      [LLMFactory.FishAudio]: () => console.log('Show Fish Audio modal'),
      [LLMFactory.TencentCloud]: () => console.log('Show Tencent Cloud modal'),
      [LLMFactory.GoogleCloud]: () => console.log('Show Google modal'),
      [LLMFactory.AzureOpenAI]: () => console.log('Show Azure modal'),
      [LLMFactory.MinerU]: () => console.log('Show MinerU modal'),
    }),
    []
  );

  // Handle add model - determines which modal to show
  const handleAddModel = useCallback(
    (llmFactory: string) => {
      console.log('handleAddModel', llmFactory);
      if (isLocalLlmFactory(llmFactory)) {
        showLlmAddingModal(llmFactory);
      } else if (llmFactory in ModalMap) {
        // Show special modal for specific providers
        ModalMap[llmFactory as keyof typeof ModalMap]();
      } else {
        // Show generic API Key modal
        showApiKeyModal({ llm_factory: llmFactory });
      }
    },
    [showApiKeyModal, showLlmAddingModal, ModalMap]
  );

  // Handle edit model
  const handleEditModel = useCallback(
    (model: any, factory: ILlmItem) => {
      if (factory) {
        const detailedFactory = detailedLlmList?.[factory.name];
        const detailedModel = detailedFactory?.llm?.find(
          (m: any) => m.name === model.name
        );

        const editData = {
          llm_factory: factory.name,
          llm_name: model.name,
          model_type: model.type,
        };

        if (isLocalLlmFactory(factory.name)) {
          showLlmAddingModal(factory.name, true, editData, detailedModel);
        } else if (factory.name in ModalMap) {
          ModalMap[factory.name as keyof typeof ModalMap]();
        } else {
          showApiKeyModal(editData, true);
        }
      }
    },
    [showApiKeyModal, showLlmAddingModal, ModalMap, detailedLlmList]
  );

  // Handle delete factory
  const handleDeleteFactory = useCallback(
    async (factory: string) => {
      await deleteFactoryMutation.mutateAsync({ llm_factory: factory, llm_name: '' });
    },
    [deleteFactoryMutation]
  );

  // Handle enable/disable LLM
  const handleEnableLlm = useCallback(
    async (factory: string, modelName: string, enabled: boolean) => {
      await enableLlmMutation.mutateAsync({
        llm_factory: factory,
        llm_name: modelName,
        enable: enabled
      });
    },
    [enableLlmMutation]
  );

  // Loading states
  if (isChecking || isInitializing) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <div className="text-gray-600">
          {isInitializing ? '正在初始化模型数据...' : '检查系统状态...'}
        </div>
        <div className="w-48 h-1 bg-gray-200 rounded-full overflow-hidden">
          <div className="h-full bg-blue-500 animate-pulse" style={{ width: '60%' }}></div>
        </div>
      </div>
    );
  }

  // Error state
  if (initError && !factoryList.length) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <div className="text-red-500">{initError}</div>
        <div className="flex gap-2">
          <button
            onClick={initialize}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            重试
          </button>
          {backendUnavailable && (
            <button
              onClick={skipInit}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              跳过初始化
            </button>
          )}
        </div>
      </div>
    );
  }

  // Normal loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="flex w-full border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
      <div className="flex flex-col lg:flex-row w-full">
        {/* Left Section - System Settings & Used Models */}
        <section className="flex flex-col gap-4 lg:w-3/5 px-5 py-4 border-r border-gray-200 overflow-auto bg-white">
          <SystemSetting
            onOk={onSystemSettingSavingOk}
            loading={saveSystemModelSettingLoading}
          />
          <UsedModel
            myLlmList={myLlmListFromDetailed}
            handleAddModel={handleAddModel}
            handleEditModel={handleEditModel}
            handleDeleteFactory={handleDeleteFactory}
            handleEnableLlm={handleEnableLlm}
          />
        </section>

        {/* Right Section - Available Models */}
        <section className="lg:w-2/5 overflow-auto bg-gray-50">
          <AvailableModels
            factoryList={factoryList}
            handleAddModel={handleAddModel}
          />
        </section>
      </div>

      {/* API Key Modal */}
      <ApiKeyModal
        visible={apiKeyVisible}
        hideModal={hideApiKeyModal}
        loading={saveApiKeyLoading}
        initialValue={initialApiKey}
        editMode={editMode}
        onOk={onApiKeySavingOk}
        llmFactory={llmFactory}
      />

      {/* Ollama/Local LLM Modal */}
      <OllamaModal
        visible={llmAddingVisible}
        hideModal={hideLlmAddingModal}
        onOk={onLlmAddingOk}
        loading={llmAddingLoading}
        editMode={llmEditMode}
        initialValues={llmInitialValues}
        llmFactory={selectedLlmFactory}
      />
    </div>
  );
};

export default ModelSettings;
