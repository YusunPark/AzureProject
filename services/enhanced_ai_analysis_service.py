"""
향상된 AI 분석 서비스
사용자 요구사항에 따른 4단계 순차 분석 프로세스 구현
"""

import streamlit as st
import time
from typing import Dict, List, Any, Optional
from utils.ai_service import AIService
from services.document_management_service import DocumentManagementService


class EnhancedAIAnalysisService:
    """향상된 AI 분석 서비스"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.doc_manager = DocumentManagementService()
        
    def run_step_by_step_analysis(self, user_input: str) -> Dict[str, Any]:
        """
        4단계 순차 AI 분석 프로세스
        1. 프롬프트 고도화
        2. 쿼리 생성
        3. 사내/외부 레퍼런스 검색 (병렬)
        4. 최종 분석 결과 생성
        """
        
        # 분석 결과 초기화
        analysis_results = {
            "step1_enhanced_prompt": None,
            "step2_search_queries": None,
            "step3_internal_references": [],
            "step3_external_references": [],
            "step4_final_analysis": None,
            "error": None,
            "completed_steps": 0
        }
        
        try:
            # 1단계: 프롬프트 고도화
            st.write("### 🔄 1단계: 프롬프트 고도화")
            with st.spinner("사용자 입력을 AI가 더 잘 이해할 수 있도록 프롬프트를 개선하고 있습니다..."):
                enhanced_prompt = self._enhance_user_prompt(user_input)
                analysis_results["step1_enhanced_prompt"] = enhanced_prompt
                analysis_results["completed_steps"] = 1
                
            self._display_step_result("1단계", enhanced_prompt, "프롬프트 고도화")
            
            # 2단계: 검색 쿼리 생성
            st.write("### 🔄 2단계: 검색 쿼리 생성")
            with st.spinner("레퍼런스 검색을 위한 최적화된 쿼리를 생성하고 있습니다..."):
                search_queries = self._generate_search_queries(enhanced_prompt)
                analysis_results["step2_search_queries"] = search_queries
                analysis_results["completed_steps"] = 2
                
            self._display_step_result("2단계", search_queries, "검색 쿼리")
            
            # 3단계: 사내/외부 레퍼런스 검색 (병렬 처리)
            st.write("### 🔄 3단계: 레퍼런스 검색")
            
            # 3-1: 사내 문서 검색
            st.write("#### 📁 사내 문서 검색")
            with st.spinner("사내 문서 데이터베이스에서 관련 자료를 검색하고 있습니다..."):
                internal_refs = self._search_internal_references(search_queries)
                analysis_results["step3_internal_references"] = internal_refs
                
            st.success(f"✅ 사내 문서 {len(internal_refs)}개 발견")
            
            # 3-2: 외부 레퍼런스 검색
            st.write("#### 🌐 외부 레퍼런스 검색")
            with st.spinner("외부 웹에서 관련 레퍼런스를 검색하고 있습니다..."):
                external_refs = self._search_external_references(search_queries)
                analysis_results["step3_external_references"] = external_refs
                analysis_results["completed_steps"] = 3
                
            st.success(f"✅ 외부 레퍼런스 {len(external_refs)}개 발견")
            
            # 검색 결과 요약 표시
            self._display_reference_summary(internal_refs, external_refs)
            
            # 4단계: 최종 분석 결과 생성
            st.write("### 🔄 4단계: 최종 분석 결과 생성")
            with st.spinner("검색된 레퍼런스를 종합하여 최종 분석 결과를 생성하고 있습니다..."):
                final_analysis = self._generate_final_analysis(
                    user_input, enhanced_prompt, internal_refs, external_refs
                )
                analysis_results["step4_final_analysis"] = final_analysis
                analysis_results["completed_steps"] = 4
                
            self._display_step_result("4단계", final_analysis, "최종 분석")
            
            # 세션 상태에 결과 저장
            self._save_results_to_session(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            st.error(f"❌ 분석 중 오류 발생: {str(e)}")
            analysis_results["error"] = str(e)
            return analysis_results
    
    def _enhance_user_prompt(self, user_input: str) -> str:
        """1단계: 사용자 프롬프트 고도화"""
        try:
            enhanced = self.ai_service.enhance_user_prompt(user_input)
            return enhanced
        except Exception as e:
            st.warning(f"프롬프트 고도화 실패: {e}")
            return user_input  # 원본 반환
    
    def _generate_search_queries(self, enhanced_prompt: str) -> Dict[str, List[str]]:
        """2단계: 검색 쿼리 생성"""
        try:
            # AI를 통해 최적화된 검색 쿼리들 생성
            queries_prompt = f"""
다음 내용을 바탕으로 효과적인 검색 쿼리들을 생성해주세요:

{enhanced_prompt}

