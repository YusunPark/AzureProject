"""
ai_analysis_orchestrator.py

AI 분석 4단계 순차 프로세스 오케스트레이터
- 1단계: 프롬프트 고도화
- 2단계: 검색 쿼리 생성
- 3단계: 사내/외부 레퍼런스 검색 (병렬)
- 4단계: 최종 분석 결과 생성

분석 모드: 전체 문서/선택 텍스트
진행 상황 표시, 레퍼런스 관리, 분석 취소 등 지원
"""
import os
import threading
from typing import List, Dict, Literal, Optional, Any
import time

from utils.azure_search_management import AzureSearchService
import requests
import openai
import streamlit as st
from config import AI_CONFIG

# 환경 변수에서 설정값 로드
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = AI_CONFIG["deployment_name"]

class AIAnalysisOrchestrator:
    def __init__(self, mode: Literal["full", "selection"] = "full"):
        self.mode = mode
        self.azure_search = AzureSearchService()
        self.cancelled = False
        self.progress = 0
        self.status = ""
        self.references: Dict[str, List[Dict[str, Any]]] = {"internal": [], "external": []}
        self.result: Optional[str] = None
        self.lock = threading.Lock()
        
        # Azure OpenAI 클라이언트 초기화
        self.openai_client = openai.AzureOpenAI(
            azure_endpoint=AI_CONFIG["openai_endpoint"],
            api_key=AI_CONFIG["openai_api_key"],
            api_version=AI_CONFIG["api_version"]
        )

    def cancel(self):
        with self.lock:
            self.cancelled = True

    def is_cancelled(self):
        with self.lock:
            return self.cancelled

    def run_analysis(self, user_input: str, selection: Optional[str] = None):
        self.progress = 0
        self.status = "1단계: 프롬프트 고도화"
        st.session_state["ai_analysis_progress"] = self.progress
        st.session_state["ai_analysis_status"] = self.status
        st.session_state["ai_analysis_cancelled"] = False
        st.session_state["ai_analysis_result"] = None
        st.session_state["ai_analysis_references"] = {"internal": [], "external": []}

        # 1단계: 프롬프트 고도화
        prompt = self._refine_prompt(user_input, selection)
        self.progress = 20
        st.session_state["ai_analysis_progress"] = self.progress
        st.session_state["ai_analysis_status"] = "2단계: 검색 쿼리 생성"
        if self.is_cancelled():
            return

        # 2단계: 검색 쿼리 생성
        internal_query, external_query = self._generate_queries(prompt)
        self.progress = 40
        st.session_state["ai_analysis_progress"] = self.progress
        st.session_state["ai_analysis_status"] = "3단계: 사내/외부 레퍼런스 검색"
        if self.is_cancelled():
            return

        # 3단계: 사내/외부 레퍼런스 검색 (병렬)
        internal_refs, external_refs = self._parallel_reference_search(internal_query, external_query)
        self.references = {"internal": internal_refs, "external": external_refs}
        st.session_state["ai_analysis_references"] = self.references
        self.progress = 70
        st.session_state["ai_analysis_progress"] = self.progress
        st.session_state["ai_analysis_status"] = "4단계: 최종 분석 결과 생성"
        if self.is_cancelled():
            return

        # 4단계: 최종 분석 결과 생성
        self.result = self._generate_final_result(prompt, internal_refs, external_refs)
        st.session_state["ai_analysis_result"] = self.result
        self.progress = 100
        st.session_state["ai_analysis_progress"] = self.progress
        st.session_state["ai_analysis_status"] = "분석 완료"

    def _refine_prompt(self, user_input: str, selection: Optional[str]) -> str:
        """1단계: 프롬프트 고도화 - GPT-4o를 활용한 사용자 입력 개선"""
        try:
            system_prompt = """당신은 AI 분석을 위한 프롬프트 최적화 전문가입니다.
사용자의 입력을 분석하여 더 명확하고 구체적인 프롬프트로 개선해주세요.

개선 기준:
1. 분석 목적과 방향성을 명확히 하기
2. 검색에 적합한 키워드 포함
3. 구체적이고 실행 가능한 질문으로 변환
4. 사내 문서와 외부 자료 모두에서 유용한 정보를 찾을 수 있도록 구성

입력된 내용을 바탕으로 개선된 프롬프트만 출력하세요."""

            user_prompt = f"사용자 입력: {user_input}"
            if self.mode == "selection" and selection:
                user_prompt += f"\n\n분석 대상 텍스트: {selection}"

            response = self.openai_client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            return enhanced_prompt
        
        except Exception as e:
            # 실패 시 기본 프롬프트 반환
            base_prompt = f"분석 목적: {user_input}"
            if self.mode == "selection" and selection:
                base_prompt += f"\n분석 대상 텍스트: {selection}"
            return base_prompt

    def _generate_queries(self, prompt: str) -> tuple[str, str]:
        """2단계: 검색 쿼리 생성 - 사내/외부 검색에 최적화된 쿼리 생성"""
        try:
            system_prompt = """당신은 검색 쿼리 최적화 전문가입니다.
주어진 프롬프트를 바탕으로 두 가지 검색 쿼리를 생성해주세요:

1. 사내 문서 검색용: 조직 내부의 문서, 정책, 가이드라인 등을 찾기 위한 쿼리
2. 외부 자료 검색용: 웹에서 최신 정보, 업계 동향, 기술 자료 등을 찾기 위한 쿼리

각 쿼리는 해당 검색 환경에 최적화되어야 하며, 핵심 키워드를 포함해야 합니다.

출력 형식:
사내검색: [사내 문서 검색 쿼리]
외부검색: [외부 자료 검색 쿼리]"""

            response = self.openai_client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"프롬프트: {prompt}"}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            
            # 결과 파싱
            internal_query = ""
            external_query = ""
            
            for line in result.split('\n'):
                if line.startswith('사내검색:'):
                    internal_query = line.replace('사내검색:', '').strip()
                elif line.startswith('외부검색:'):
                    external_query = line.replace('외부검색:', '').strip()
            
            # 파싱 실패 시 기본값
            if not internal_query:
                internal_query = prompt
            if not external_query:
                external_query = prompt
                
            return internal_query, external_query
            
        except Exception as e:
            # 실패 시 기본 쿼리 반환
            return prompt, prompt

    def _parallel_reference_search(self, internal_query: str, external_query: str):
        internal_refs, external_refs = [], []
        threads = []
        def search_internal():
            nonlocal internal_refs
            internal_refs = self._search_internal(internal_query)
        def search_external():
            nonlocal external_refs
            external_refs = self._search_external(external_query)
        t1 = threading.Thread(target=search_internal)
        t2 = threading.Thread(target=search_external)
        t1.start(); t2.start(); t1.join(); t2.join()
        return internal_refs, external_refs

    def _search_internal(self, query: str) -> List[Dict[str, Any]]:
        """사내 문서 검색: Azure AI Search를 통한 벡터/키워드 검색"""
        try:
            if not self.azure_search.available:
                return [{"title": "Azure Search 서비스 이용불가", "content": "Azure AI Search 서비스가 설정되지 않았습니다.", "url": ""}]
            
            # Azure AI Search에서 문서 검색
            search_results = self.azure_search.search_documents(query, top=5)
            
            # 결과를 표준화된 형태로 변환
            formatted_results = []
            for doc in search_results:
                formatted_results.append({
                    "title": doc.get("title", doc.get("filename", "제목없음")),
                    "content": doc.get("content", doc.get("summary", ""))[:500],  # 500자 제한
                    "url": doc.get("blob_url", ""),
                    "source": "internal",
                    "score": doc.get("@search.score", 0)
                })
            
            return formatted_results
            
        except Exception as e:
            return [{"title": "사내 검색 오류", "content": f"검색 중 오류 발생: {str(e)}", "url": "", "source": "internal"}]

    def _search_external(self, query: str) -> List[Dict[str, Any]]:
        """외부 자료 검색: Tavily API를 통한 실시간 웹 검색"""
        try:
            if not TAVILY_API_KEY:
                return [{"title": "Tavily API 키 없음", "content": "TAVILY_API_KEY가 설정되지 않았습니다.", "url": "", "source": "external"}]
            
            # Tavily API 호출
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": TAVILY_API_KEY,
                    "query": query,
                    "search_depth": "advanced",
                    "include_answer": True,
                    "include_raw_content": False,
                    "max_results": 5
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # 결과를 표준화된 형태로 변환
                formatted_results = []
                for item in results:
                    formatted_results.append({
                        "title": item.get("title", "제목없음"),
                        "content": item.get("content", "")[:500],  # 500자 제한
                        "url": item.get("url", ""),
                        "source": "external",
                        "score": item.get("score", 0)
                    })
                
                return formatted_results
            else:
                return [{"title": "Tavily API 오류", "content": f"HTTP {response.status_code}: {response.text}", "url": "", "source": "external"}]
                
        except requests.exceptions.Timeout:
            return [{"title": "Tavily 검색 시간초과", "content": "외부 검색 요청이 시간 초과되었습니다.", "url": "", "source": "external"}]
        except Exception as e:
            return [{"title": "Tavily 검색 예외", "content": f"검색 중 오류 발생: {str(e)}", "url": "", "source": "external"}]

    def _generate_final_result(self, prompt: str, internal_refs: List[Dict[str, Any]], external_refs: List[Dict[str, Any]]) -> str:
        """4단계: 최종 분석 결과 생성 - 모든 정보를 종합한 AI 분석"""
        try:
            # 레퍼런스 정보 정리
            internal_context = ""
            for ref in internal_refs[:3]:  # 상위 3개만
                internal_context += f"- {ref.get('title', '제목없음')}: {ref.get('content', '')[:200]}...\n"
            
            external_context = ""
            for ref in external_refs[:3]:  # 상위 3개만
                external_context += f"- {ref.get('title', '제목없음')}: {ref.get('content', '')[:200]}...\n"

            system_prompt = """당신은 전문 AI 분석가입니다.
사용자의 요청과 수집된 사내 문서 및 외부 자료를 종합하여 완전하고 실용적인 분석 결과를 제공해주세요.

분석 결과는 다음 구조로 작성하세요:
1. 🎯 분석 요약
2. 📋 주요 발견사항 (3-5개)
3. 💡 실행 가능한 제안사항
4. ⚠️ 주의사항 및 고려사항
5. 🔗 참고자료 요약

사내 문서와 외부 자료의 정보를 균형있게 활용하고, 구체적이고 실행 가능한 내용으로 작성해주세요."""

            user_prompt = f"""
분석 요청: {prompt}

사내 문서 정보:
{internal_context if internal_context else "사내 문서 없음"}

외부 자료 정보:
{external_context if external_context else "외부 자료 없음"}

위 정보를 바탕으로 종합적인 분석 결과를 제공해주세요."""

            response = self.openai_client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.4
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # 실패 시 기본 요약 반환
            summary = f"## 📊 AI 분석 결과\n\n"
            summary += f"**분석 요청**: {prompt}\n\n"
            summary += f"**수집된 자료**:\n"
            summary += f"- 사내 문서: {len(internal_refs)}건\n"
            summary += f"- 외부 자료: {len(external_refs)}건\n\n"
            summary += f"**오류 정보**: 최종 분석 생성 중 오류 발생 ({str(e)})\n\n"
            
            if internal_refs:
                summary += "**사내 문서 예시**:\n"
                summary += f"- {internal_refs[0].get('title', '제목없음')}: {internal_refs[0].get('content', '')[:200]}...\n\n"
            
            if external_refs:
                summary += "**외부 자료 예시**:\n" 
                summary += f"- {external_refs[0].get('title', '제목없음')}: {external_refs[0].get('content', '')[:200]}...\n"
            
            return summary

# Streamlit 연동 함수 (UI/세션 상태 관리)
def run_ai_analysis(user_input: str, mode: Literal["full", "selection"] = "full", selection: Optional[str] = None):
    """AI 분석을 비동기로 실행하고 세션 상태를 업데이트"""
    
    def analysis_worker():
        orchestrator = AIAnalysisOrchestrator(mode=mode)
        try:
            orchestrator.run_analysis(user_input, selection)
        except Exception as e:
            st.session_state["ai_analysis_status"] = f"분석 중 오류 발생: {str(e)}"
            st.session_state["ai_analysis_progress"] = 0
    
    # 백그라운드에서 분석 실행
    if "ai_analysis_thread" not in st.session_state or not st.session_state["ai_analysis_thread"].is_alive():
        st.session_state["ai_analysis_cancelled"] = False
        st.session_state["ai_analysis_progress"] = 0
        st.session_state["ai_analysis_status"] = "분석 시작..."
        
        analysis_thread = threading.Thread(target=analysis_worker)
        st.session_state["ai_analysis_thread"] = analysis_thread
        analysis_thread.start()
        
        # 약간의 지연 후 UI 업데이트를 위해 rerun
        time.sleep(0.5)
        st.rerun()
