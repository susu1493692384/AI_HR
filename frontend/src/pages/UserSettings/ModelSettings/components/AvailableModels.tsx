/**
 * Available Models Component
 * Display and manage available LLM providers to add
 * Based on RAGFlow un-add-model.tsx
 */

import React, { useState, useMemo } from 'react';
import { Search, Plus, ArrowUpRight } from 'lucide-react';
import { LlmIcon } from '@/components/llm';
import { LLMFactory, APIMapUrl, sortTags } from '@/constants/llm';
import { IFactory } from '@/interfaces/database/llm';
import Button from '@/components/common/Button';

interface IAvailableModelsProps {
  factoryList: IFactory[];
  handleAddModel: (factory: string) => void;
}

type TagType =
  | 'LLM'
  | 'TEXT EMBEDDING'
  | 'TEXT RE-RANK'
  | 'TTS'
  | 'SPEECH2TEXT'
  | 'IMAGE2TEXT'
  | 'MODERATION'
  | 'OCR';

const AvailableModels: React.FC<IAvailableModelsProps> = ({
  factoryList,
  handleAddModel,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTag, setSelectedTag] = useState<string | null>(null);

  const filteredModels = useMemo(() => {
    const models = factoryList.filter((model) => {
      const matchesSearch = model.name
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesTag =
        selectedTag === null ||
        model.tags.split(',').some((tag) => tag.trim() === selectedTag);
      return matchesSearch && matchesTag;
    });
    return models;
  }, [factoryList, searchTerm, selectedTag]);

  const allTags = useMemo(() => {
    const tagsSet = new Set<string>();
    factoryList.forEach((model) => {
      model.tags.split(',').forEach((tag) => tagsSet.add(tag.trim()));
    });
    return Array.from(tagsSet).sort();
  }, [factoryList]);

  const handleTagClick = (tag: string) => {
    setSelectedTag(selectedTag === tag ? null : tag);
  };

  return (
    <div className="text-gray-900 h-full p-4">
      <div className="text-gray-900 text-base font-semibold mb-4">
        可添加的模型
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="搜索模型提供商..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Tags Filter */}
      <div className="flex flex-wrap gap-2 mb-6">
        <Button
          variant={selectedTag === null ? 'primary' : 'outline'}
          onClick={() => setSelectedTag(null)}
          className={`px-3 py-1.5 text-xs rounded-sm transition-colors ${
            selectedTag === null
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-300'
          }`}
        >
          全部
        </Button>
        {allTags.map((tag) => (
          <Button
            key={tag}
            variant={selectedTag === tag ? 'primary' : 'outline'}
            onClick={() => handleTagClick(tag)}
            className={`px-3 py-1.5 text-xs rounded-sm transition-colors ${
              selectedTag === tag
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-300'
            }`}
          >
            {tag}
          </Button>
        ))}
      </div>

      {/* Models List */}
      <div className="flex flex-col gap-3 overflow-auto h-[calc(100vh-350px)] pr-1">
        {filteredModels.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-sm">未找到匹配的模型提供商</p>
            <p className="text-xs text-gray-400 mt-1">
              尝试调整搜索词或标签筛选
            </p>
          </div>
        ) : (
          filteredModels.map((model) => (
            <div
              key={model.name}
              className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 hover:border-blue-300 transition-colors group cursor-pointer"
              onClick={() => handleAddModel(model.name)}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3 flex-1">
                  <LlmIcon name={model.name} size="medium" />
                  <div className="flex flex-1 gap-1 items-center">
                    <div className="font-normal text-base truncate">
                      {model.name}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {APIMapUrl[model.name as LLMFactory] && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        window.open(
                          APIMapUrl[model.name as LLMFactory],
                          '_blank',
                          'noopener,noreferrer'
                        );
                      }}
                      className="p-1 text-gray-400 hover:text-blue-600 rounded-md hover:bg-blue-50 transition-colors"
                      title="获取 API Key"
                    >
                      <ArrowUpRight size={16} />
                    </button>
                  )}
                  <Button
                    variant="ghost"
                    className="px-2 items-center gap-1 text-xs h-7 rounded-md transition-colors opacity-0 group-hover:opacity-100 bg-blue-500 text-white hover:bg-blue-600"
                  >
                    <Plus size={12} />
                    添加
                  </Button>
                </div>
              </div>

              <div className="flex flex-wrap gap-1">
                {sortTags(model.tags).map((tag, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-md"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AvailableModels;
