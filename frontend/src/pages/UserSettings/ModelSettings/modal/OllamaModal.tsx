/**
 * Ollama / Local LLM Modal Component
 * Modal for adding local LLM models (Ollama, Xinference, etc.)
 * Based on RAGFlow ollama-modal
 */

import React, { useState, useEffect, useCallback } from 'react';
import { LLMFactory } from '@/constants/llm';
import { LlmIcon } from '@/components/llm';
import Modal from '@/components/common/Modal';
import { IAddLlmRequestBody } from '@/interfaces/request/llm';

interface IOllamaModalProps {
  visible: boolean;
  hideModal: () => void;
  loading: boolean;
  llmFactory: string;
  editMode?: boolean;
  initialValues?: Partial<IAddLlmRequestBody>;
  onOk: (payload: IAddLlmRequestBody) => void;
}

type FieldType = IAddLlmRequestBody & {
  vision: boolean;
};

const OllamaModal: React.FC<IOllamaModalProps> = ({
  visible,
  hideModal,
  llmFactory,
  loading,
  editMode = false,
  initialValues,
  onOk,
}) => {
  const [formData, setFormData] = useState<FieldType>({
    llm_factory: llmFactory,
    llm_name: '',
    model_type: 'chat',
    api_base: '',
    api_key: '',
    max_tokens: 8192,
    vision: false,
  });

  useEffect(() => {
    if (visible && editMode && initialValues) {
      setFormData({
        llm_factory: llmFactory,
        llm_name: initialValues.llm_name || '',
        model_type: initialValues.model_type || 'chat',
        api_base: initialValues.api_base || '',
        api_key: '',
        max_tokens: initialValues.max_tokens || 8192,
        vision: false,
      });
    } else if (visible && !editMode) {
      setFormData({
        llm_factory: llmFactory,
        llm_name: '',
        model_type: 'chat',
        api_base: '',
        api_key: '',
        max_tokens: 8192,
        vision: false,
      });
    }
  }, [visible, editMode, initialValues, llmFactory]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value,
    }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData((prev) => ({ ...prev, [name]: checked }));
  };

  const handleOk = useCallback(() => {
    const modelType =
      formData.model_type === 'chat' && formData.vision
        ? 'image2text'
        : formData.model_type;

    const data: IAddLlmRequestBody = {
      ...formData,
      model_type: modelType,
      llm_factory: llmFactory,
      max_tokens: formData.max_tokens,
    };

    onOk(data);
  }, [formData, llmFactory, onOk]);

  const getOptions = () => {
    const optionsMap: Record<string, Array<{ value: string; label: string }>> = {
      'HuggingFace': [
        { value: 'embedding', label: 'Embedding' },
        { value: 'chat', label: 'Chat' },
        { value: 'rerank', label: 'Rerank' },
      ],
      'LM-Studio': [
        { value: 'chat', label: 'Chat' },
        { value: 'embedding', label: 'Embedding' },
        { value: 'image2text', label: 'Image2Text' },
      ],
      'Xinference': [
        { value: 'chat', label: 'Chat' },
        { value: 'embedding', label: 'Embedding' },
        { value: 'rerank', label: 'Rerank' },
        { value: 'image2text', label: 'Image2Text' },
        { value: 'speech2text', label: 'Speech2Text' },
        { value: 'tts', label: 'TTS' },
      ],
      'ModelScope': [{ value: 'chat', label: 'Chat' }],
      'GPUStack': [
        { value: 'chat', label: 'Chat' },
        { value: 'embedding', label: 'Embedding' },
        { value: 'rerank', label: 'Rerank' },
        { value: 'speech2text', label: 'Speech2Text' },
        { value: 'tts', label: 'TTS' },
      ],
      'OpenRouter': [
        { value: 'chat', label: 'Chat' },
        { value: 'image2text', label: 'Image2Text' },
      ],
      'Ollama': [
        { value: 'chat', label: 'Chat' },
        { value: 'embedding', label: 'Embedding' },
        { value: 'rerank', label: 'Rerank' },
        { value: 'image2text', label: 'Image2Text' },
      ],
    };

    return (
      optionsMap[llmFactory] || [
        { value: 'chat', label: 'Chat' },
        { value: 'embedding', label: 'Embedding' },
        { value: 'rerank', label: 'Rerank' },
        { value: 'image2text', label: 'Image2Text' },
      ]
    );
  };

  const getHelpLink = () => {
    const linkMap: Record<string, string> = {
      'Ollama': 'https://github.com/infiniflow/ragflow/blob/main/docs/guides/models/deploy_local_llm.mdx',
      'Xinference': 'https://inference.readthedocs.io/en/latest/user_guide',
      'ModelScope': 'https://www.modelscope.cn/docs/model-service/API-Inference/intro',
      'LocalAI': 'https://localai.io/docs/getting-started/models/',
      'LM-Studio': 'https://lmstudio.ai/docs/basics',
      'OpenAI-API-Compatible': 'https://platform.openai.com/docs/models/gpt-4',
      'TogetherAI': 'https://docs.together.ai/docs/deployment-options',
      'Replicate': 'https://replicate.com/docs/topics/deployments',
      'OpenRouter': 'https://openrouter.ai/docs',
      'HuggingFace': 'https://huggingface.co/docs/text-embeddings-inference/quick_tour',
      'GPUStack': 'https://docs.gpustack.ai/latest/quickstart',
      'VLLM': 'https://docs.vllm.ai/en/latest/',
    };

    return (
      linkMap[llmFactory] ||
      'https://github.com/infiniflow/ragflow/blob/main/docs/guides/models/deploy_local_llm.mdx'
    );
  };

  const options = getOptions();

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
        <div className="flex justify-between items-center">
          <a
            href={getHelpLink()}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-500 hover:text-blue-600"
          >
            查看 {llmFactory} 文档
          </a>
          <div className="flex space-x-3">
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
        </div>
      }
    >
      <div className="space-y-4 py-4">
        {/* Model Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            模型类型 <span className="text-red-500">*</span>
          </label>
          <select
            name="model_type"
            value={formData.model_type}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Model Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            模型名称 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="llm_name"
            value={formData.llm_name}
            onChange={handleInputChange}
            placeholder="例如: llama2, qwen, mistral 等"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* API Base */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API 地址 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="api_base"
            value={formData.api_base}
            onChange={handleInputChange}
            placeholder="例如: http://localhost:11434"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* API Key (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API Key (可选)
          </label>
          <input
            type="password"
            name="api_key"
            value={formData.api_key}
            onChange={handleInputChange}
            placeholder="如果需要认证请填写"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Max Tokens */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            最大 Tokens <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            name="max_tokens"
            value={formData.max_tokens}
            onChange={handleInputChange}
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="mt-1 text-xs text-gray-500">
            模型支持的最大上下文长度
          </p>
        </div>

        {/* Vision Toggle (for chat models) */}
        {formData.model_type === 'chat' && (
          <div className="flex items-center">
            <input
              type="checkbox"
              id="vision"
              name="vision"
              checked={formData.vision}
              onChange={handleCheckboxChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label
              htmlFor="vision"
              className="ml-2 block text-sm text-gray-700"
            >
              启用视觉能力 (Vision)
            </label>
          </div>
        )}
      </div>
    </Modal>
  );
};

export default OllamaModal;
