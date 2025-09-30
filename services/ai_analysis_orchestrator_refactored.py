"""
개선된 AI 분석 오케스트레이터
4단계 AI 분석 프로세스를 담당하는 핵심 서비스
"""
import streamlit as st
import time
from typing import Dict, List, Any, Optional, Tuple
import hashlib

from core.constants import UIConstants, MessageConstants
from core.utils import show_message, create_progress_tracker, update_progress
from core.exceptions import AIAnalysisException
from utils.ai_service import AIService
from services.document_management_service import DocumentManagementService

class AIAnalysisOrchestrator:
    """AI 분석 오케스트레이터 - 4단계 프로세스 관리"""
    
    def __init__(self, mode: str = "full"):
        """
        초기화
        Args:
            mode: 분석 모드 ("full", "selection", "quick")
        """
        self.mode = mode
        self.ai_service = AIService()
        self.doc_manager = DocumentManagementService()
    
    def run_complete_analysis(self, user_input: str, selection: str = None) -> Dict[str, Any]:
        """
        완전한 4단계 AI 분석 프로세스 실행
        
        Args:
            user_input: 사용자 입력
            selection: 선택된 텍스트 (옵션)
            
        Returns:
            분석 결과 딕셔너리
        """
        # 중복 실행 방지
        input_hash = self._generate_input_hash(user_input, selection)
        if self._is_duplicate_analysis(input_hash):
            st.info("이미 분석된 내용입니다. 기존 결과를 표시합니다.")
            return self._get_cached_result(input_hash)
        
        try:
            # 진행 상황 추적기 초기화
            tracker = create_progress_tracker(4)
            
            st.markdown("### 🔄 AI 분석 4단계 프로세스")
            
            # 1단계: 프롬프트 고도화
            enhanced_prompt = self._execute_step_1(tracker, user_input, selection)
            
            # 2단계: 검색 쿼리 생성
            internal_query, external_query = self._execute_step_2(tracker, enhanced_prompt)
            
            # 3단계: 병렬 검색
            internal_refs, external_refs = self._execute_step_3(tracker, internal_query, external_query)
            
            # 4단계: 최종 분석 결과 생성
            final_result = self._execute_step_4(tracker, enhanced_prompt, internal_refs, external_refs)
            
            # 결과 캐싱 및 반환
            analysis_result = {
                'result': final_result,
                'internal_refs': internal_refs,
                'external_refs': external_refs,
                'enhanced_prompt': enhanced_prompt,
                'queries': {'internal': internal_query, 'external': external_query}
            }
            
            self._cache_result(input_hash, analysis_result)
            return analysis_result
            
        except Exception as e:
            st.error(f"❌ 분석 프로세스 중 치명적 오류: {str(e)}")
            raise AIAnalysisException("complete_analysis", str(e))
    
    def _execute_step_1(self, tracker: Dict, user_input: str, selection: str = None) -> str:
        """1단계: 프롬프트 고도화 실행"""
        st.markdown("#### 🔄 1단계: 프롬프트 고도화")
        update_progress(tracker, 0, "🧠 사용자 입력을 AI가 더 잘 이해할 수 있도록 개선 중...")
        
        try:
            enhanced_prompt = self._refine_prompt(user_input, selection)
            update_progress(tracker, 1, "✅ 1단계 완료: 프롬프트 고도화")
            st.success("✅ 1단계 완료: 프롬프트 고도화")
            
            with st.expander("🔍 고도화된 프롬프트 확인"):
                st.markdown(f"**원본 입력:**\n{user_input}")
                if selection:
                    st.markdown(f"**선택된 텍스트:**\n{selection}")
                st.markdown(f"**AI 고도화 프롬프트:**\n{enhanced_prompt}")
            
            return enhanced_prompt
            
        except Exception as e:
            raise AIAnalysisException("prompt_enhancement", str(e))
    
    def _execute_step_2(self, tracker: Dict, enhanced_prompt: str) -> Tuple[str, str]:
        """2단계: 검색 쿼리 생성 실행"""
        st.markdown("#### 🔍 2단계: 검색 쿼리 생성")
        update_progress(tracker, 1, "🔍 사내/외부 검색에 최적화된 쿼리 생성 중...")
        
        try:
            internal_query, external_query = self._generate_queries(enhanced_prompt)
            update_progress(tracker, 2, "✅ 2단계 완료: 검색 쿼리 생성")
            st.success("✅ 2단계 완료: 검색 쿼리 생성")
            
            with st.expander("🔍 생성된 검색 쿼리 확인"):
                st.markdown(f"**사내 문서 검색 쿼리:**\n{internal_query}")
                st.markdown(f"**외부 자료 검색 쿼리:**\n{external_query}")
            
            return internal_query, external_query
            
        except Exception as e:
            raise AIAnalysisException("query_generation", str(e))
    
    def _execute_step_3(self, tracker: Dict, internal_query: str, external_query: str) -> Tuple[List[Dict], List[Dict]]:
        """3단계: 병렬 검색 실행 - 150자 미리보기와 함께"""
        st.markdown("#### � 3단계: 사내/외부 레퍼런스 병렬 검색")
        update_progress(tracker, 2, "📚 사내 문서 및 외부 자료를 동시 검색 중...")
        
        try:
            internal_refs, external_refs = self._parallel_reference_search(internal_query, external_query)
            update_progress(tracker, 3, f"✅ 3단계 완료: 사내 문서 {len(internal_refs)}개, 외부 자료 {len(external_refs)}개 발견")
            st.success(f"✅ 3단계 완료: 사내 문서 {len(internal_refs)}개, 외부 자료 {len(external_refs)}개 발견")
            
            # 검색 결과 상세 미리보기 (150자씩)
            self._display_enhanced_search_preview(internal_refs, external_refs)
            
            return internal_refs, external_refs
            
        except Exception as e:
            raise AIAnalysisException("parallel_search", str(e))
    
    def _execute_step_4(self, tracker: Dict, enhanced_prompt: str, internal_refs: List[Dict], external_refs: List[Dict]) -> str:
        """4단계: 최종 분석 결과 생성"""
        st.markdown("#### 🔄 4단계: 최종 분석 결과 생성")
        update_progress(tracker, 3, "🤖 모든 정보를 종합하여 최종 AI 분석 결과 생성 중...")
        
        try:
            # 분석 대상 문서 내용 가져오기
            document_content = self._get_analysis_target_content()
            final_result = self._generate_final_result(enhanced_prompt, internal_refs, external_refs, document_content)
            update_progress(tracker, 4, "✅ 모든 단계 완료!")
            st.success("✅ 4단계 완료: 최종 분석 결과 생성")
            
            return final_result
            
        except Exception as e:
            raise AIAnalysisException("result_generation", str(e))
    
    def _refine_prompt(self, user_input: str, selection: str = None) -> str:
        """프롬프트 고도화"""
        # 분석 대상 문서 내용 확인
        if selection and selection.strip():
            # 분석할 실제 문서 내용이 있는 경우
            context = f"사용자 요청: {user_input}\n\n분석 대상 문서 내용:\n{selection[:2000]}..."
            if len(selection) > 2000:
                context += f"\n(문서 총 길이: {len(selection):,}자)"
        else:
            # 문서 내용이 없는 경우 현재 세션의 문서 내용 시도
            document_content = st.session_state.get('document_content', '')
            if document_content and document_content.strip():
                context = f"사용자 요청: {user_input}\n\n분석 대상 문서 내용:\n{document_content[:2000]}..."
                if len(document_content) > 2000:
                    context += f"\n(문서 총 길이: {len(document_content):,}자)"
            else:
                context = f"사용자 요청: {user_input}\n\n주의: 분석할 문서 내용이 제공되지 않았습니다."
        
        try:
            return self.ai_service.refine_user_prompt(context)
        except Exception as e:
            st.warning(f"프롬프트 고도화 실패, 원본 사용: {str(e)}")
            return user_input
    
    def _generate_queries(self, enhanced_prompt: str) -> Tuple[str, str]:
        """검색 쿼리 생성"""
        try:
            queries = self.ai_service.generate_search_queries(enhanced_prompt)
            internal_query = queries.get('internal', enhanced_prompt)
            external_query = queries.get('external', enhanced_prompt)
            return internal_query, external_query
        except Exception as e:
            st.warning(f"검색 쿼리 생성 실패, 원본 사용: {str(e)}")
            return enhanced_prompt, enhanced_prompt
    
    def _parallel_reference_search(self, internal_query: str, external_query: str) -> Tuple[List[Dict], List[Dict]]:
        """병렬 레퍼런스 검색"""
        internal_refs = []
        external_refs = []
        
        # 사내 문서 검색
        try:
            docs = self.doc_manager.search_training_documents(internal_query, top=10)
            internal_refs = self._convert_docs_for_ai(docs)
        except Exception as e:
            st.warning(f"사내 문서 검색 실패: {str(e)}")
        
        # 외부 자료 검색
        try:
            external_results = self.ai_service.search_external_references(external_query)
            external_refs = external_results if external_results else []
        except Exception as e:
            st.warning(f"외부 자료 검색 실패: {str(e)}")
        
        return internal_refs, external_refs
    
    def _get_analysis_target_content(self) -> str:
        """분석 대상 문서 내용 가져오기"""
        # 현재 세션에 저장된 분석 텍스트 확인
        analysis_text = st.session_state.get('analysis_text', '')
        
        if analysis_text and analysis_text.strip():
            return analysis_text
        
        # 현재 문서 내용 확인
        document_content = st.session_state.get('document_content', '')
        if document_content and document_content.strip():
            return document_content
        
        # 선택된 텍스트 확인
        selected_text = st.session_state.get('selected_text', '')
        if selected_text and selected_text.strip():
            return selected_text
        
        return ""

    def _generate_final_result(self, enhanced_prompt: str, internal_refs: List[Dict], external_refs: List[Dict], document_content: str = "") -> str:
        """최종 분석 결과 생성 - 문서 내용 포함"""
        try:
            return self.ai_service.generate_comprehensive_analysis(
                query=enhanced_prompt,
                internal_docs=internal_refs,
                external_docs=external_refs,
                document_content=document_content  # 실제 분석할 문서 내용 추가
            )
        except Exception as e:
            raise AIAnalysisException("final_result", f"최종 결과 생성 실패: {str(e)}")
    
    def _convert_docs_for_ai(self, docs: List[Dict]) -> List[Dict]:
        """문서 관리 서비스의 문서 형식을 AI 서비스 형식으로 변환"""
        converted_docs = []
        for doc in docs:
            converted_doc = {
                "id": doc.get("file_id", "unknown"),
                "title": doc.get("title", "제목 없음"),
                "content": doc.get("content", ""),
                "summary": doc.get("summary", ""),
                "source_detail": f"사내 문서 - {doc.get('filename', 'Unknown')}",
                "relevance_score": doc.get("search_score", 0.5) / 10 if doc.get("search_score") else 0.5,
                "search_type": "company_docs"
            }
            converted_docs.append(converted_doc)
        return converted_docs
    
    def _display_enhanced_search_preview(self, internal_refs: List[Dict], external_refs: List[Dict]):
        """검색 결과 상세 미리보기 표시 (150자씩)"""
        with st.expander("🔍 검색된 레퍼런스 미리보기", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📁 사내 문서 결과**")
                if internal_refs:
                    for i, doc in enumerate(internal_refs[:3], 1):
                        title = doc.get('title', 'N/A')
                        content = doc.get('content', '')
                        
                        st.markdown(f"**{i}. {title}**")
                        if content:
                            preview = content[:150]
                            if len(content) > 150:
                                preview += "..."
                            st.markdown(f"*{preview}*")
                        st.markdown("---")
                else:
                    st.markdown("*검색된 사내 문서가 없습니다.*")
                    
            with col2:
                st.markdown("**🌐 외부 자료 결과**")
                if external_refs:
                    for i, doc in enumerate(external_refs[:3], 1):
                        title = doc.get('title', 'N/A')
                        content = doc.get('content', '')
                        
                        st.markdown(f"**{i}. {title}**")
                        if content:
                            preview = content[:150]
                            if len(content) > 150:
                                preview += "..."
                            st.markdown(f"*{preview}*")
                        st.markdown("---")
                else:
                    st.markdown("*검색된 외부 자료가 없습니다.*")
    
    def _generate_input_hash(self, user_input: str, selection: str = None) -> str:
        """입력 해시 생성"""
        combined_input = user_input + (selection or "")
        return hashlib.md5(combined_input.encode()).hexdigest()
    
    def _is_duplicate_analysis(self, input_hash: str) -> bool:
        """중복 분석 확인"""
        return st.session_state.get('last_analysis_hash') == input_hash
    
    def _cache_result(self, input_hash: str, result: Dict[str, Any]):
        """결과 캐싱"""
        st.session_state.last_analysis_hash = input_hash
        st.session_state.ai_analysis_references = {
            "internal": result['internal_refs'], 
            "external": result['external_refs']
        }
        st.session_state.ai_analysis_result = result['result']
    
    def _get_cached_result(self, input_hash: str) -> Dict[str, Any]:
        """캐시된 결과 반환"""
        return {
            'result': st.session_state.get('ai_analysis_result', ''),
            'internal_refs': st.session_state.get('ai_analysis_references', {}).get('internal', []),
            'external_refs': st.session_state.get('ai_analysis_references', {}).get('external', [])
        }