다음 형태로 응답해주세요:
1. 사내문서용 키워드 (3-5개)
2. 외부검색용 키워드 (3-5개)
3. 핵심 개념어 (2-3개)
"""
            
            response = self.ai_service.get_ai_response(queries_prompt)
            
            # 간단한 파싱 (실제 구현에서는 더 정교하게)
            lines = response.split('\n')
            internal_queries = []
            external_queries = []
            core_concepts = []
            
            current_section = None
            for line in lines:
                line = line.strip()
                if '사내문서' in line:
                    current_section = 'internal'
                elif '외부검색' in line:
                    current_section = 'external'
                elif '핵심' in line:
                    current_section = 'core'
                elif line and line.startswith(('-', '•', '*')):
                    clean_line = line.lstrip('-•* ').strip()
                    if current_section == 'internal':
                        internal_queries.append(clean_line)
                    elif current_section == 'external':
                        external_queries.append(clean_line)
                    elif current_section == 'core':
                        core_concepts.append(clean_line)
            
            # 기본 쿼리 추가 (AI가 제대로 파싱되지 않은 경우)
            if not internal_queries:
                internal_queries = [enhanced_prompt[:50]]
            if not external_queries:
                external_queries = [enhanced_prompt[:50]]
            
            return {
                "internal_queries": internal_queries[:5],
                "external_queries": external_queries[:5],
                "core_concepts": core_concepts[:3],
                "original_query": enhanced_prompt
            }
            
        except Exception as e:
            st.warning(f"쿼리 생성 실패: {e}")
            return {
                "internal_queries": [enhanced_prompt[:50]],
                "external_queries": [enhanced_prompt[:50]],
                "core_concepts": [enhanced_prompt[:30]],
                "original_query": enhanced_prompt
            }
    
    def _search_internal_references(self, queries: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """3단계-1: 사내 문서 검색"""
        try:
            all_results = []
            
            # 각 쿼리로 검색 수행
            for query in queries.get("internal_queries", []):
                results = self.doc_manager.search_training_documents(query, top=3)
                all_results.extend(results)
            
            # 중복 제거 및 상위 결과만 반환
            seen_ids = set()
            unique_results = []
            for result in all_results:
                doc_id = result.get('file_id', result.get('id', ''))
                if doc_id and doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    unique_results.append(result)
            
            return unique_results[:5]  # 상위 5개만
            
        except Exception as e:
            st.warning(f"사내 문서 검색 실패: {e}")
            return []
    
    def _search_external_references(self, queries: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """3단계-2: 외부 레퍼런스 검색"""
        try:
            all_results = []
            
            # 각 쿼리로 외부 검색 수행
            for query in queries.get("external_queries", [])[:2]:  # 외부 검색은 2개만
                results = self.ai_service.search_external_references(query)
                all_results.extend(results)
            
            return all_results[:5]  # 상위 5개만
            
        except Exception as e:
            st.warning(f"외부 레퍼런스 검색 실패: {e}")
            return []
    
    def _generate_final_analysis(self, 
                               original_input: str,
                               enhanced_prompt: str, 
                               internal_refs: List[Dict], 
                               external_refs: List[Dict]) -> str:
        """4단계: 최종 분석 결과 생성"""
        try:
            # 레퍼런스 정보를 텍스트로 변환
            internal_text = self._format_references_for_ai(internal_refs, "사내 문서")
            external_text = self._format_references_for_ai(external_refs, "외부 레퍼런스")
            
            analysis_prompt = f"""
사용자 요청: {original_input}

고도화된 분석 요구사항: {enhanced_prompt}

활용 가능한 사내 문서:
{internal_text}

활용 가능한 외부 레퍼런스:
{external_text}

위 정보들을 종합하여 사용자의 요청에 대한 상세하고 실용적인 분석 결과를 제공해주세요.
다음 구조로 작성해주세요:

## 📋 분석 요약
[핵심 내용 2-3줄 요약]

## 🎯 주요 발견사항
[사내 문서와 외부 자료를 바탕으로 한 주요 발견사항]

## 💡 실행 가능한 제안사항
[구체적이고 실행 가능한 제안사항들]

## 📚 참고 자료 활용법
[제공된 레퍼런스들을 어떻게 활용할지에 대한 가이드]

