"""
AI 서비스 모듈 - 간소화된 버전
핵심 기능만 유지하고 불필요한 코드 제거
"""
import openai
import streamlit as st
import json
import re
from datetime import datetime
from typing import List, Dict, Any
from tavily import TavilyClient
from config import AI_CONFIG, TAVILY_CONFIG, LANGSMITH_CONFIG, AZURE_SEARCH_CONFIG

class AIService:
    def __init__(self):
        self.ai_available = False
        self.search_available = False
        self.azure_search_available = False
        self._init_services()
    
    def _init_services(self):
        """서비스 초기화"""
        self._init_openai()
        self._init_tavily()
        self._init_azure_search()
    
    def _init_openai(self):
        """Azure OpenAI 초기화"""
        try:
            if AI_CONFIG["openai_api_key"] and AI_CONFIG["openai_endpoint"]:
                self.client = openai.AzureOpenAI(
                    azure_endpoint=AI_CONFIG["openai_endpoint"],
                    api_key=AI_CONFIG["openai_api_key"],
                    api_version=AI_CONFIG["api_version"]
                )
                self.ai_available = True
                print("✅ Azure OpenAI 초기화 성공")
            else:
                self.client = None
                print("⚠️ Azure OpenAI 설정이 없습니다.")
        except Exception as e:
            self.client = None
            print(f"⚠️ Azure OpenAI 초기화 실패: {e}")
    
    def _init_tavily(self):
        """Tavily 검색 초기화"""
        try:
            if TAVILY_CONFIG["api_key"]:
                self.tavily_client = TavilyClient(api_key=TAVILY_CONFIG["api_key"])
                self.search_available = True
            else:
                self.tavily_client = None
                print("⚠️ Tavily API 키가 없습니다.")
        except Exception as e:
            self.tavily_client = None
            print(f"⚠️ Tavily 초기화 실패: {e}")
    
    def _init_azure_search(self):
        """Azure Search 초기화"""
        try:
            if AZURE_SEARCH_CONFIG["endpoint"] and AZURE_SEARCH_CONFIG["admin_key"]:
                self.azure_search_available = True
                self.azure_search_endpoint = AZURE_SEARCH_CONFIG["endpoint"]
                self.azure_search_key = AZURE_SEARCH_CONFIG["admin_key"]
                self.azure_search_index = AZURE_SEARCH_CONFIG["index_name"]
                print("✅ Azure Search 초기화 성공")
            else:
                self.azure_search_available = False
                print("⚠️ Azure Search 설정이 없습니다.")
        except Exception as e:
            self.azure_search_available = False
            print(f"⚠️ Azure Search 초기화 실패: {e}")
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """AI 연결 상태 테스트"""
        result = {
            "ai_available": self.ai_available,
            "search_available": self.search_available,
            "endpoint": AI_CONFIG.get("openai_endpoint", "없음"),
            "model": AI_CONFIG.get("deployment_name", "없음"),
            "api_key_set": bool(AI_CONFIG.get("openai_api_key")),
            "tavily_key_set": bool(TAVILY_CONFIG.get("api_key"))
        }
        
        if self.ai_available:
            try:
                response = self.client.chat.completions.create(
                    model=AI_CONFIG["deployment_name"],
                    messages=[{"role": "user", "content": "안녕하세요."}],
                    max_tokens=50,
                    temperature=0.1
                )
                result["test_response"] = response.choices[0].message.content
                result["connection_test"] = "성공"
            except Exception as e:
                result["connection_test"] = f"실패: {str(e)}"
                result["test_response"] = None
        else:
            result["connection_test"] = "AI 사용 불가능"
            
        return result
    
    def enhance_user_prompt(self, user_input: str) -> str:
        """사용자 프롬프트 최적화"""
        if not self.ai_available:
            return f"[프롬프트 최적화] {user_input}"
        
        try:
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": "사용자 입력을 분석하여 더 구체적이고 검색에 유용한 프롬프트로 재작성해주세요."},
                    {"role": "user", "content": f"다음을 분석용 프롬프트로 최적화: {user_input}"}
                ],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"프롬프트 최적화 실패: {e}")
            return f"[최적화된 프롬프트] {user_input}"
    
    def search_internal_documents(self, query: str) -> List[Dict[str, Any]]:
        """사내 문서 검색"""
        if self.azure_search_available:
            return self._search_azure_search(query)
        else:
            return self._search_local_documents(query)
    
    def _search_azure_search(self, query: str) -> List[Dict[str, Any]]:
        """Azure Search 검색"""
        try:
            import requests
            
            search_url = f"{self.azure_search_endpoint}/indexes/{self.azure_search_index}/docs/search"
            headers = {
                'Content-Type': 'application/json',
                'api-key': self.azure_search_key
            }
            
            search_body = {
                "search": query,
                "top": 5
            }
            
            response = requests.post(search_url, headers=headers, json=search_body, 
                                   params={'api-version': AZURE_SEARCH_CONFIG["api_version"]})
            
            if response.status_code == 200:
                results = response.json().get('value', [])
                return [self._convert_azure_doc(doc, i) for i, doc in enumerate(results)]
            else:
                return self._search_local_documents(query)
        except Exception as e:
            print(f"Azure Search 실패: {e}")
            return self._search_local_documents(query)
    
    def _convert_azure_doc(self, doc: dict, index: int) -> Dict[str, Any]:
        """Azure Search 문서 변환"""
        return {
            "id": doc.get("id", f"azure_doc_{index}"),
            "title": doc.get("title", "제목 없음"),
            "content": doc.get("content", ""),
            "summary": doc.get("content", "")[:200] + "...",
            "source_detail": f"Azure AI Search - {self.azure_search_index}",
            "relevance_score": doc.get("@search.score", 1.0) / 10.0,
            "search_type": "azure_search"
        }
    
    def _search_local_documents(self, query: str) -> List[Dict[str, Any]]:
        """로컬 문서 검색"""
        try:
            with open('data/sample_documents.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = data.get("documents", [])[:3]
            for doc in documents:
                doc["search_type"] = "local"
                doc["source_detail"] = f"로컬 DB - {doc.get('source', 'Unknown')}"
            
            return documents
        except Exception:
            return [self._get_dummy_internal_doc(query)]
    
    def _get_dummy_internal_doc(self, query: str) -> Dict[str, Any]:
        """더미 사내 문서"""
        return {
            "id": "dummy_internal",
            "title": f"사내 정책 - {query[:20]}... 관련",
            "summary": f"{query[:30]}...와 관련된 사내 가이드라인입니다.",
            "content": f"사내에서 {query}에 대한 표준 절차를 정의한 문서입니다.",
            "source_detail": "사내 문서 시스템",
            "relevance_score": 0.8,
            "search_type": "dummy"
        }
    
    def search_external_references(self, query: str) -> List[Dict[str, Any]]:
        """외부 레퍼런스 검색"""
        if not self.search_available:
            return [self._get_dummy_external_doc(query)]
        
        try:
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            return [self._convert_tavily_doc(result, i) for i, result in enumerate(response.get("results", []))]
        except Exception as e:
            print(f"외부 검색 실패: {e}")
            return [self._get_dummy_external_doc(query)]
    
    def _convert_tavily_doc(self, result: dict, index: int) -> Dict[str, Any]:
        """Tavily 결과 변환"""
        return {
            "id": f"external_{index}",
            "title": result.get("title", "제목 없음"),
            "summary": result.get("content", "")[:200] + "...",
            "content": result.get("content", ""),
            "source_detail": result.get("url", ""),
            "url": result.get("url", ""),
            "relevance_score": result.get("score", 0.5),
            "search_type": "external"
        }
    
    def _get_dummy_external_doc(self, query: str) -> Dict[str, Any]:
        """더미 외부 문서"""
        return {
            "id": "dummy_external",
            "title": f"Best Practices - {query[:20]}...",
            "summary": f"{query[:30]}...에 대한 업계 모범사례입니다.",
            "content": f"업계에서 {query}와 관련된 성공 사례들을 정리한 자료입니다.",
            "source_detail": "External Reference",
            "url": "https://example.com",
            "relevance_score": 0.7,
            "search_type": "dummy"
        }
    
    def generate_optimized_analysis(self, enhanced_prompt: str, internal_docs: List[Dict], 
                                  external_docs: List[Dict], original_input: str) -> Dict[str, Any]:
        """통합 분석 결과 생성"""
        if not self.ai_available:
            return self._get_fallback_analysis(enhanced_prompt, internal_docs, external_docs)
        
        try:
            internal_summary = self._summarize_docs(internal_docs, "사내 문서")
            external_summary = self._summarize_docs(external_docs, "외부 레퍼런스")
            
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": "전문 분석가로서 사내 문서와 외부 레퍼런스를 종합하여 실용적인 분석 결과를 제공하세요."},
                    {"role": "user", "content": f"""
분석 요청: {original_input}
최적화된 범위: {enhanced_prompt}

사내 문서: {internal_summary}
외부 레퍼런스: {external_summary}

위 정보를 바탕으로 종합 분석 결과를 제공해주세요.
"""}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return {
                "title": "🎯 AI 종합 분석 결과",
                "content": response.choices[0].message.content,
                "internal_docs_count": len(internal_docs),
                "external_docs_count": len(external_docs),
                "confidence": 0.9,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"분석 생성 실패: {e}")
            return self._get_fallback_analysis(enhanced_prompt, internal_docs, external_docs)
    
    def _summarize_docs(self, docs: List[Dict], doc_type: str) -> str:
        """문서 요약"""
        if not docs:
            return f"{doc_type}: 관련 자료 없음"
        
        summaries = []
        for doc in docs[:3]:
            title = doc.get("title", "제목 없음")
            summary = doc.get("summary", "")[:100]
            summaries.append(f"- {title}: {summary}")
        
        return f"{doc_type} ({len(docs)}개):\n" + "\n".join(summaries)
    
    def _get_fallback_analysis(self, prompt: str, internal_docs: List[Dict], external_docs: List[Dict]) -> Dict[str, Any]:
        """폴백 분석 결과"""
        return {
            "title": "📋 기본 분석 결과",
            "content": f"""
## 📋 분석 결과

### 🎯 분석 요청
{prompt[:200]}...

### 📊 검색 결과
- 사내 문서: {len(internal_docs)}개
- 외부 레퍼런스: {len(external_docs)}개

### 💡 기본 분석
검색된 자료를 바탕으로 추가 분석이 필요합니다.

### 🔍 참고 자료
""" + "\n".join([f"- {doc.get('title', 'N/A')}" for doc in (internal_docs + external_docs)[:5]]),
            "internal_docs_count": len(internal_docs),
            "external_docs_count": len(external_docs),
            "confidence": 0.5,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def refine_text(self, text: str, style: str = "clear") -> str:
        """텍스트 다듬기"""
        if not self.ai_available:
            return f"[{style} 스타일로 개선] {text}"
        
        style_prompts = {
            "clear": "명확하고 이해하기 쉽게",
            "professional": "전문적이고 정확하게", 
            "concise": "간결하고 핵심적으로"
        }
        
        try:
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": f"다음 텍스트를 {style_prompts.get(style, '더 좋게')} 다듬어주세요."},
                    {"role": "user", "content": text}
                ],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[다듬기 실패] {text}"
    
    def structure_content(self, text: str, structure_type: str = "outline") -> str:
        """내용 구조화"""
        if not self.ai_available:
            return self._get_dummy_structure(text, structure_type)
        
        structure_prompts = {
            "outline": "목차와 소제목이 있는 개요 형식으로",
            "steps": "단계별 가이드 형식으로",
            "qa": "질문과 답변 형식으로"
        }
        
        try:
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": f"다음 내용을 {structure_prompts.get(structure_type, '체계적으로')} 구조화해주세요."},
                    {"role": "user", "content": text}
                ],
                max_tokens=800,
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return self._get_dummy_structure(text, structure_type)
    
    def get_ai_response(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """일반적인 AI 응답 생성 (누락된 메서드 추가)"""
        if not self.ai_available:
            return f"[AI 응답 생성 불가] 요청: {prompt[:100]}..."
        
        try:
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI 응답 생성 실패: {e}")
            return f"[AI 응답 실패] 요청에 대한 응답을 생성할 수 없습니다. 오류: {str(e)}"
    
    def _get_dummy_structure(self, text: str, structure_type: str) -> str:
        """더미 구조화 결과"""
        preview = text[:100] + "..." if len(text) > 100 else text
        
        if structure_type == "outline":
            return f"""# 주제 개요

## 1. 주요 내용
{preview}

## 2. 핵심 포인트
- 포인트 1
- 포인트 2

## 3. 결론
요약 정리"""
        elif structure_type == "steps":
            return f"""# 단계별 가이드

**1단계:** {preview}
**2단계:** 세부 실행
**3단계:** 완료 및 검료"""
        else:  # qa
            return f"""# Q&A 형식

**Q: 핵심은 무엇인가?**
A: {preview}

**Q: 어떻게 진행하나?**
A: 단계적 접근이 필요합니다."""