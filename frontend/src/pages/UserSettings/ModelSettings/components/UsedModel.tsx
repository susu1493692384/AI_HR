/**
 * Used Models Component
 * Display and manage already configured LLM models
 * Based on RAGFlow used-model.tsx
 */

import React, { useState } from 'react';
import { LlmIcon } from '@/components/llm';
import { getRealModelName, sortTags, isLocalLlmFactory } from '@/utils/llm-util';
import { ILlmItem } from '@/hooks/llm/use-llm-request';
import {
  Settings,
  ChevronDown,
  ChevronUp,
  Trash2,
  Edit,
} from 'lucide-react';
import Button from '@/components/common/Button';

interface IUsedModelProps {
  myLlmList: ILlmItem[];
  handleAddModel: (factory: string) => void;
  handleEditModel: (model: any, factory: ILlmItem) => void;
  handleDeleteFactory?: (factory: string) => void;
  handleEnableLlm?: (factory: string, modelName: string, enabled: boolean) => void;
}

const UsedModel: React.FC<IUsedModelProps> = ({
  myLlmList,
  handleAddModel,
  handleEditModel,
  handleDeleteFactory,
  handleEnableLlm,
}) => {
  return (
    <div className="flex flex-col w-full gap-4 mb-4">
      <div className="text-gray-900 text-xl font-semibold mb-2 mt-4">
        已添加的模型
      </div>
      {myLlmList.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <p className="mt-2 text-sm">还没有添加任何模型</p>
          <p className="text-xs text-gray-400 mt-1">
            从右侧选择一个提供商开始添加
          </p>
        </div>
      ) : (
        myLlmList.map((llm) => (
          <ModelProviderCard
            key={llm.name}
            item={llm}
            clickApiKey={handleAddModel}
            handleEditModel={handleEditModel}
            handleDeleteFactory={handleDeleteFactory}
            handleEnableLlm={handleEnableLlm}
          />
        ))
      )}
    </div>
  );
};

interface IModelCardProps {
  item: ILlmItem;
  clickApiKey: (llmFactory: string) => void;
  handleEditModel: (model: any, factory: ILlmItem) => void;
  handleDeleteFactory?: (factory: string) => void;
  handleEnableLlm?: (factory: string, modelName: string, enabled: boolean) => void;
}

const ModelProviderCard: React.FC<IModelCardProps> = ({
  item,
  clickApiKey,
  handleEditModel,
  handleDeleteFactory,
  handleEnableLlm,
}) => {
  const [visible, setVisible] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleApiKeyClick = () => {
    clickApiKey(item.name);
  };

  const handleDeleteClick = () => {
    setShowDeleteConfirm(true);
  };

  const confirmDelete = () => {
    handleDeleteFactory?.(item.name);
    setShowDeleteConfirm(false);
  };

  return (
    <div className="w-full rounded-lg border border-gray-200 bg-white">
      {/* Header */}
      <div className="flex h-16 items-center justify-between px-4 cursor-pointer hover:bg-gray-50 transition-colors">
        <div className="flex items-center space-x-3">
          <LlmIcon name={item.name} width={32} />
          <div>
            <div className="font-medium text-lg text-gray-900">
              {item.name}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={(e) => {
              e.stopPropagation();
              handleApiKeyClick();
            }}
            className="px-3 py-1.5 text-sm rounded-md border border-gray-300 hover:bg-gray-50 flex items-center space-x-1"
          >
            <Settings className="w-4 h-4" />
            <span>{isLocalLlmFactory(item.name) ? '添加模型' : 'API-Key'}</span>
          </Button>

          <Button
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              setVisible(!visible);
            }}
            className="px-3 py-1.5 text-sm rounded-md hover:bg-gray-100 flex items-center space-x-1"
          >
            <span>{visible ? '收起模型' : '展开模型'}</span>
            {visible ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </Button>

          {showDeleteConfirm ? (
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">确认删除?</span>
              <button
                onClick={confirmDelete}
                className="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600"
              >
                确认
              </button>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                取消
              </button>
            </div>
          ) : (
            <Button
              variant="ghost"
              onClick={handleDeleteClick}
              className="p-2 hover:text-red-600 hover:bg-red-50 rounded-md"
              title="删除此提供商"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Content */}
      {visible && (
        <div>
          <div className="px-4 flex flex-wrap gap-1 mt-1">
            {sortTags(item.tags).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-md"
              >
                {tag}
              </span>
            ))}
          </div>
          <div className="m-4 bg-gray-50 rounded-lg max-h-96 overflow-auto">
            <div>
              {item.llm.map((model) => (
                <div
                  key={model.name}
                  className="flex items-center border-b border-gray-200 justify-between p-3 hover:bg-gray-100 transition-colors last:border-0"
                >
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-sm">
                      {getRealModelName(model.name)}
                    </span>
                    <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">
                      {model.type}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    {isLocalLlmFactory(item.name) && (
                      <Button
                        variant="ghost"
                        onClick={() => handleEditModel(model, item)}
                        className="p-1.5 text-gray-600 hover:text-gray-900 rounded"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                    )}
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={model.status === '1'}
                        onChange={(e) =>
                          handleEnableLlm?.(
                            item.name,
                            model.name,
                            e.target.checked
                          )
                        }
                      />
                      <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsedModel;
