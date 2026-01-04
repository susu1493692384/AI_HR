/**
 * API Key Modal Component
 * Generic modal for providers that only need API Key
 * Based on RAGFlow api-key-modal
 */

import React, { useState, useEffect, useCallback } from 'react';
import { LLMFactory, ModelsWithBaseUrl } from '@/constants/llm';
import { LlmIcon } from '@/components/llm';
import Modal from '@/components/common/Modal';
import { ApiKeyPostBody } from '@/interfaces/request/llm';

interface IApiKeyModalProps {
  visible: boolean;
  hideModal: () => void;
  loading: boolean;
  initialValue: string;
  llmFactory: string;
  editMode?: boolean;
  onOk: (postBody: ApiKeyPostBody) => void;
}

type FieldType = {
  api_key?: string;
  base_url?: string;
  group_id?: string;
};

const ApiKeyModal: React.FC<IApiKeyModalProps> = ({
  visible,
  hideModal,
  llmFactory,
  loading,
  initialValue,
  editMode = false,
  onOk,
}) => {
  const [formData, setFormData] = useState<FieldType>({
    api_key: '',
    base_url: '',
    group_id: '',
  });

  useEffect(() => {
    if (visible) {
      setFormData({
        api_key: initialValue,
        base_url: '',
        group_id: '',
      });
    }
  }, [initialValue, visible]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleOk = useCallback(() => {
    if (!formData.api_key?.trim()) {
      return;
    }
    onOk(formData as ApiKeyPostBody);
  }, [formData, onOk]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleOk();
    }
  };

  const showBaseUrl = ModelsWithBaseUrl.some((x) => x === llmFactory);
  const showGroupId = llmFactory === LLMFactory.MiniMax;
  const showBaseUrlForAnthropic = llmFactory.toLowerCase() === 'anthropic';

  const getBaseUrlPlaceholder = () => {
    switch (llmFactory) {
      case LLMFactory.TongYiQianWen:
        return 'https://dashscope.aliyuncs.com/compatible-mode/v1';
      case LLMFactory.MiniMax:
        return 'https://api.minimax.chat/v1';
      default:
        return 'https://api.openai.com/v1';
    }
  };

  const getBaseUrlTooltip = () => {
    switch (llmFactory) {
      case LLMFactory.MiniMax:
        return '如果您使用 MiniMax 的海外服务，请填写 https://api.minimax.chat/v1';
      case LLMFactory.TongYiQianWen:
        return '如果您使用通义千问的兼容模式，请填写此地址';
      default:
        return '自定义 API 地址，如果使用默认地址则无需填写';
    }
  };

  return (
    <Modal
      isOpen={visible}
      onClose={hideModal}
      title={
        <div className="flex items-center space-x-3">
          <LlmIcon name={llmFactory} width={32} />
          <span className="text-lg font-semibold">{llmFactory}</span>
        </div>
      }
      footer={
        <div className="flex justify-end space-x-3">
          <button
            onClick={hideModal}
            disabled={loading}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            取消
          </button>
          <button
            onClick={handleOk}
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? '保存中...' : '保存'}
          </button>
        </div>
      }
    >
      <div className="space-y-4 py-4">
        {/* API Key */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API Key <span className="text-red-500">*</span>
          </label>
          <input
            type="password"
            name="api_key"
            value={formData.api_key}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={editMode ? '留空保持不变' : '请输入 API Key'}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            autoFocus={!editMode}
          />
        </div>

        {/* Base URL */}
        {(showBaseUrl || showBaseUrlForAnthropic) && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
              Base URL (可选)
              <span
                className="ml-2 text-gray-400 cursor-help"
                title={getBaseUrlTooltip()}
              >
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clipRule="evenodd"
                  />
                </svg>
              </span>
            </label>
            <input
              type="text"
              name="base_url"
              value={formData.base_url}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={getBaseUrlPlaceholder()}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}

        {/* Group ID (for MiniMax) */}
        {showGroupId && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Group ID
            </label>
            <input
              type="text"
              name="group_id"
              value={formData.group_id}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="请输入 Group ID"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}
      </div>
    </Modal>
  );
};

export default ApiKeyModal;
