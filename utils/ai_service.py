"""
AI 서비스 모듈 - Azure OpenAI와 Tavily 검색을 사용
"""
import openai
import time
import streamlit as st
from typing import List, Dict, Any
from tavily import TavilyClient
from config import AI_CONFIG, TAVILY_CONFIG

class AIService:
    def __init__(self):
        # Azure OpenAI 설정
        self.client = openai.AzureOpenAI(
            azure_endpoint=AI_CONFIG["openai_endpoint"],
            api_key=AI_CONFIG["openai_api_key"],
            api_version=AI_CONFIG["api_version"]
        )
        
        # Tavily 검색 클라이언트
        self.tavily_client = TavilyClient(api_key=TAVILY_CONFIG["api_key"]) if TAVILY_CONFIG["api_key"] else None
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """텍스트 분석"""
        if not text.strip():
            return {"keywords": [], "topic": "", "context": "", "summary": ""}
        
        try:
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": """당신은 문서 분석 전문가입니다. 
                    주어진 텍스트를 분석하여 다음을 JSON 형식으로 제공하세요:
                    - keywords: 핵심 키워드 리스트 (최대 10개)
                    - topic: 주요 주제 (한 문장)
                    - summary: 요약 (2-3 문장)
                    - context: 문맥 정보"""},
                    {"role": "user", "content": f"다음 텍스트를 분석해주세요:\n\n{text}"}
                ],
                max_tokens=AI_CONFIG["max_tokens"],
                temperature=AI_CONFIG["temperature"]
            )
            
            content = response.choices[0].message.content
            
            # 키워드, 주제, 요약 추출
            keywords = self._extract_keywords(text, content)
            topic = self._extract_topic(content)
            summary = self._extract_summary(content)
            
            return {
                "keywords": keywords,
                "topic": topic,
                "summary": summary,
                "context": content,
                "original_text": text
            }
            
        except Exception as e:
            st.error(f"AI 분석 중 오류 발생: {str(e)}")
            return {
                "keywords": text.split()[:5],
                "topic": "분석 실패",
                "summary": "텍스트 분석에 실패했습니다.",
                "context": "",
                "original_text": text
            }
    
    def search_related_documents(self, query: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Tavily를 사용한 관련 문서 검색"""
        if not self.tavily_client:
            return self._get_dummy_search_results(query, keywords)
        
        try:
            # 검색 쿼리 최적화
            search_query = query
            if keywords:
                search_query += " " + " ".join(keywords[:3])
            
            # Tavily 검색 실행
            response = self.tavily_client.search(
                query=search_query,
                search_depth=TAVILY_CONFIG["search_depth"],
                max_results=TAVILY_CONFIG["max_results"]
            )
            
            # 결과 변환
            documents = []
            for i, result in enumerate(response.get("results", [])):
                doc = {
                    "id": i + 1,
                    "title": result.get("title", "제목 없음"),
                    "summary": result.get("content", "")[:200] + "...",
                    "content": result.get("content", ""),
                    "source": result.get("url", ""),
                    "relevance_score": result.get("score", 0.5),
                    "keywords": keywords[:5] if keywords else []
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            st.warning(f"검색 중 오류 발생: {str(e)}")
            return self._get_dummy_search_results(query, keywords)
    
    def refine_text(self, text: str, style: str = "clear") -> str:
        """텍스트 다듬기"""
        style_prompts = {
            "clear": "명확하고 이해하기 쉽게 다듬어주세요.",
            "professional": "전문적이고 정확한 표현으로 다듬어주세요.",
            "concise": "간결하고 핵심적인 내용으로 다듬어주세요."
        }
        
        try:
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": f"다음 텍스트를 {style_prompts.get(style, '더 좋게')} 원본의 의미를 유지하면서 개선해주세요."},
                    {"role": "user", "content": text}
                ],
                max_tokens=min(AI_CONFIG["max_tokens"], len(text.split()) * 2),
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"텍스트 다듬기 중 오류 발생: {str(e)}")
            return text
    
    def structure_content(self, text: str, structure_type: str = "outline") -> str:
        """내용 구조화"""
        structure_prompts = {
            "outline": "다음 내용을 목차와 소제목이 있는 체계적인 개요 형식으로 구조화해주세요.",
            "steps": "다음 내용을 단계별 가이드 형식(1단계, 2단계...)으로 구조화해주세요.",
            "qa": "다음 내용을 질문과 답변(Q&A) 형식으로 구조화해주세요."
        }
        
        try:
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": structure_prompts.get(structure_type, "다음 내용을 체계적으로 구조화해주세요.")},
                    {"role": "user", "content": text}
                ],
                max_tokens=AI_CONFIG["max_tokens"],
                temperature=0.4
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"내용 구조화 중 오류 발생: {str(e)}")
            return text
    
    def _extract_keywords(self, original_text: str, ai_response: str) -> List[str]:
        """키워드 추출"""
        # AI 응답에서 키워드를 찾거나, 원본 텍스트에서 추출
        words = original_text.split()
        # 간단한 키워드 추출 (실제로는 더 정교한 알고리즘 사용)
        keywords = []
        for word in words:
            clean_word = word.strip('.,!?:;"()[]{}').lower()
            if len(clean_word) > 2 and clean_word not in ['있는', '있어', '그리고', '하지만', '그러나']:
                keywords.append(clean_word)
        
        return list(set(keywords))[:10]
    
    def _extract_topic(self, content: str) -> str:
        """주제 추출"""
        lines = content.split('\n')
        for line in lines:
            if '주제' in line or 'topic' in line.lower():
                return line.strip()
        return lines[0][:50] if lines else "주제 추출 실패"
    
    def _extract_summary(self, content: str) -> str:
        """요약 추출"""
        lines = content.split('\n')
        summary_lines = []
        for line in lines:
            if '요약' in line or 'summary' in line.lower():
                summary_lines.append(line.strip())
        
        if summary_lines:
            return ' '.join(summary_lines)
        else:
            return content[:100] + "..." if len(content) > 100 else content
    
    def _get_dummy_search_results(self, query: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """더미 검색 결과 (Tavily API가 없을 때) - 실제 샘플 데이터 사용"""
        try:
            import json
            with open('data/sample_documents.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = data.get("documents", [])
            
            # 키워드 기반 필터링 및 관련도 점수 계산
            if keywords:
                filtered_docs = []
                for doc in documents:
                    relevance = 0
                    doc_keywords = doc.get("keywords", [])
                    
                    # 키워드 매칭
                    for keyword in keywords:
                        if any(keyword.lower() in dk.lower() for dk in doc_keywords):
                            relevance += 0.2
                        if keyword.lower() in doc["title"].lower():
                            relevance += 0.3
                        if keyword.lower() in doc["summary"].lower():
                            relevance += 0.1
                    
                    # 쿼리 매칭
                    if query.lower() in doc["title"].lower():
                        relevance += 0.3
                    if query.lower() in doc["content"].lower():
                        relevance += 0.1
                    
                    if relevance > 0:
                        doc["relevance_score"] = min(1.0, relevance)
                        filtered_docs.append(doc)
                
                # 관련도 순으로 정렬
                filtered_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
                return filtered_docs[:5]  # 최대 5개
            
            # 키워드가 없으면 전체 문서 반환
            for doc in documents:
                doc["relevance_score"] = 0.7  # 기본 점수
            
            return documents[:3]  # 최대 3개
            
        except Exception as e:
            # 파일 로드 실패시 기본 더미 데이터
            return [
                {
                    "id": 1,
                    "title": f"'{query}' 관련 문서",
                    "summary": f"{query}에 대한 포괄적인 분석과 설명을 제공하는 문서입니다.",
                    "content": f"이 문서는 {query}에 대해 자세히 설명하고 있으며, 관련된 개념들과 실제 적용 사례들을 포함하고 있습니다.",
                    "source": "Sample Database",
                    "relevance_score": 0.9,
                    "keywords": keywords[:5] if keywords else []
                }
            ]