import React, { useState, useMemo } from 'react';
import {
  FileText,
  Download,
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';

interface ReportPanelProps {
  messages: Array<{ role: 'user' | 'assistant'; content: string; json_data?: string }>;
  resumeData?: {
    name: string;
    position: string;
  };
}

interface AnalysisData {
  overall_score?: number;
  credibility_score?: number;
  risk_level?: 'A' | 'B' | 'C' | 'D';
  verified_claims?: Array<{ claim: string; evidence?: string; confidence?: string }>;
  questionable_claims?: Array<{
    claim: string;
    concern?: string;
    verification_needed?: string;
    confidence?: string;
  }>;
  logical_inconsistencies?: Array<{ issue: string; explanation?: string }>;
  exaggeration_indicators?: Array<{ indicator: string; count?: number }>;
  interview_questions?: string[];
  constructive_feedback?: string[];
  recommendations?: string | string[];
  summary?: string;
  // 原有4个专家分析结果
  skills?: {
    credibility_score?: number;
    score?: number;
    matched_skills?: Array<{ name: string; level: string; relevance: string }>;
    missing_skills?: string[];
    strengths?: string[];
  };
  experience?: {
    score?: number;
    total_years?: number;
    relevant_years?: number;
    project_highlights?: string[];
  };
  education?: {
    score?: number;
    highest_degree?: string;
    major_relevance?: string;
  };
  soft_skills?: {
    score?: number;
    communication?: string;
    teamwork?: string;
  };
  // 新增3个专家分析结果
  stability?: {
    score?: number;
    job_tenure_avg?: number;
    job_changes_count?: number;
    frequent_hopper_flag?: boolean;
    career_progression_score?: number;
    promotion_history?: string[];
    role_evolution?: string;
    leaving_reasons_quality?: string;
  };
  work_attitude?: {
    score?: number;
    stress_resistance?: string;
    responsibility_level?: string;
    stress_score?: number;
    responsibility_score?: number;
    dedication_score?: number;
    emotional_score?: number;
  };
  development_potential?: {
    score?: number;
    learning_ability?: string;
    innovation_capability?: string;
    growth_mindset?: string;
    adaptability_score?: number;
    high_potential_flags?: string[];
  };
  // 元数据
  analysis_version?: string;
  dimension_count?: number;
  weights_used?: Record<string, number>;
}

interface DimensionScore {
  name: string;
  score: number;
  grade: 'A' | 'B' | 'C' | 'D';
  trend: 'up' | 'down' | 'neutral';
}

const ReportPanel: React.FC<ReportPanelProps> = ({ messages, resumeData }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview', 'scores']));
  const [isExporting, setIsExporting] = useState(false);

  // 辅助函数：获取等级
  const getGrade = (score: number): 'A' | 'B' | 'C' | 'D' => {
    if (score >= 90) return 'A';
    if (score >= 70) return 'B';
    if (score >= 50) return 'C';
    return 'D';
  };

  // 辅助函数：获取等级配置
  const getGradeConfig = (grade: 'A' | 'B' | 'C' | 'D') => {
    const configs = {
      A: { color: 'green', bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', label: '优秀' },
      B: { color: 'blue', bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', label: '良好' },
      C: { color: 'yellow', bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200', label: '一般' },
      D: { color: 'red', bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', label: '较差' }
    };
    return configs[grade];
  };

  // 从AI消息中解析分析数据
  const analysisData = useMemo(() => {
    const assistantMessages = messages.filter(m => m.role === 'assistant');

    console.log('📊 [ReportPanel] 开始解析分析数据');
    console.log(`📊 [ReportPanel] 共有 ${assistantMessages.length} 条AI消息`);

    // 首先尝试从json_data字段获取（隐藏的JSON数据）
    for (let i = 0; i < assistantMessages.length; i++) {
      const msg = assistantMessages[assistantMessages.length - 1 - i]; // 从最新的开始

      // 优先使用json_data字段（不显示在聊天中的数据）
      if (msg.json_data) {
        console.log('✅ [ReportPanel] 从json_data字段找到JSON数据');
        try {
          const parsed = JSON.parse(msg.json_data);
          console.log('✅ [ReportPanel] JSON解析成功:', parsed);
          return parsed as AnalysisData;
        } catch (e) {
          console.log('❌ [ReportPanel] json_data解析失败:', e);
        }
      }
    }

    // 如果没有json_data，回退到从消息内容中解析（旧版本兼容）
    console.log('⚠️ [ReportPanel] json_data未找到，尝试从消息内容解析');
    for (let i = 0; i < assistantMessages.length; i++) {
      const msg = assistantMessages[assistantMessages.length - 1 - i]; // 从最新的开始
      const content = msg.content;

      console.log(`📊 [ReportPanel] 尝试解析第 ${assistantMessages.length - i} 条消息`);
      console.log(`📊 [ReportPanel] 消息长度: ${content.length} 字符`);

      try {
        // 1. 查找JSON代码块
        const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
        if (jsonMatch) {
          console.log('✅ [ReportPanel] 找到JSON代码块');
          const parsed = JSON.parse(jsonMatch[1]);
          console.log('✅ [ReportPanel] JSON解析成功:', parsed);
          return parsed as AnalysisData;
        }

        // 2. 查找纯JSON代码块
        const codeMatch = content.match(/```\s*(\{[\s\S]*?\})\s*```/);
        if (codeMatch) {
          console.log('✅ [ReportPanel] 找到纯JSON代码块');
          const parsed = JSON.parse(codeMatch[1]);
          console.log('✅ [ReportPanel] JSON解析成功:', parsed);
          return parsed as AnalysisData;
        }

        // 3. 尝试直接解析整个内容
        if (content.trim().startsWith('{')) {
          console.log('✅ [ReportPanel] 消息以{开头，尝试直接解析');
          const parsed = JSON.parse(content);
          console.log('✅ [ReportPanel] JSON解析成功:', parsed);
          return parsed as AnalysisData;
        }

        // 4. 尝试提取花括号内容
        const braceMatch = content.match(/\{[\s\S]*\}/);
        if (braceMatch) {
          console.log('✅ [ReportPanel] 找到花括号内容');
          const parsed = JSON.parse(braceMatch[0]);
          console.log('✅ [ReportPanel] JSON解析成功:', parsed);
          return parsed as AnalysisData;
        }

        console.log(`⚠️ [ReportPanel] 第 ${assistantMessages.length - i} 条消息中未找到JSON`);
      } catch (e) {
        console.log(`❌ [ReportPanel] 解析第 ${assistantMessages.length - i} 条消息失败:`, e);
        // 继续尝试下一条消息
      }
    }

    console.log('⚠️ [ReportPanel] 所有消息解析完毕，未找到有效的JSON数据');
    return {} as AnalysisData;
  }, [messages]);

  // 计算各维度分数（7维度版本）
  const dimensionScores: DimensionScore[] = useMemo(() => {
    // 从专家结果中提取实际分数
    const skillsScore = analysisData.skills?.credibility_score || analysisData.skills?.score || 0;
    const experienceScore = analysisData.experience?.score || 0;
    const educationScore = analysisData.education?.score || 0;
    const softSkillsScore = analysisData.soft_skills?.score || 0;
    const stabilityScore = analysisData.stability?.score || 0;
    const attitudeScore = analysisData.work_attitude?.score || 0;
    const potentialScore = analysisData.development_potential?.score || 0;

    return [
      {
        name: '技能匹配度',
        score: skillsScore,
        grade: getGrade(skillsScore),
        trend: 'neutral'
      },
      {
        name: '工作经验',
        score: experienceScore,
        grade: getGrade(experienceScore),
        trend: 'neutral'
      },
      {
        name: '教育背景',
        score: educationScore,
        grade: getGrade(educationScore),
        trend: 'neutral'
      },
      {
        name: '软技能',
        score: softSkillsScore,
        grade: getGrade(softSkillsScore),
        trend: 'neutral'
      },
      {
        name: '稳定性',
        score: stabilityScore,
        grade: getGrade(stabilityScore),
        trend: 'neutral'
      },
      {
        name: '工作态度',
        score: attitudeScore,
        grade: getGrade(attitudeScore),
        trend: 'neutral'
      },
      {
        name: '发展潜力',
        score: potentialScore,
        grade: getGrade(potentialScore),
        trend: 'neutral'
      }
    ];
  }, [
    analysisData.skills,
    analysisData.experience,
    analysisData.education,
    analysisData.soft_skills,
    analysisData.stability,
    analysisData.work_attitude,
    analysisData.development_potential
  ]);

  // 切换展开/收起
  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  // 导出报告
  const handleExportReport = async () => {
    setIsExporting(true);

    try {
      // 生成HTML报告
      const reportHtml = generateReportHtml();

      // 创建下载
      const blob = new Blob([reportHtml], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `简历分析报告_${resumeData?.name || '候选人'}_${new Date().toLocaleDateString()}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('导出报告失败:', error);
      alert('导出报告失败，请稍后重试');
    } finally {
      setIsExporting(false);
    }
  };

  // 生成HTML报告 (7维度版本)
  const generateReportHtml = () => {
    const grade = analysisData.risk_level || getGrade(analysisData.credibility_score || 65);
    const config = getGradeConfig(grade);
    const version = analysisData.analysis_version || '2.0';
    const dimensionCount = analysisData.dimension_count || 7;

    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>简历分析报告 - ${resumeData?.name || '候选人'}</title>
  <style>
    body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .header { border-bottom: 2px solid #3b82f6; padding-bottom: 20px; margin-bottom: 30px; }
    .title { font-size: 28px; color: #1f2937; margin: 0 0 10px 0; }
    .subtitle { color: #6b7280; font-size: 14px; }
    .score-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }
    .score-big { font-size: 48px; font-weight: bold; }
    .grade-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; margin-left: 10px; }
    .section { margin-bottom: 30px; }
    .section-title { font-size: 18px; color: #1f2937; border-left: 4px solid #3b82f6; padding-left: 12px; margin-bottom: 15px; }
    .dimension-item { padding: 12px; border-left: 3px solid #d1d5db; background: #f9fafb; margin-bottom: 10px; border-radius: 4px; }
    .claim-item { padding: 12px; border-left: 3px solid #d1d5db; background: #f9fafb; margin-bottom: 10px; border-radius: 4px; }
    .claim-verified { border-left-color: #10b981; background: #ecfdf5; }
    .claim-questionable { border-left-color: #f59e0b; background: #fffbeb; }
    .question-item { padding: 10px; background: #eff6ff; border-radius: 4px; margin-bottom: 8px; }
    .footer { text-align: center; color: #9ca3af; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 class="title">简历分析报告</h1>
      <p class="subtitle">候选人：${resumeData?.name || '未知'} | 职位：${resumeData?.position || '未指定'}</p>
      <p class="subtitle">生成时间：${new Date().toLocaleString('zh-CN')}</p>
      <p class="subtitle">分析版本：v${version} | ${dimensionCount}维度评估</p>
    </div>

    <div class="score-section">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <div style="font-size: 16px; opacity: 0.9; margin-bottom: 10px;">综合评分</div>
          <div class="score-big">${analysisData.credibility_score || analysisData.overall_score || 'N/A'}<span style="font-size: 24px; opacity: 0.8;">/100</span></div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 16px; opacity: 0.9; margin-bottom: 10px;">风险等级</div>
          <span class="grade-badge" style="background: white; color: ${grade === 'A' ? '#10b981' : grade === 'B' ? '#3b82f6' : grade === 'C' ? '#f59e0b' : '#ef4444'};">
            ${config.label} (${grade}级)
          </span>
        </div>
      </div>
    </div>

    <div class="section">
      <h2 class="section-title">维度评分</h2>
      ${dimensionScores.map(dim => `
        <div class="dimension-item">
          <strong>${dim.name}</strong>: ${dim.score}分 (${dim.grade}级)
        </div>
      `).join('')}
    </div>

    ${analysisData.verified_claims && analysisData.verified_claims.length > 0 ? `
    <div class="section">
      <h2 class="section-title">✅ 可信的陈述</h2>
      ${analysisData.verified_claims.map(claim => `
        <div class="claim-item claim-verified">
          <strong>${claim.claim}</strong>
          ${claim.evidence ? `<br><small style="color: #059669;">证据：${claim.evidence}</small>` : ''}
        </div>
      `).join('')}
    </div>
    ` : ''}

    ${analysisData.questionable_claims && analysisData.questionable_claims.length > 0 ? `
    <div class="section">
      <h2 class="section-title">⚠️ 需要验证的陈述</h2>
      ${analysisData.questionable_claims.map(claim => `
        <div class="claim-item claim-questionable">
          <strong>${claim.claim}</strong>
          ${claim.concern ? `<br><small style="color: #d97706;">疑点：${claim.concern}</small>` : ''}
          ${claim.verification_needed ? `<br><small style="color: #92400e;">验证方法：${claim.verification_needed}</small>` : ''}
        </div>
      `).join('')}
    </div>
    ` : ''}

    ${analysisData.logical_inconsistencies && analysisData.logical_inconsistencies.length > 0 ? `
    <div class="section">
      <h2 class="section-title">🔄 逻辑矛盾</h2>
      ${analysisData.logical_inconsistencies.map(issue => `
        <div class="claim-item">
          <strong>${issue.issue}</strong>
          ${issue.explanation ? `<br><small>${issue.explanation}</small>` : ''}
        </div>
      `).join('')}
    </div>
    ` : ''}

    ${analysisData.interview_questions && analysisData.interview_questions.length > 0 ? `
    <div class="section">
      <h2 class="section-title">🎯 建议的面试问题</h2>
      ${analysisData.interview_questions.map(q => `<div class="question-item">${q}</div>`).join('')}
    </div>
    ` : ''}

    ${analysisData.recommendations ? `
    <div class="section">
      <h2 class="section-title">📋 综合建议</h2>
      <p style="line-height: 1.6; color: #4b5563;">${analysisData.recommendations}</p>
    </div>
    ` : ''}

    <div class="footer">
      本报告由 AI 简历分析系统生成 | 仅供参考，请结合实际情况综合判断 | 分析版本 v${version}
    </div>
  </div>
</body>
</html>`;
  };

  const grade = analysisData.risk_level || getGrade(analysisData.credibility_score || 65);
  const config = getGradeConfig(grade);
  const hasAnalysisData = analysisData.credibility_score || analysisData.overall_score ||
                          (analysisData.skills && (analysisData.skills.score || analysisData.skills.credibility_score));

  // 没有分析数据时的显示
  if (!hasAnalysisData && messages.length === 0) {
    return (
      <div className="h-full flex flex-col bg-white">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">分析报告</h2>
          <p className="text-sm text-gray-600">开始对话以生成分析报告</p>
        </div>
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <FileText className="w-16 h-16 text-gray-300 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">暂无分析数据</h3>
          <p className="text-sm text-gray-500 mb-4">
            请向AI助手提问以生成简历分析报告
          </p>
          <div className="text-left text-sm text-gray-600 space-y-2">
            <p>💡 试试这些问题：</p>
            <ul className="list-disc list-inside space-y-1">
              <li>分析候选人的技能优势</li>
              <li>评估项目经验</li>
              <li>给出综合评分和建议</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white">
      {/* 头部 */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">分析报告</h2>
          {resumeData && (
            <p className="text-xs text-gray-500 mt-1">{resumeData.name} - {resumeData.position}</p>
          )}
        </div>
        <button
          onClick={handleExportReport}
          disabled={isExporting || !hasAnalysisData}
          className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <Download className="w-4 h-4" />
          <span>{isExporting ? '导出中...' : '生成报告'}</span>
        </button>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* 综合评分卡片 */}
        <div className={`bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border-2 ${config.border}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Shield className={`w-5 h-5 ${config.text.replace('700', '600')}`} />
              <span className="font-semibold text-gray-900">可信度评分</span>
              {analysisData.analysis_version && (
                <span className="text-xs text-gray-500 bg-white px-2 py-0.5 rounded">
                  v{analysisData.analysis_version}
                </span>
              )}
            </div>
            <span className={`px-2 py-1 rounded text-xs font-bold ${config.bg} ${config.text} ${config.border} border`}>
              {config.label} ({grade}级)
            </span>
          </div>

          <div className="flex items-end justify-between">
            <div>
              <div className="text-4xl font-bold text-blue-600">
                {analysisData.credibility_score || analysisData.overall_score || '--'}
                <span className="text-lg text-gray-500">/100</span>
              </div>
              <p className="text-xs text-gray-600 mt-1">
                {grade === 'A' && '优秀，风险低'}
                {grade === 'B' && '良好，部分需验证'}
                {grade === 'C' && '一般，需重点验证'}
                {grade === 'D' && '较差，建议谨慎'}
              </p>
            </div>

            {/* 维度数量指示器 */}
            <div className="text-right">
              <div className="text-sm text-gray-600">
                {analysisData.dimension_count || 7}个维度评估
              </div>
            </div>
          </div>

          {/* 进度条 */}
          <div className="mt-3">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  grade === 'A' ? 'bg-green-500' :
                  grade === 'B' ? 'bg-blue-500' :
                  grade === 'C' ? 'bg-yellow-500' :
                  'bg-red-500'
                }`}
                style={{ width: `${analysisData.credibility_score || analysisData.overall_score || 0}%` }}
              />
            </div>
          </div>
        </div>

        {/* 维度评分 (7维度) */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div
            className="p-3 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
            onClick={() => toggleSection('scores')}
          >
            <h3 className="font-semibold text-gray-900">维度评分</h3>
            {expandedSections.has('scores') ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
          </div>

          {expandedSections.has('scores') && (
            <div className="p-3 pt-0 space-y-3">
              {dimensionScores.map((dimension, index) => {
                const dimConfig = getGradeConfig(dimension.grade);
                return (
                  <div key={index} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-700">{dimension.name}</span>
                      <div className="flex items-center space-x-2">
                        {dimension.trend === 'up' && <TrendingUp className="w-3 h-3 text-green-500" />}
                        {dimension.trend === 'down' && <TrendingDown className="w-3 h-3 text-red-500" />}
                        {dimension.trend === 'neutral' && <Minus className="w-3 h-3 text-gray-400" />}
                        <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${dimConfig.bg} ${dimConfig.text}`}>
                          {dimension.grade}
                        </span>
                        <span className="font-medium text-gray-900">{dimension.score}</span>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${
                          dimension.grade === 'A' ? 'bg-green-500' :
                          dimension.grade === 'B' ? 'bg-blue-500' :
                          dimension.grade === 'C' ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${dimension.score}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* 可信的陈述 */}
        {analysisData.verified_claims && analysisData.verified_claims.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div
              className="p-3 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleSection('verified')}
            >
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <h3 className="font-semibold text-gray-900">可信的陈述</h3>
                <span className="text-xs text-gray-500">({analysisData.verified_claims.length})</span>
              </div>
              {expandedSections.has('verified') ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
            </div>

            {expandedSections.has('verified') && (
              <div className="p-3 pt-0 space-y-2">
                {analysisData.verified_claims.map((claim, index) => (
                  <div key={index} className="p-2 bg-green-50 border-l-2 border-green-500 rounded text-sm">
                    <p className="text-gray-900 font-medium">{claim.claim}</p>
                    {claim.evidence && <p className="text-xs text-green-700 mt-1">📌 {claim.evidence}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 需要验证的陈述 */}
        {analysisData.questionable_claims && analysisData.questionable_claims.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div
              className="p-3 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleSection('questionable')}
            >
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-yellow-600" />
                <h3 className="font-semibold text-gray-900">需要验证的陈述</h3>
                <span className="text-xs text-gray-500">({analysisData.questionable_claims.length})</span>
              </div>
              {expandedSections.has('questionable') ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
            </div>

            {expandedSections.has('questionable') && (
              <div className="p-3 pt-0 space-y-2">
                {analysisData.questionable_claims.map((claim, index) => (
                  <div key={index} className="p-2 bg-yellow-50 border-l-2 border-yellow-500 rounded text-sm">
                    <p className="text-gray-900 font-medium">{claim.claim}</p>
                    {claim.concern && <p className="text-xs text-yellow-700 mt-1">⚠️ {claim.concern}</p>}
                    {claim.verification_needed && <p className="text-xs text-orange-700 mt-1">🔍 {claim.verification_needed}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 逻辑矛盾 */}
        {analysisData.logical_inconsistencies && analysisData.logical_inconsistencies.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div
              className="p-3 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleSection('inconsistencies')}
            >
              <div className="flex items-center space-x-2">
                <XCircle className="w-4 h-4 text-red-600" />
                <h3 className="font-semibold text-gray-900">逻辑矛盾</h3>
                <span className="text-xs text-gray-500">({analysisData.logical_inconsistencies.length})</span>
              </div>
              {expandedSections.has('inconsistencies') ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
            </div>

            {expandedSections.has('inconsistencies') && (
              <div className="p-3 pt-0 space-y-2">
                {analysisData.logical_inconsistencies.map((issue, index) => (
                  <div key={index} className="p-2 bg-red-50 border-l-2 border-red-500 rounded text-sm">
                    <p className="text-gray-900 font-medium">{issue.issue}</p>
                    {issue.explanation && <p className="text-xs text-red-700 mt-1">💡 {issue.explanation}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 面试问题 */}
        {analysisData.interview_questions && analysisData.interview_questions.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div
              className="p-3 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleSection('interview')}
            >
              <div className="flex items-center space-x-2">
                <HelpCircle className="w-4 h-4 text-blue-600" />
                <h3 className="font-semibold text-gray-900">建议的面试问题</h3>
                <span className="text-xs text-gray-500">({analysisData.interview_questions.length})</span>
              </div>
              {expandedSections.has('interview') ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
            </div>

            {expandedSections.has('interview') && (
              <div className="p-3 pt-0 space-y-2">
                {analysisData.interview_questions.map((question, index) => (
                  <div key={index} className="p-2 bg-blue-50 rounded text-sm text-gray-800">
                    <span className="text-blue-600 font-bold mr-2">{index + 1}.</span>
                    {question}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 综合建议 */}
        {analysisData.recommendations && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <h3 className="font-semibold text-blue-900 mb-2">📋 综合建议</h3>
            <p className="text-sm text-blue-800 whitespace-pre-wrap">{analysisData.recommendations}</p>
          </div>
        )}

        {/* 建设性反馈 */}
        {analysisData.constructive_feedback && analysisData.constructive_feedback.length > 0 && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
            <h3 className="font-semibold text-gray-900 mb-2">💡 建设性反馈</h3>
            <ul className="space-y-1">
              {analysisData.constructive_feedback.map((feedback, index) => (
                <li key={index} className="text-sm text-gray-700 flex items-start">
                  <span className="text-gray-400 mr-2">•</span>
                  <span>{feedback}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportPanel;
