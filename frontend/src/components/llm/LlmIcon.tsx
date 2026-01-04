/**
 * LLM Provider Icon Component
 * Displays icon for various LLM providers
 * Based on RAGFlow LLM icon component
 */

import React from 'react';
import { LLMFactory, IconMap } from '@/constants/llm';
import { cn } from '@/lib/utils';

interface ILlmIconProps {
  name: string;
  width?: number;
  height?: number;
  size?: 'small' | 'medium' | 'large';
  className?: string;
  imgClass?: string;
}

const sizeMap = {
  small: 16,
  medium: 24,
  large: 32,
};

// SVG icons for major providers
const ProviderIcons: Record<string, React.FC<React.SVGProps<SVGSVGElement>>> = {
  openai: (props) => (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.0 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z" fill="currentColor"/>
    </svg>
  ),
  anthropropic: (props) => (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <path d="M17.304 3.541l-.568-.329a10.27 10.27 0 0 0-10.472 0l-.568.329A10.265 10.265 0 0 0 .5 12.257v.327c0 3.78 2.075 7.245 5.455 9.028l.569.329a10.27 10.27 0 0 0 10.472 0l.568-.329a10.265 10.265 0 0 0 5.196-8.886v-.327a10.265 10.265 0 0 0-5.196-8.886v-.072zm-1.837 16.276l-3.467 2.002-3.467-2.002V12.17l3.467-2.002 3.467 2.002v7.647z" fill="currentColor"/>
    </svg>
  ),
  deepseek: (props) => (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <circle cx="12" cy="12" r="10" fill="currentColor"/>
      <path d="M8 12h8M12 8v8" stroke="white" strokeWidth="2"/>
    </svg>
  ),
  azure: (props) => (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <path d="M11.96 2.108L2 12.069l9.96 9.96L22 12.069 11.96 2.108z" fill="#0078D4"/>
    </svg>
  ),
  gemini: (props) => (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" fill="currentColor"/>
    </svg>
  ),
  groq: (props) => (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <circle cx="12" cy="12" r="10" fill="currentColor"/>
      <path d="M8 8h8v8H8z" fill="white"/>
    </svg>
  ),
  bedrock: (props) => (
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" {...props}>
      <path d="M12 2L2 7v10l10 5 10-5V7L12 2z" fill="#FF9900"/>
    </svg>
  ),
};

const LlmIcon: React.FC<ILlmIconProps> = ({
  name,
  width,
  height,
  size = 'medium',
  className,
  imgClass,
}) => {
  const computedSize = width || height || sizeMap[size];
  const iconName = IconMap[name as LLMFactory] || name.toLowerCase();

  const IconComponent = ProviderIcons[iconName];

  if (IconComponent) {
    return (
      <div
        className={cn('flex items-center justify-center', className)}
        style={{ width: computedSize, height: computedSize }}
      >
        <IconComponent
          className={imgClass}
          width={computedSize}
          height={computedSize}
        />
      </div>
    );
  }

  // Default fallback icon
  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-md bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold',
        className
      )}
      style={{ width: computedSize, height: computedSize }}
    >
      <span
        className={imgClass}
        style={{ fontSize: computedSize * 0.5 }}
      >
        {name.charAt(0).toUpperCase()}
      </span>
    </div>
  );
};

export default LlmIcon;
