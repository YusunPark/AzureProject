"""
AI 서비스 모듈 - 간소화된 버전 (리팩토링용)
"""
import openai
import streamlit as st
import json
from typing import List, Dict, Any, Optional
from config import AI_CONFIG, TAVILY_CONFIG

class AIService:
    """AI 서비스 클래스"""
    
    def __init__(self):
        """AI 서비스 초기화"""
        self.client = None
        self._initialize_openai_client()
    
    def _initialize_openai_client(self):
        """OpenAI 클라이언트 초기화"""
        try:
            if AI_CONFIG.get("openai_api_key") and AI_CONFIG.get("openai_endpoint"):
                self.client = openai.AzureOpenAI(
                    api_key=AI_CONFIG["openai_api_key"],
                    azure_endpoint=AI_CONFIG["openai_endpoint"],
                    api_version=AI_CONFIG["api_version"]
                )
        except Exception as e:
            st.warning(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
    
    def refine_user_prompt(self, context: str) -> str:
        """사용자 프롬프트 고도화"""
        if not self.client:
            return context
            
        try:
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": "사용자의 요청을 더 구체적이고 명확하게 개선해주세요."},
                    {"role": "user", "content": f"다음 요청을 개선해주세요: {context}"}
                ],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            st.warning(f"프롬프트 고도화 실패: {str(e)}")
            return context
    
    def generate_search_queries(self, enhanced_prompt: str) -> Dict[str, str]:
        """검색 쿼리 생성"""
        if not self.client:
            return {"internal": enhanced_prompt, "external": enhanced_prompt}
            
        try:
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": "사내 문서 검색용과 외부 검색용 쿼리를 각각 생성해주세요. JSON 형식으로 반환하세요."},
                    {"role": "user", "content": f"요청: {enhanced_prompt}"}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            try:
                queries = json.loads(result)
                return {
                    "internal": queries.get("internal", enhanced_prompt),
                    "external": queries.get("external", enhanced_prompt)
                }
            except:
                return {"internal": enhanced_prompt, "external": enhanced_prompt}
                
        except Exception as e:
            st.warning(f"검색 쿼리 생성 실패: {str(e)}")
            return {"internal": enhanced_prompt, "external": enhanced_prompt}
    
    def search_external_references(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """외부 레퍼런스 검색 (Tavily 또는 더미 데이터)"""
        try:
            if TAVILY_CONFIG.get("api_key"):
                # Tavily API 사용 (실제 구현 시)
                return self._search_with_tavily(query, max_results)
            else:
                # 더미 데이터 반환
                return self._get_dummy_external_results(query, max_results)
        except Exception as e:
            st.warning(f"외부 검색 실패: {str(e)}")
            return []
    
    def _search_with_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Tavily를 사용한 외부 검색"""
        try:
            # Tavily API 사용 (requests 사용)
            import requests
            
            api_key = TAVILY_CONFIG.get("api_key")
            if not api_key:
                st.warning("Tavily API 키가 설정되지 않았습니다.")
                return self._get_dummy_external_results(query, max_results)
            
            # Tavily API 요청
            url = "https://api.tavily.com/search"
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "api_key": api_key,
                "query": query,
                "search_depth": TAVILY_CONFIG.get("search_depth", "basic"),
                "max_results": max_results,
                "include_answer": True,
                "include_raw_content": False
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                # Tavily 결과를 표준 형식으로 변환
                external_results = []
                if "results" in result:
                    for i, item in enumerate(result["results"][:max_results]):
                        external_results.append({
                            "id": f"tavily_{i}",
                            "title": item.get("title", "제목 없음"),
                            "content": item.get("content", "")[:500],  # 500자 제한
                            "url": item.get("url", ""),
                            "score": item.get("score", 0.5),
                            "source": "Tavily Search",
                            "source_detail": f"Tavily - {item.get('url', '')}",
                            "search_type": "external_web"
                        })
                
                st.info(f"✅ Tavily로 {len(external_results)}개의 외부 자료를 찾았습니다.")
                return external_results
            else:
                st.warning(f"Tavily API 요청 실패: {response.status_code}")
                return self._get_dummy_external_results(query, max_results)
                
        except Exception as e:
            st.warning(f"Tavily 검색 중 오류: {str(e)}")
            return self._get_dummy_external_results(query, max_results)
    
    def _get_dummy_external_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """더미 외부 검색 결과 (Tavily API 없을 때)"""
        import random
        
        # 더 다양하고 현실적인 더미 데이터
        dummy_templates = [
            {
                "source": "Wikipedia",
                "title_format": "{query} - 위키백과",
                "content_format": "{query}에 대한 백과사전적 정보입니다. 역사적 배경, 정의, 특징 등을 포함한 종합적인 개요를 제공합니다. 이는 검증된 정보원에서 수집된 신뢰할 수 있는 내용입니다.",
                "url_format": "https://ko.wikipedia.org/wiki/{query}"
            },
            {
                "source": "Stack Overflow",
                "title_format": "{query} 구현 방법 - 개발자 커뮤니티",
                "content_format": "{query}와 관련된 실제 개발 경험과 해결책을 공유하는 개발자들의 토론입니다. 코드 예제, 모범 사례, 일반적인 문제와 해결방법을 포함합니다.",
                "url_format": "https://stackoverflow.com/questions/tagged/{query}"
            },
            {
                "source": "Medium",
                "title_format": "{query} 트렌드 분석 - 전문가 블로그",
                "content_format": "{query}에 대한 최신 트렌드와 전문가 의견을 제공하는 기술 블로그입니다. 실무 경험을 바탕으로 한 인사이트와 향후 전망을 다룹니다.",
                "url_format": "https://medium.com/topic/{query}"
            },
            {
                "source": "GitHub",
                "title_format": "{query} 오픈소스 프로젝트",
                "content_format": "{query}와 관련된 오픈소스 프로젝트 및 코드 저장소입니다. 실제 구현 예제, 라이브러리, 도구 등을 포함하여 개발에 직접 활용할 수 있는 자료입니다.",
                "url_format": "https://github.com/topics/{query}"
            },
            {
                "source": "Academic Paper",
                "title_format": "{query} 연구 논문 - 학술 자료",
                "content_format": "{query}에 대한 학술적 연구 결과입니다. 체계적인 연구 방법론과 실증적 데이터를 바탕으로 한 전문적인 분석과 결론을 제공합니다.",
                "url_format": "https://scholar.google.com/scholar?q={query}"
            }
        ]
        
        results = []
        for i in range(min(max_results, len(dummy_templates))):
            template = dummy_templates[i]
            results.append({
                "id": f"dummy_ext_{i+1}",
                "title": template["title_format"].format(query=query),
                "content": template["content_format"].format(query=query),
                "url": template["url_format"].format(query=query.replace(" ", "-")),
                "score": 0.9 - (i * 0.15),
                "source": template["source"],
                "source_detail": f"{template['source']} (데모 데이터)",
                "search_type": "external_demo"
            })
        
        st.info(f"🔄 데모 모드: {len(results)}개의 더미 외부 자료 생성 (실제 환경에서는 Tavily API 사용)")
        return results
    
    def generate_comprehensive_analysis(self, query: str, internal_docs: List[Dict], external_docs: List[Dict], document_content: str = "") -> str:
        """종합 분석 결과 생성 - 문서 내용 포함"""
        if not self.client:
            return self._get_dummy_analysis(query, internal_docs, external_docs, document_content)
            
        try:
            # 분석할 문서 내용과 참고 자료를 포함한 완전한 컨텍스트 생성
            context = self._build_comprehensive_context(query, document_content, internal_docs, external_docs)
            
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": "주어진 문서 내용을 분석하고, 사내 문서와 외부 자료를 참고하여 포괄적이고 실용적인 분석 결과를 제공하세요."},
                    {"role": "user", "content": context}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
            
        except Exception as e:
            st.warning(f"종합 분석 생성 실패: {str(e)}")
            return self._get_dummy_analysis(query, internal_docs, external_docs, document_content)
    
    def _build_comprehensive_context(self, query: str, document_content: str, internal_docs: List[Dict], external_docs: List[Dict]) -> str:
        """포괄적인 분석용 컨텍스트 구성"""
        context = f"사용자 요청: {query}\n\n"
        
        # 분석 대상 문서 내용 (가장 중요!)
        if document_content and document_content.strip():
            context += f"===== 분석 대상 문서 내용 =====\n{document_content}\n\n"
        else:
            context += "===== 분석 대상 문서 내용 =====\n(문서 내용이 제공되지 않음)\n\n"
        
        # 사내 참고 문서
        if internal_docs:
            context += "===== 사내 참고 문서 =====\n"
            for i, doc in enumerate(internal_docs[:3], 1):
                title = doc.get('title', 'N/A')
                content = doc.get('content', '')[:300]  # 300자까지
                context += f"{i}. {title}\n{content}...\n\n"
        
        # 외부 참고 자료
        if external_docs:
            context += "===== 외부 참고 자료 =====\n"
            for i, doc in enumerate(external_docs[:3], 1):
                title = doc.get('title', 'N/A')
                content = doc.get('content', '')[:300]  # 300자까지
                context += f"{i}. {title}\n{content}...\n\n"
        
        context += "위의 문서 내용을 중심으로 분석하되, 참고 자료들을 활용하여 포괄적인 분석 결과를 제공해주세요."
        return context

    def _build_analysis_context(self, internal_docs: List[Dict], external_docs: List[Dict]) -> str:
        """기존 분석용 컨텍스트 구성 (하위 호환성)"""
        context = ""
        
        if internal_docs:
            context += "**사내 문서:**\n"
            for doc in internal_docs[:3]:  # 최대 3개만
                context += f"- {doc.get('title', 'N/A')}: {doc.get('content', '')[:200]}...\n"
        
        if external_docs:
            context += "\n**외부 자료:**\n"
            for doc in external_docs[:3]:  # 최대 3개만
                context += f"- {doc.get('title', 'N/A')}: {doc.get('content', '')[:200]}...\n"
        
        return context
    
    def _get_dummy_analysis(self, query: str, internal_docs: List[Dict], external_docs: List[Dict], document_content: str = "") -> str:
        """더미 분석 결과 - 문서 내용 포함"""
        doc_info = ""
        if document_content and document_content.strip():
            word_count = len(document_content.split())
            char_count = len(document_content)
            doc_info = f"\n\n**📄 분석된 문서 정보:**\n- 글자수: {char_count:,}자\n- 단어수: {word_count:,}단어\n- 문서 미리보기: {document_content[:200]}..."
        
        return f"""
## 📋 AI 분석 결과

**사용자 요청:** {query}{doc_info}

### 🔍 종합 분석
사내 문서 {len(internal_docs)}개와 외부 자료 {len(external_docs)}개를 참고하여 분석한 결과입니다.

### 💡 주요 인사이트
1. **핵심 포인트**: {query}와 관련하여 다음과 같은 중요한 점들이 발견되었습니다.
2. **사내 관점**: 우리 조직의 문서들에서는 이러한 접근 방식을 제시하고 있습니다.
3. **업계 동향**: 외부 자료들은 최신 트렌드와 모범 사례를 보여줍니다.

### 🎯 결론 및 권장사항
분석된 자료들을 종합하면, 다음과 같은 방향으로 진행하는 것이 좋겠습니다.

*(실제 AI 분석 결과는 OpenAI API 연결 후 제공됩니다)*
        """.strip()
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """AI 서비스 연결 테스트"""
        if not self.client:
            return {"available": False, "error": "OpenAI 클라이언트 초기화 실패"}
        
        try:
            # 간단한 테스트 요청
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return {"available": True, "model": AI_CONFIG["deployment_name"]}
        except Exception as e:
            return {"available": False, "error": str(e)}