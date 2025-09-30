"""
AI 분석 서비스 - AI 관련 비즈니스 로직 처리
"""
import streamlit as st
import time
from utils.ai_service import AIService

class AIAnalysisService:
    """AI 분석 서비스 클래스"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def run_enhanced_analysis_process(self, user_input: str):
        """
        개선된 동기적 3단계 AI 분석 프로세스
        1. 프롬프트 재생성 (사용자 의도 파악)
        2. 병렬 검색 (사내 문서 + 외부 레퍼런스)  
        3. 통합 분석 결과 생성
        """
        
        # 입력 검증
        if not user_input or not user_input.strip():
            st.error("❌ 입력된 내용이 없습니다.")
            return
        
        user_input = user_input.strip()
        st.info(f"🔍 분석 시작: '{user_input[:50]}...' ({len(user_input)}자)")
        
        # 중복 실행 방지
        input_hash = str(hash(user_input))
        if st.session_state.get('last_analysis_hash') == input_hash:
            st.info("이미 분석된 내용입니다. 기존 결과를 표시합니다.")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            st.session_state.last_analysis_hash = input_hash
            
            # AI 서비스 초기화 확인
            status_text.text("🔧 AI 서비스 초기화 중...")
            progress_bar.progress(10)
            
            # AI 서비스 상태 확인
            ai_status = self.ai_service.test_ai_connection()
            if not ai_status.get('ai_available', False):
                raise Exception(f"AI 서비스 사용 불가: {ai_status.get('connection_test', 'Unknown')}")
            
            # 1단계: 사용자 의도 파악 및 프롬프트 재생성
            status_text.text("🧠 사용자 의도 분석 중...")
            try:
                enhanced_prompt = self._enhance_user_prompt(user_input)
                progress_bar.progress(30)
            except Exception as e:
                st.error(f"1단계 실패 - 프롬프트 최적화: {str(e)}")
                enhanced_prompt = user_input  # 폴백으로 원본 사용
            
            # 2단계: 순차적 검색 수행
            status_text.text("📚 사내 문서 검색 중...")
            try:
                internal_docs = self._search_internal_documents(enhanced_prompt)
                progress_bar.progress(50)
            except Exception as e:
                st.warning(f"사내 문서 검색 실패: {str(e)}")
                internal_docs = []
            
            status_text.text("🌍 외부 레퍼런스 검색 중...")
            try:
                external_docs = self._search_external_references(enhanced_prompt)
                progress_bar.progress(70)
            except Exception as e:
                st.warning(f"외부 검색 실패: {str(e)}")
                external_docs = []
            
            # 3단계: 통합 분석 결과 생성
            status_text.text("🤖 AI 분석 결과 생성 중...")
            try:
                analysis_result = self._generate_analysis_result(enhanced_prompt, internal_docs, external_docs, user_input)
                progress_bar.progress(100)
            except Exception as e:
                st.error(f"3단계 실패 - 분석 결과 생성: {str(e)}")
                # 폴백 결과 생성
                analysis_result = {
                    "title": "⚠️ 제한된 분석 결과",
                    "content": f"입력: {user_input}\n\n사내 문서: {len(internal_docs)}개\n외부 자료: {len(external_docs)}개\n\n분석 엔진에 일시적인 문제가 발생했습니다.",
                    "timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            status_text.text("✅ 모든 단계 완료!")
            
            # 결과를 세션 상태에 저장
            self._save_results_to_session(enhanced_prompt, internal_docs, external_docs, analysis_result)
            
            st.success("✅ AI 분석이 완료되었습니다!")
            
        except Exception as e:
            st.error(f"❌ 분석 프로세스 중 치명적 오류: {str(e)}")
            st.error(f"오류 상세: {type(e).__name__}")
            progress_bar.progress(0)
            status_text.text("❌ 치명적 오류 발생")
            
            # 최소한의 결과라도 제공
            try:
                self._save_results_to_session(
                    user_input, [], [], 
                    {
                        "title": "❌ 오류 발생",
                        "content": f"분석 중 오류가 발생했습니다: {str(e)}",
                        "timestamp": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
            except:
                pass
    
    def _enhance_user_prompt(self, user_input: str) -> str:
        """1단계: 프롬프트 재생성"""
        st.info("🧠 **1단계:** 사용자 의도를 분석하고 검색 프롬프트를 최적화합니다...")
        
        try:
            with st.spinner("사용자 의도를 분석하고 프롬프트를 최적화하고 있습니다..."):
                enhanced_prompt = self.ai_service.enhance_user_prompt(user_input)
                st.session_state.enhanced_prompt = enhanced_prompt
                
                # 프롬프트 최적화 완료 표시
                st.success("✅ 프롬프트 최적화 완료!")
                
                with st.expander("🔍 재생성된 프롬프트 확인"):
                    st.markdown(f"**📝 원본 입력 ({len(user_input)}자):**")
                    st.code(user_input[:200] + ('...' if len(user_input) > 200 else ''))
                    st.markdown(f"**🤖 AI 최적화 프롬프트 ({len(enhanced_prompt)}자):**")
                    st.code(enhanced_prompt[:200] + ('...' if len(enhanced_prompt) > 200 else ''))
                    if len(enhanced_prompt) > len(user_input):
                        st.caption("✨ 프롬프트가 더 구체적이고 검색에 최적화되었습니다!")
                
                return enhanced_prompt
                
        except Exception as e:
            st.warning(f"⚠️ 프롬프트 최적화 실패: {str(e)}")
            st.info("원본 입력을 그대로 사용합니다.")
            return user_input
    
    def _search_internal_documents(self, enhanced_prompt: str) -> list:
        """2-1단계: 사내 문서 검색"""
        with st.spinner("사내 문서 데이터베이스에서 관련 자료를 검색하고 있습니다..."):
            internal_docs = self.ai_service.search_internal_documents(enhanced_prompt)
            st.success(f"✅ 사내 문서 {len(internal_docs)}개 발견")
            return internal_docs
    
    def _search_external_references(self, enhanced_prompt: str) -> list:
        """2-2단계: 외부 레퍼런스 검색"""
        with st.spinner("인터넷에서 유사 사례와 레퍼런스를 검색하고 있습니다..."):
            external_docs = self.ai_service.search_external_references(enhanced_prompt)
            st.success(f"✅ 외부 참조 {len(external_docs)}개 발견")
            return external_docs
    
    def _generate_analysis_result(self, enhanced_prompt: str, internal_docs: list, external_docs: list, original_input: str) -> dict:
        """3단계: 통합 분석 결과 생성"""
        with st.spinner("검색 결과를 바탕으로 통합 분석 결과를 생성하고 있습니다..."):
            analysis_result = self.ai_service.generate_optimized_analysis(
                enhanced_prompt, internal_docs, external_docs, original_input
            )
            return analysis_result
    
    def _save_results_to_session(self, enhanced_prompt: str, internal_docs: list, external_docs: list, analysis_result: dict):
        """결과를 세션 상태에 저장"""
        st.session_state.enhanced_prompt = enhanced_prompt
        st.session_state.internal_search_results = internal_docs
        st.session_state.external_search_results = external_docs
        st.session_state.analysis_result = analysis_result
    
    def get_ai_status(self) -> dict:
        """AI 서비스 상태 확인"""
        return self.ai_service.test_ai_connection()