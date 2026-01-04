/**
 * System Model Settings Component
 * Default model selection for different use cases
 * Based on RAGFlow system-setting.tsx
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card } from '@/components/common';
import { LlmModelType } from '@/constants/llm';
import { ISystemModelSettingSavingParams } from '@/interfaces/request/llm';
import { useFetchSystemModelSettingOnMount, useComposeLlmOptionsByModelTypes } from '../hooks';

interface ISystemSettingProps {
  loading: boolean;
  onOk: (
    payload: Omit<ISystemModelSettingSavingParams, 'tenant_id' | 'name'>
  ) => void;
}

const SystemSetting: React.FC<ISystemSettingProps> = ({ onOk, loading }) => {
  const { systemSetting, allOptions } = useFetchSystemModelSettingOnMount();

  const [formData, setFormData] = useState({
    llm_id: '',
    embd_id: '',
    img2txt_id: '',
    asr_id: '',
    rerank_id: '',
    tts_id: '',
  });

  const handleFieldChange = useCallback(
    (field: string, value: string) => {
      const updatedData = { ...formData, [field]: value || '' };
      setFormData(updatedData);
      onOk(updatedData);
    },
    [formData, onOk]
  );

  useEffect(() => {
    setFormData({
      llm_id: systemSetting?.llm_id ?? '',
      embd_id: systemSetting?.embd_id ?? '',
      img2txt_id: systemSetting?.img2txt_id ?? '',
      asr_id: systemSetting?.asr_id ?? '',
      rerank_id: systemSetting?.rerank_id ?? '',
      tts_id: systemSetting?.tts_id ?? '',
    });
  }, [systemSetting]);

  // Compose chat and image2text options
  const modelOptions = useComposeLlmOptionsByModelTypes([
    LlmModelType.Chat,
    LlmModelType.Image2text,
  ]);

  // Model type labels with options
  const modelTypes = useMemo(() => {
    return [
      {
        id: 'llm_id',
        label: '聊天模型',
        isRequired: true,
        value: formData.llm_id,
        options: modelOptions || [],
        tooltip: '用于日常对话和通用任务',
      },
      {
        id: 'embd_id',
        label: '嵌入模型',
        value: formData.embd_id,
        options: allOptions?.embedding || [],
        tooltip: '用于文本向量化和语义搜索',
      },
      {
        id: 'img2txt_id',
        label: '图像理解模型',
        value: formData.img2txt_id,
        options: allOptions?.image2text || [],
        tooltip: '用于图片内容识别和描述',
      },
      {
        id: 'asr_id',
        label: '语音转文本模型',
        value: formData.asr_id,
        options: allOptions?.speech2text || [],
        tooltip: '用于语音识别和转写',
      },
      {
        id: 'rerank_id',
        label: '重排序模型',
        value: formData.rerank_id,
        options: allOptions?.rerank || [],
        tooltip: '用于搜索结果重排序优化',
      },
      {
        id: 'tts_id',
        label: '文本转语音模型',
        value: formData.tts_id,
        options: allOptions?.tts || [],
        tooltip: '用于语音合成',
      },
    ];
  }, [formData, modelOptions, allOptions]);

  const SettingItem: React.FC<{
    id: string;
    label: string;
    value: string;
    options: any[];
    tooltip?: string;
    isRequired?: boolean;
  }> = ({ id, label, value, options, tooltip, isRequired }) => {
    return (
      <div className="flex gap-3 items-center py-2">
        <label className="block text-sm font-medium text-gray-700 w-1/3 flex items-center">
          {isRequired && <span className="text-red-500 mr-1">*</span>}
          {label}
          {tooltip && (
            <span
              className="ml-2 text-gray-400 cursor-help"
              title={tooltip}
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
          )}
        </label>
        <select
          value={value}
          onChange={(e) => handleFieldChange(id, e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        >
          <option value="">请选择模型</option>
          {options.map((group: any) => (
            <optgroup key={group.label} label={group.label}>
              {group.options.map((option: any) => (
                <option
                  key={option.value}
                  value={option.value}
                  disabled={option.disabled}
                >
                  {option.label}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </div>
    );
  };

  return (
    <div className="rounded-lg w-full bg-white">
      <div className="flex flex-col py-4 px-6 border-b border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900">
          系统模型设置
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          配置系统默认使用的 AI 模型，这些设置将作为全局默认值
        </p>
      </div>
      <div className="p-6 space-y-2">
        {modelTypes.map((item) => (
          <SettingItem key={item.id} {...item} />
        ))}
      </div>
    </div>
  );
};

export default SystemSetting;