## 🔍 추가 고려사항
[더 깊이 있는 분석이 필요한 영역이나 주의사항]
"""
            
            response = self.ai_service.get_ai_response(analysis_prompt)
            return response
            
        except Exception as e:
            st.warning(f"최종 분석 생성 실패: {e}")
            return f"분석 결과 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _format_references_for_ai(self, references: List[Dict], ref_type: str) -> str:
        """레퍼런스를 AI가 이해하기 쉬운 텍스트로 변환"""
        if not references:
            return f"{ref_type}: 관련 자료 없음"
        
        formatted_text = f"{ref_type}:\n"
        for i, ref in enumerate(references, 1):
            title = ref.get('title', '제목 없음')
            content = ref.get('content', ref.get('summary', '내용 없음'))
            # 내용이 너무 길면 요약
            if len(content) > 300:
                content = content[:300] + "..."
            
            formatted_text += f"{i}. {title}\n   {content}\n\n"
        
        return formatted_text
    
    def _display_step_result(self, step_name: str, result: Any, result_type: str):
        """각 단계 결과를 150자 제한으로 표시"""
        st.success(f"✅ {step_name} 완료!")
        
        # 결과를 문자열로 변환
        if isinstance(result, dict):
            display_text = str(result)
        else:
            display_text = str(result)
        
        # 150자 제한으로 미리보기 표시
        preview = display_text[:150] + ("..." if len(display_text) > 150 else "")
        
        with st.expander(f"📄 {step_name} 결과 미리보기"):
            st.text(preview)
            
            # 전체 결과 보기 버튼
            if len(display_text) > 150:
                if st.button(f"🔍 {result_type} 전체 결과 보기", key=f"view_full_{step_name}"):
                    self._show_full_result_popup(step_name, result, result_type)
    
    def _display_reference_summary(self, internal_refs: List[Dict], external_refs: List[Dict]):
        """검색 결과 요약 표시 (150자 제한)"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📁 사내 문서 결과")
            if internal_refs:
                for i, ref in enumerate(internal_refs[:3], 1):
                    title = ref.get('title', '제목 없음')
                    summary = ref.get('summary', ref.get('content', ''))[:100] + "..."
                    
                    with st.expander(f"{i}. {title}"):
                        st.write(summary)
                        if st.button(f"📖 전체 내용 보기", key=f"internal_full_{i}"):
                            self._show_full_result_popup(f"사내문서 {i}", ref, "문서")
            else:
                st.info("관련 사내 문서가 없습니다.")
        
        with col2:
            st.markdown("#### 🌐 외부 레퍼런스")
            if external_refs:
                for i, ref in enumerate(external_refs[:3], 1):
                    title = ref.get('title', '제목 없음')
                    summary = ref.get('summary', ref.get('content', ''))[:100] + "..."
                    
                    with st.expander(f"{i}. {title}"):
                        st.write(summary)
                        if st.button(f"🔗 전체 내용 보기", key=f"external_full_{i}"):
                            self._show_full_result_popup(f"외부자료 {i}", ref, "레퍼런스")
            else:
                st.info("관련 외부 자료가 없습니다.")
    
    def _show_full_result_popup(self, title: str, content: Any, content_type: str):
        """전체 결과를 새 창(모달)으로 표시"""
        st.session_state[f'popup_content_{title}'] = {
            'title': title,
            'content': content,
            'type': content_type,
            'show': True
        }
        st.rerun()
    
    def _save_results_to_session(self, results: Dict[str, Any]):
        """분석 결과를 세션에 저장"""
        st.session_state.enhanced_analysis_results = results
        st.session_state.analysis_completed = True
        
        # 기존 세션 변수들도 업데이트 (호환성 유지)
        if results.get("step1_enhanced_prompt"):
            st.session_state.enhanced_prompt = results["step1_enhanced_prompt"]
        if results.get("step3_internal_references"):
            st.session_state.internal_search_results = results["step3_internal_references"]
        if results.get("step3_external_references"):
            st.session_state.external_search_results = results["step3_external_references"]
        if results.get("step4_final_analysis"):
            st.session_state.analysis_result = {"content": results["step4_final_analysis"]}


def render_analysis_popup():
    """분석 결과 팝업 렌더링 (메인 앱에서 호출)"""
    # 팝업 상태 확인
    popup_keys = [key for key in st.session_state.keys() if key.startswith('popup_content_')]
    
    for key in popup_keys:
        popup_data = st.session_state.get(key)
        if popup_data and popup_data.get('show'):
            # 팝업 표시
            with st.expander(f"📄 {popup_data['title']} - 전체 내용", expanded=True):
                content = popup_data['content']
                
                if isinstance(content, dict):
                    # 딕셔너리인 경우 (문서 레퍼런스)
                    st.markdown(f"**제목:** {content.get('title', 'N/A')}")
                    st.markdown(f"**요약:** {content.get('summary', 'N/A')}")
                    st.markdown(f"**출처:** {content.get('source_detail', content.get('url', 'N/A'))}")
                    
                    full_content = content.get('content', '')
                    if full_content:
                        st.markdown("**전체 내용:**")
                        st.text_area("", full_content, height=400, key=f"popup_text_{key}")
                    
                else:
                    # 문자열인 경우
                    st.text_area("", str(content), height=400, key=f"popup_text_{key}")
                
                # 팝업 닫기 버튼
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("❌ 닫기", key=f"close_{key}"):
                        popup_data['show'] = False
                        st.session_state[key] = popup_data
                        st.rerun()