"""
简历解析服务
从 PDF 和 Word 文档中提取文本内容
"""

import logging
import re
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ResumeParser:
    """简历解析器"""

    def __init__(self):
        """初始化解析器"""
        self.supported_formats = ['.pdf', '.doc', '.docx', '.txt']

    async def parse_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        解析简历文件

        Args:
            file_path: 文件路径
            filename: 文件名

        Returns:
            解析结果字典
        """
        file_ext = Path(filename).suffix.lower()

        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {file_ext}")

        # 根据文件类型选择解析方法
        if file_ext == '.pdf':
            text = await self._parse_pdf(file_path)
        elif file_ext in ['.doc', '.docx']:
            text = await self._parse_word(file_path)
        elif file_ext == '.txt':
            text = await self._parse_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")

        # 提取候选人基本信息
        candidate_info = self._extract_candidate_info(text, filename)

        return {
            "extracted_text": text,
            "candidate_name": candidate_info.get("name"),
            "candidate_email": candidate_info.get("email"),
            "candidate_phone": candidate_info.get("phone"),
            "candidate_location": candidate_info.get("location"),
        }

    async def _parse_pdf(self, file_path: str) -> str:
        """解析 PDF 文件"""
        try:
            import PyPDF2

            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"

            # 清理提取的文本
            return self._clean_text(text)

        except ImportError:
            # 备用方案：使用 pdfplumber
            try:
                import pdfplumber

                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"

                return self._clean_text(text)
            except ImportError:
                logger.warning("PyPDF2 和 pdfplumber 都未安装，无法解析 PDF")
                return ""
        except Exception as e:
            logger.error(f"PDF 解析失败: {str(e)}")
            return ""

    async def _parse_word(self, file_path: str) -> str:
        """解析 Word 文件"""
        try:
            from docx import Document

            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return self._clean_text(text)

        except ImportError:
            logger.warning("python-docx 未安装，无法解析 Word 文档")
            return ""
        except Exception as e:
            logger.error(f"Word 文档解析失败: {str(e)}")
            return ""

    async def _parse_txt(self, file_path: str) -> str:
        """解析纯文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self._clean_text(text)
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    text = f.read()
                return self._clean_text(text)
            except Exception as e:
                logger.error(f"文本文件解析失败: {str(e)}")
                return ""

    def _clean_text(self, text: str) -> str:
        """清理提取的文本"""
        if not text:
            return ""

        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)

        # 移除特殊字符
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # 移除页眉页脚（常见模式）
        text = re.sub(r'第\s*\d+\s*页', '', text)
        text = re.sub(r'Page\s*\d+', '', text)

        return text.strip()

    def _extract_candidate_info(self, text: str, filename: str = "") -> Dict[str, Optional[str]]:
        """从文本中提取候选人基本信息"""
        info = {
            "name": None,
            "email": None,
            "phone": None,
            "location": None,
        }

        # 首先尝试从文件名提取姓名（格式如：简历_姓名.pdf 或 简历__姓名.pdf）
        filename_patterns = [
            r'[_\s]{1,2}([\u4e00-\u9fa5]{2,3})\.',  # 简历_姓名.pdf
            r'[\s_]{2,}([\u4e00-\u9fa5]{2,3})\.',  # 简历__姓名.pdf
        ]
        for pattern in filename_patterns:
            match = re.search(pattern, filename)
            if match:
                info["name"] = match.group(1)
                break

        # 提取邮箱
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            info["email"] = emails[0]

        # 提取手机号（支持多种格式）
        phone_patterns = [
            r'1[3-9]\d{9}',  # 中国大陆手机号
            r'\d{3}-\d{4}-\d{4}',  # 021-1234-5678
            r'\d{3}-\d{8}',  # 021-12345678
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # 国际格式
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                info["phone"] = phones[0]
                break

        # 如果文件名没找到姓名，再从文本中提取
        if not info["name"]:
            # 提取姓名 - 多种模式
            name_patterns = [
                # 模式1: 姓名:xxxx 或 姓名：xxxx
                r'姓\s*名\s*[:：]\s*([\u4e00-\u9fa5]{2,4})',
            ]

            # 尝试各种姓名提取模式
            for pattern in name_patterns:
                match = re.search(pattern, text)
                if match:
                    info["name"] = match.group(1)
                    break

            # 如果还没找到，尝试从文本开头查找
            if not info["name"]:
                # 取文本前200字符进行分析
                header_text = text[:200]
                # 清理掉邮箱和电话
                for email in emails:
                    header_text = header_text.replace(email, '')
                for pattern in phone_patterns:
                    header_text = re.sub(pattern, '', header_text)
                # 清理掉日期、数字等
                header_text = re.sub(r'\d{4}-\d{1,2}-\d{1,2}', '', header_text)
                header_text = re.sub(r'\d{11}', '', header_text)
                # 查找2-4个连续的中文字符
                name_match = re.search(r'([\u4e00-\u9fa5]{2,4})', header_text)
                if name_match:
                    info["name"] = name_match.group(1)

        # 提取地址/位置（改进版）
        location_patterns = [
            r'(北京|上海|广州|深圳|杭州|成都|武汉|南京|西安|重庆|天津|青岛|大连|厦门|苏州)',
            r'([\u4e00-\u9fa5]{2,4}[省]|自治区)',
            r'广东省|浙江省|江苏省|四川省|湖北省|湖南省|山东省|河南省|河北省|福建省',
        ]
        for pattern in location_patterns:
            locations = re.findall(pattern, text)
            if locations:
                info["location"] = locations[0]
                break

        return info


# 全局解析器实例
_resume_parser = None


def get_resume_parser() -> ResumeParser:
    """获取简历解析器单例"""
    global _resume_parser
    if _resume_parser is None:
        _resume_parser = ResumeParser()
    return _resume_parser
