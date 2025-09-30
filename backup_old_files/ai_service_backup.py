"""
AI 서비스 모듈 - Azure OpenAI와 Tavily 검색을 사용
기획자와 보고서 제작자를 위한 전문 분석 도구
"""
import openai
import time
import streamlit as st
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from tavily import TavilyClient
from config import AI_CONFIG, TAVILY_CONFIG, LANGSMITH_CONFIG, AZURE_SEARCH_CONFIG

# LangSmith 추적 설정
try:
    if LANGSMITH_CONFIG["enabled"]:
        from langsmith import Client, trace
        import os
        os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_CONFIG["api_key"]
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_CONFIG["project_name"]
        
        langsmith_client = Client(api_key=LANGSMITH_CONFIG["api_key"])
        LANGSMITH_AVAILABLE = True
        print("✅ LangSmith 추적 활성화됨")
    else:
        LANGSMITH_AVAILABLE = False
        print("⚠️ LangSmith API 키가 없습니다")
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("⚠️ LangSmith 패키지가 설치되지 않았습니다")
except Exception as e:
    LANGSMITH_AVAILABLE = False
    print(f"⚠️ LangSmith 초기화 실패: {e}")

class AIService:
    def __init__(self):
        # 초기화
        self.use_legacy = False
        self.legacy_client = None
        self.langsmith_enabled = LANGSMITH_AVAILABLE
        
        # Azure OpenAI 설정
        try:
            if AI_CONFIG["openai_api_key"] and AI_CONFIG["openai_endpoint"]:
                # OpenAI 라이브러리 버전 호환성을 위한 설정
                self.client = openai.AzureOpenAI(
                    azure_endpoint=AI_CONFIG["openai_endpoint"],
                    api_key=AI_CONFIG["openai_api_key"],
                    api_version=AI_CONFIG["api_version"]
                )
                self.ai_available = True
                print("✅ Azure OpenAI 초기화 성공")
            else:
                self.client = None
                self.ai_available = False
                print("⚠️ Azure OpenAI 설정이 없습니다. 더미 모드로 작동합니다.")
        except Exception as e:
            self.client = None
            self.ai_available = False
            print(f"⚠️ Azure OpenAI 초기화 실패: {e}")
            # 호환성 문제인 경우 대체 초기화 시도
            try:
                import openai as openai_client
                openai_client.api_type = "azure"
                openai_client.api_base = AI_CONFIG["openai_endpoint"]
                openai_client.api_version = AI_CONFIG["api_version"] 
                openai_client.api_key = AI_CONFIG["openai_api_key"]
                self.legacy_client = openai_client
                self.ai_available = True
                self.use_legacy = True
                print("✅ 레거시 모드로 Azure OpenAI 초기화 성공")
            except Exception as legacy_error:
                self.use_legacy = False
                print(f"⚠️ 레거시 모드도 실패: {legacy_error}")
        
        # Tavily 검색 클라이언트
        try:
            if TAVILY_CONFIG["api_key"]:
                self.tavily_client = TavilyClient(api_key=TAVILY_CONFIG["api_key"])
                self.search_available = True
            else:
                self.tavily_client = None
                self.search_available = False
                print("⚠️ Tavily API 키가 없습니다. 로컬 검색을 사용합니다.")
        except Exception as e:
            self.tavily_client = None
            self.search_available = False
            print(f"⚠️ Tavily 초기화 실패: {e}")
        
        # 캐시 시스템 초기화 (중복 API 호출 방지)
        self._cache = {}
        self._cache_ttl = 300  # 5분 캐시
        
        # Azure Search 클라이언트
        try:
            if AZURE_SEARCH_CONFIG["endpoint"] and AZURE_SEARCH_CONFIG["admin_key"]:
                import requests
                self.azure_search_available = True
                self.azure_search_endpoint = AZURE_SEARCH_CONFIG["endpoint"]
                self.azure_search_key = AZURE_SEARCH_CONFIG["admin_key"]
                self.azure_search_index = AZURE_SEARCH_CONFIG["index_name"]
                self.azure_search_api_version = AZURE_SEARCH_CONFIG["api_version"]
                print("✅ Azure Search 초기화 성공")
            else:
                self.azure_search_available = False
                print("⚠️ Azure Search 설정이 없습니다. 로컬 검색을 사용합니다.")
        except Exception as e:
            self.azure_search_available = False
            print(f"⚠️ Azure Search 초기화 실패: {e}")
    
    def _get_cache_key(self, method: str, query: str) -> str:
        """캐시 키 생성"""
        return f"{method}:{hash(query)}"
    
    def _get_cached_result(self, cache_key: str):
        """캐시된 결과 조회"""
        if cache_key in self._cache:
            timestamp, result = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return result
            else:
                # 만료된 캐시 삭제
                del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, result):
        """결과 캐시 저장"""
        self._cache[cache_key] = (time.time(), result)
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """AI 연결 상태 테스트"""
        result = {
            "ai_available": self.ai_available,
            "search_available": self.search_available,
            "langsmith_enabled": self.langsmith_enabled,
            "langsmith_project": LANGSMITH_CONFIG.get("project_name", "없음"),
            "endpoint": AI_CONFIG.get("openai_endpoint", "없음"),
            "model": AI_CONFIG.get("deployment_name", "없음"),
            "api_key_set": bool(AI_CONFIG.get("openai_api_key")),
            "tavily_key_set": bool(TAVILY_CONFIG.get("api_key")),
            "langsmith_key_set": bool(LANGSMITH_CONFIG.get("api_key"))
        }
        
        if self.ai_available:
            try:
                print("🔍 OpenAI 연결 테스트 중...")
                
                if hasattr(self, 'use_legacy') and self.use_legacy:
                    # 레거시 모드 호출
                    response = self.legacy_client.ChatCompletion.create(
                        engine=AI_CONFIG["deployment_name"],
                        messages=[{"role": "user", "content": "안녕하세요. 간단히 인사해주세요."}],
                        max_tokens=50,
                        temperature=0.1
                    )
                    result["test_response"] = response.choices[0].message.content
                    result["mode"] = "legacy"
                else:
                    # 새로운 모드 호출
                    response = self.client.chat.completions.create(
                        model=AI_CONFIG["deployment_name"],
                        messages=[{"role": "user", "content": "안녕하세요. 간단히 인사해주세요."}],
                        max_tokens=50,
                        temperature=0.1
                    )
                    result["test_response"] = response.choices[0].message.content
                    result["mode"] = "modern"
                    
                result["connection_test"] = "성공"
                print("✅ OpenAI 연결 테스트 성공")
            except Exception as e:
                result["connection_test"] = f"실패: {str(e)}"
                result["test_response"] = None
                print(f"❌ OpenAI 연결 테스트 실패: {e}")
        else:
            result["connection_test"] = "AI 사용 불가능"
            result["test_response"] = None
            
        return result
    
    def get_smart_analysis_prompt(self, text: str, user_type: str = "planner") -> str:
        """사용자 유형에 맞는 스마트 분석 프롬프트 생성"""
        prompts = {
            "planner": """당신은 경험이 풍부한 기획 전문가입니다. 
            주어진 텍스트를 분석하여 기획자 관점에서 다음을 제공하세요:
            
            1. 핵심 인사이트 (3-5개 불릿포인트)
            2. 실행 가능한 액션 아이템 (우선순위별)
            3. 잠재적 위험요소와 대안
            4. 이해관계자별 고려사항
            5. 성공 지표 제안
            
            결과는 명확하고 실행 가능한 형태로 구조화하세요.""",
            
            "reporter": """당신은 전문 보고서 작성자입니다.
            주어진 텍스트를 분석하여 보고서 작성자 관점에서 다음을 제공하세요:
            
            1. 핵심 메시지 요약 (한 문단)
            2. 주요 데이터 포인트와 통계
            3. 논리적 구조 제안 (서론-본론-결론)
            4. 시각화 제안 (차트, 그래프, 표)
            5. 추가 필요 정보 목록
            
            결과는 설득력 있고 논리적인 보고서 형태로 구조화하세요.""",
            
            "general": """당신은 문서 분석 전문가입니다.
            주어진 텍스트를 종합적으로 분석하여 다음을 제공하세요:
            
            1. 주요 주제와 키워드
            2. 핵심 내용 요약
            3. 논리적 흐름 분석
            4. 개선 제안
            5. 관련 자료 검색 키워드
            
            결과는 명확하고 활용하기 쉬운 형태로 제공하세요."""
        }
        
        return prompts.get(user_type, prompts["general"])
    
    def analyze_text(self, text: str, user_type: str = "general") -> Dict[str, Any]:
        """텍스트 분석 - 사용자 유형별 맞춤 분석"""
        # LangSmith 추적 시작
        if self.langsmith_enabled:
            return self._analyze_text_with_langsmith(text, user_type)
        else:
            return self._analyze_text_core(text, user_type)
    
    def _analyze_text_with_langsmith(self, text: str, user_type: str = "general") -> Dict[str, Any]:
        """LangSmith 추적과 함께 텍스트 분석 - LangChain 통합"""
        try:
            from langchain_openai import AzureChatOpenAI
            
            print("🔍 LangChain + LangSmith 추적 시작...")
            
            # LangChain OpenAI 클라이언트 (자동 LangSmith 추적)
            llm = AzureChatOpenAI(
                azure_endpoint=AI_CONFIG["openai_endpoint"],
                api_key=AI_CONFIG["openai_api_key"],
                api_version=AI_CONFIG["api_version"],
                deployment_name=AI_CONFIG["deployment_name"],
                temperature=AI_CONFIG["temperature"],
                max_tokens=AI_CONFIG["max_tokens"],
                model_kwargs={
                    "metadata": {
                        "user_type": user_type,
                        "text_length": len(text),
                        "project": "AI-Document-Assistant"
                    }
                }
            )
            
            # 프롬프트 준비
            system_prompt = self.get_smart_analysis_prompt(text, user_type)
            
            # LangChain invoke 호출 (자동으로 LangSmith에 추적됨)
            messages = [
                ("system", system_prompt),
                ("human", f"다음 텍스트를 분석해주세요:\n\n{text}")
            ]
            
            print("� LangChain Azure OpenAI API 호출 시작...")
            start_time = time.time()
            
            response = llm.invoke(messages)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print("✅ LangChain Azure OpenAI API 호출 성공!")
            print(f"📊 응답 길이: {len(response.content)} 문자")
            print(f"⏱️ 호출 시간: {duration:.2f}초")
            print("✅ LangSmith 자동 추적 완료 - https://smith.langchain.com에서 확인 가능")
            
            # 응답 내용
            content = response.content
            
            # 구조화된 분석 결과 생성
            analysis_result = self._parse_analysis_response(content, user_type)
            
            return {
                "keywords": self._extract_keywords(text),
                "topic": self._extract_topic(content),
                "summary": self._extract_summary(content),
                "analysis": analysis_result,
                "user_type": user_type,
                "original_text": text[:500] + "..." if len(text) > 500 else text,
                "call_info": {
                    "duration_seconds": duration,
                    "response_length": len(content),
                    "status": "success",
                    "method": "langchain_azure_openai"
                }
            }
            
        except ImportError:
            print("⚠️ LangChain OpenAI 패키지가 설치되지 않음 - 기본 모드로 전환")
            return self._analyze_text_core(text, user_type)
        except Exception as langchain_error:
            print(f"⚠️ LangChain 추적 실패: {langchain_error}")
            print("🔄 기본 OpenAI 모드로 분석 계속...")
            return self._analyze_text_core(text, user_type)
    
    def _analyze_text_core(self, text: str, user_type: str = "general") -> Dict[str, Any]:
        """핵심 텍스트 분석 로직"""
        if not text.strip():
            return {"keywords": [], "topic": "", "context": "", "summary": "", "analysis": {}}
        
        # AI 사용 가능 여부 체크 및 로그
        print(f"🔍 AI 분석 요청: user_type={user_type}, text_length={len(text)}")
        print(f"🔧 AI 사용 가능: {self.ai_available}")
        
        if not self.ai_available:
            print("⚠️ AI 사용 불가능 - 더미 데이터 반환")
            return self._get_dummy_analysis(text, user_type)
        
        try:
            # 사용자 맞춤형 프롬프트 사용
            system_prompt = self.get_smart_analysis_prompt(text, user_type)
            
            print("🚀 Azure OpenAI API 호출 시작...")
            print(f"📍 Endpoint: {AI_CONFIG['openai_endpoint']}")
            print(f"🤖 Model: {AI_CONFIG['deployment_name']}")
            
            # API 호출 시작 시간 기록
            start_time = time.time()
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 텍스트를 분석해주세요:\n\n{text}"}
            ]
            
            # LangSmith 로깅을 위한 호출 정보
            call_info = {
                "messages": messages,
                "model": AI_CONFIG["deployment_name"],
                "max_tokens": AI_CONFIG["max_tokens"],
                "temperature": AI_CONFIG["temperature"],
                "user_type": user_type,
                "input_length": len(text)
            }
            
            if self.langsmith_enabled:
                print("📝 LangSmith 호출 정보 기록 중...")
            
            if hasattr(self, 'use_legacy') and self.use_legacy:
                # 레거시 모드 호출
                print("🔧 레거시 모드로 API 호출")
                response = self.legacy_client.ChatCompletion.create(
                    engine=AI_CONFIG["deployment_name"],
                    messages=messages,
                    max_tokens=AI_CONFIG["max_tokens"],
                    temperature=AI_CONFIG["temperature"]
                )
            else:
                # 새로운 모드 호출
                print("🔧 모던 모드로 API 호출")
                response = self.client.chat.completions.create(
                    model=AI_CONFIG["deployment_name"],
                    messages=messages,
                    max_tokens=AI_CONFIG["max_tokens"],
                    temperature=AI_CONFIG["temperature"]
                )
            
            # API 호출 종료 시간 및 성능 메트릭
            end_time = time.time()
            duration = end_time - start_time
            
            print("✅ Azure OpenAI API 호출 성공!")
            print(f"📊 응답 길이: {len(response.choices[0].message.content)} 문자")
            print(f"⏱️ 호출 시간: {duration:.2f}초")
            
            # 토큰 사용량 정보 (가능한 경우)
            if hasattr(response, 'usage') and response.usage:
                print(f"🎯 토큰 사용량: {response.usage.total_tokens} (입력: {response.usage.prompt_tokens}, 출력: {response.usage.completion_tokens})")
                call_info["token_usage"] = {
                    "total_tokens": response.usage.total_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            
            content = response.choices[0].message.content
            
            # LangSmith 응답 정보 추가
            if self.langsmith_enabled:
                call_info.update({
                    "response_length": len(content),
                    "duration_seconds": duration,
                    "status": "success"
                })
                print("📝 LangSmith 응답 정보 기록 완료")
            
            # 구조화된 분석 결과 생성
            analysis_result = self._parse_analysis_response(content, user_type)
            
            return {
                "keywords": self._extract_keywords(text),
                "topic": self._extract_topic(content),
                "summary": self._extract_summary(content),
                "analysis": analysis_result,
                "user_type": user_type,
                "original_text": text[:500] + "..." if len(text) > 500 else text,
                "call_info": call_info if self.langsmith_enabled else None
            }
            
        except Exception as e:
            print(f"❌ Azure OpenAI API 호출 실패: {str(e)}")
            
            # LangSmith 에러 정보
            if self.langsmith_enabled:
                error_info = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "status": "failed"
                }
                print("📝 LangSmith 에러 정보 기록")
            
            st.error(f"AI 분석 중 오류 발생: {str(e)}")
            return self._get_dummy_analysis(text, user_type)
    
    def _parse_analysis_response(self, content: str, user_type: str) -> Dict[str, Any]:
        """AI 응답을 구조화된 분석 결과로 파싱"""
        lines = content.split('\n')
        sections = {}
        current_section = ""
        current_content = []
        
        # 섹션별로 내용 분류
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 번호나 제목으로 시작하는 섹션 감지
            if re.match(r'^\d+\.', line) or line.startswith('#') or line.endswith(':'):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # 마지막 섹션 처리
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        # 사용자 타입별 구조화
        if user_type == "planner":
            return {
                "insights": sections.get("1. 핵심 인사이트", ""),
                "action_items": sections.get("2. 실행 가능한 액션 아이템", ""),
                "risks": sections.get("3. 잠재적 위험요소와 대안", ""),
                "stakeholders": sections.get("4. 이해관계자별 고려사항", ""),
                "metrics": sections.get("5. 성공 지표 제안", ""),
                "raw_content": content
            }
        elif user_type == "reporter":
            return {
                "key_message": sections.get("1. 핵심 메시지 요약", ""),
                "data_points": sections.get("2. 주요 데이터 포인트와 통계", ""),
                "structure": sections.get("3. 논리적 구조 제안", ""),
                "visualization": sections.get("4. 시각화 제안", ""),
                "additional_info": sections.get("5. 추가 필요 정보 목록", ""),
                "raw_content": content
            }
        else:
            return {
                "topics_keywords": sections.get("1. 주요 주제와 키워드", ""),
                "summary": sections.get("2. 핵심 내용 요약", ""),
                "logic_flow": sections.get("3. 논리적 흐름 분석", ""),
                "improvements": sections.get("4. 개선 제안", ""),
                "search_keywords": sections.get("5. 관련 자료 검색 키워드", ""),
                "raw_content": content
            }
    
    def _get_dummy_analysis(self, text: str, user_type: str) -> Dict[str, Any]:
        """더미 분석 결과 (AI가 사용 불가능할 때)"""
        keywords = self._extract_keywords(text)
        
        if user_type == "planner":
            return {
                "keywords": keywords,
                "topic": "기획 분석 필요",
                "summary": "기획자 관점에서 추가 분석이 필요한 내용입니다.",
                "analysis": {
                    "insights": "• 주요 논점들을 명확히 정의 필요\n• 이해관계자 분석 요구\n• 실행 계획 수립 필요",
                    "action_items": "1. 현황 분석 수행\n2. 목표 설정\n3. 실행 계획 작성",
                    "risks": "• 불확실한 요소들 존재\n• 리소스 제약 고려 필요",
                    "stakeholders": "• 내부 팀원들\n• 경영진\n• 외부 파트너",
                    "metrics": "• 진행률 측정\n• 품질 지표\n• 성과 측정",
                    "raw_content": f"[더미 모드] {text[:200]}..."
                },
                "user_type": user_type,
                "original_text": text[:500] + "..." if len(text) > 500 else text
            }
        elif user_type == "reporter":
            return {
                "keywords": keywords,
                "topic": "보고서 작성 지원",
                "summary": "보고서 작성을 위한 구조화된 분석이 필요합니다.",
                "analysis": {
                    "key_message": "핵심 메시지를 명확히 정의하고 논리적으로 전개해야 합니다.",
                    "data_points": "• 정량적 데이터 수집 필요\n• 비교 분석 데이터\n• 트렌드 분석",
                    "structure": "1. 서론: 배경과 목적\n2. 본론: 현황 분석과 해결방안\n3. 결론: 권고사항",
                    "visualization": "• 막대 차트: 비교 분석\n• 선 그래프: 트렌드\n• 파이 차트: 비율",
                    "additional_info": "• 업계 벤치마크\n• 경쟁사 분석\n• 시장 동향",
                    "raw_content": f"[더미 모드] {text[:200]}..."
                },
                "user_type": user_type,
                "original_text": text[:500] + "..." if len(text) > 500 else text
            }
        else:
            return {
                "keywords": keywords,
                "topic": "텍스트 분석",
                "summary": "텍스트 내용에 대한 종합적인 분석이 필요합니다.",
                "analysis": {
                    "topics_keywords": f"주요 키워드: {', '.join(keywords[:5])}",
                    "summary": "문서의 핵심 내용을 요약하고 구조화가 필요합니다.",
                    "logic_flow": "논리적 흐름을 개선하여 가독성을 높일 수 있습니다.",
                    "improvements": "• 명확한 제목 구성\n• 단락별 주제 명확화\n• 결론 강화",
                    "search_keywords": f"검색 키워드: {', '.join(keywords[:3])}",
                    "raw_content": f"[더미 모드] {text[:200]}..."
                },
                "user_type": user_type,
                "original_text": text[:500] + "..." if len(text) > 500 else text
            }
    
    def search_related_documents(self, query: str, keywords: List[str] = None, user_type: str = "general") -> List[Dict[str, Any]]:
        """Tavily를 사용한 관련 문서 검색 - 사용자 타입별 맞춤 검색"""
        if not self.search_available:
            return self._get_intelligent_dummy_results(query, keywords, user_type)
        
        try:
            # 사용자 타입별 검색 쿼리 최적화
            search_query = self._optimize_search_query(query, keywords, user_type)
            
            # Tavily 검색 실행 (디버깅 로그 추가)
            print(f"🔍 Tavily 호출 시작: query='{search_query}', depth={TAVILY_CONFIG['search_depth']}, max={TAVILY_CONFIG['max_results']}")
            response = self.tavily_client.search(
                query=search_query,
                search_depth=TAVILY_CONFIG["search_depth"],
                max_results=TAVILY_CONFIG["max_results"]
            )
            print(f"✅ Tavily 응답 수신: {len(response.get('results', []))}개 결과")
            
            # 결과 변환 및 필터링
            documents = []
            for i, result in enumerate(response.get("results", [])):
                doc = {
                    "id": i + 1,
                    "title": result.get("title", "제목 없음"),
                    "summary": self._generate_smart_summary(result.get("content", ""), user_type),
                    "content": result.get("content", ""),
                    "source": result.get("url", ""),
                    "relevance_score": self._calculate_relevance_score(result, query, keywords, user_type),
                    "keywords": keywords[:5] if keywords else [],
                    "user_type": user_type,
                    "document_type": self._classify_document_type(result, user_type)
                }
                documents.append(doc)
            
            # 관련도순 정렬 및 필터링
            documents.sort(key=lambda x: x["relevance_score"], reverse=True)
            return documents[:6]  # 최대 6개
            
        except Exception as e:
            print(f"❌ 외부 검색 실패: {str(e)}")
            print(f"❌ 오류 타입: {type(e).__name__}")
            import traceback
            print(f"❌ 상세 오류: {traceback.format_exc()}")
            st.warning(f"실시간 검색 중 오류 발생: {str(e)} - 로컬 데이터를 사용합니다.")
            return self._get_intelligent_dummy_results(query, keywords, user_type)
    
    def _optimize_search_query(self, query: str, keywords: List[str], user_type: str) -> str:
        """사용자 타입별 검색 쿼리 최적화"""
        base_query = query
        
        # 키워드 추가
        if keywords:
            base_query += " " + " ".join(keywords[:3])
        
        # 사용자 타입별 검색어 추가
        type_keywords = {
            "planner": ["기획", "전략", "계획", "방안", "strategy", "planning"],
            "reporter": ["보고서", "분석", "데이터", "통계", "report", "analysis"],
            "general": ["정보", "자료", "가이드", "방법", "information"]
        }
        
        if user_type in type_keywords:
            base_query += " " + " OR ".join(type_keywords[user_type][:2])
        
        return base_query
    
    def _get_relevant_domains(self, user_type: str) -> List[str]:
        """사용자 타입별 관련 도메인 반환"""
        domains = {
            "planner": ["harvard.edu", "mit.edu", "mckinsey.com", "pwc.com", "deloitte.com"],
            "reporter": ["statista.com", "bloomberg.com", "reuters.com", "economist.com"],
            "general": []  # 모든 도메인 허용
        }
        return domains.get(user_type, [])
    
    def _generate_smart_summary(self, content: str, user_type: str) -> str:
        """사용자 타입별 스마트 요약 생성"""
        if not content or len(content) < 100:
            return content[:200] + "..." if len(content) > 200 else content
        
        # 간단한 요약 로직 (실제로는 더 정교한 AI 요약 사용 가능)
        sentences = content.split('. ')
        
        if user_type == "planner":
            # 기획자를 위한 액션 중심 요약
            key_sentences = [s for s in sentences if any(word in s.lower() 
                           for word in ['계획', '전략', '방법', '방안', '목표', 'strategy', 'plan'])]
        elif user_type == "reporter":
            # 보고서 작성자를 위한 데이터 중심 요약
            key_sentences = [s for s in sentences if any(word in s.lower() 
                           for word in ['데이터', '통계', '결과', '분석', '수치', 'data', 'analysis'])]
        else:
            # 일반적인 요약
            key_sentences = sentences[:3]
        
        if not key_sentences:
            key_sentences = sentences[:2]
        
        summary = '. '.join(key_sentences[:2])
        return summary[:300] + "..." if len(summary) > 300 else summary
    
    def _calculate_relevance_score(self, result: Dict, query: str, keywords: List[str], user_type: str) -> float:
        """사용자 타입별 관련도 점수 계산"""
        score = result.get("score", 0.5)
        
        title = result.get("title", "").lower()
        content = result.get("content", "").lower()
        query_lower = query.lower()
        
        # 기본 점수
        relevance = score
        
        # 제목 매칭 보너스
        if query_lower in title:
            relevance += 0.3
        
        # 키워드 매칭
        if keywords:
            keyword_matches = sum(1 for kw in keywords if kw.lower() in title or kw.lower() in content)
            relevance += (keyword_matches / len(keywords)) * 0.2
        
        # 사용자 타입별 보너스
        type_bonus_keywords = {
            "planner": ["기획", "전략", "계획", "방안", "strategy", "planning", "roadmap"],
            "reporter": ["보고서", "분석", "데이터", "통계", "report", "analysis", "study"],
            "general": []
        }
        
        if user_type in type_bonus_keywords:
            bonus_matches = sum(1 for kw in type_bonus_keywords[user_type] 
                              if kw in title or kw in content)
            relevance += bonus_matches * 0.1
        
        return min(1.0, relevance)
    
    def _classify_document_type(self, result: Dict, user_type: str) -> str:
        """문서 타입 분류"""
        title = result.get("title", "").lower()
        url = result.get("url", "").lower()
        
        if any(word in title for word in ["보고서", "report", "분석", "analysis"]):
            return "보고서"
        elif any(word in title for word in ["가이드", "guide", "방법", "how-to"]):
            return "가이드"
        elif any(word in url for word in ["pdf", "doc", "paper"]):
            return "문서"
        elif any(word in title for word in ["뉴스", "news", "기사"]):
            return "뉴스"
        else:
            return "일반"
    
    def _get_intelligent_dummy_results(self, query: str, keywords: List[str], user_type: str) -> List[Dict[str, Any]]:
        """지능형 더미 검색 결과 - 사용자 타입별 맞춤형"""
        try:
            # 로컬 샘플 데이터 로드
            with open('data/sample_documents.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = data.get("documents", [])
            
            # 사용자 타입별 필터링 및 점수 조정
            filtered_docs = []
            for doc in documents:
                relevance = self._calculate_local_relevance(doc, query, keywords, user_type)
                if relevance > 0.3:  # 최소 관련도 임계값
                    doc["relevance_score"] = relevance
                    doc["user_type"] = user_type
                    doc["document_type"] = self._classify_local_document(doc, user_type)
                    doc["summary"] = self._generate_smart_summary(doc.get("content", ""), user_type)
                    filtered_docs.append(doc)
            
            # 관련도순 정렬
            filtered_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            # 사용자 타입별 추가 더미 데이터 생성
            if len(filtered_docs) < 3:
                additional_docs = self._generate_type_specific_dummy_docs(query, keywords, user_type)
                filtered_docs.extend(additional_docs)
            
            return filtered_docs[:5]
            
        except Exception as e:
            # 파일 로드 실패시 기본 더미 데이터
            return self._generate_type_specific_dummy_docs(query, keywords, user_type)
    
    def _calculate_local_relevance(self, doc: Dict, query: str, keywords: List[str], user_type: str) -> float:
        """로컬 문서의 관련도 계산"""
        relevance = 0.0
        
        title = doc.get("title", "").lower()
        content = doc.get("content", "").lower()
        doc_keywords = [kw.lower() for kw in doc.get("keywords", [])]
        query_lower = query.lower()
        
        # 쿼리 매칭
        if query_lower in title:
            relevance += 0.4
        elif query_lower in content:
            relevance += 0.2
        
        # 키워드 매칭
        if keywords:
            keyword_matches = sum(1 for kw in keywords 
                                if kw.lower() in title or kw.lower() in content or kw.lower() in doc_keywords)
            relevance += (keyword_matches / len(keywords)) * 0.3
        
        # 사용자 타입별 보너스
        type_keywords = {
            "planner": ["기획", "전략", "계획", "방안", "프로젝트"],
            "reporter": ["보고서", "분석", "데이터", "통계", "연구"],
            "general": ["정보", "자료", "내용"]
        }
        
        if user_type in type_keywords:
            type_matches = sum(1 for kw in type_keywords[user_type] 
                             if kw in title or kw in content)
            relevance += type_matches * 0.15
        
        return min(1.0, relevance)
    
    def _classify_local_document(self, doc: Dict, user_type: str) -> str:
        """로컬 문서 타입 분류"""
        title = doc.get("title", "").lower()
        keywords = [kw.lower() for kw in doc.get("keywords", [])]
        
        if any(word in title for word in ["분석", "보고서", "연구"]):
            return "분석 보고서"
        elif any(word in keywords for word in ["가이드", "방법", "튜토리얼"]):
            return "실용 가이드"
        elif user_type == "planner" and any(word in title for word in ["기획", "전략", "계획"]):
            return "기획 자료"
        elif user_type == "reporter" and any(word in keywords for word in ["데이터", "통계"]):
            return "데이터 자료"
        else:
            return "참고 자료"
    
    def _generate_type_specific_dummy_docs(self, query: str, keywords: List[str], user_type: str) -> List[Dict[str, Any]]:
        """사용자 타입별 특화 더미 문서 생성"""
        base_docs = []
        
        if user_type == "planner":
            base_docs = [
                {
                    "id": "dummy_plan_1",
                    "title": f"'{query}' 기획 실행 가이드",
                    "summary": f"{query}와 관련된 기획 업무를 체계적으로 수행하기 위한 단계별 가이드입니다.",
                    "content": f"이 문서는 {query}에 대한 기획 프로세스를 다루며, 현황 분석, 목표 설정, 실행 계획 수립, 리스크 관리 등의 핵심 요소들을 포함합니다.",
                    "source": "기획 전문가 DB",
                    "relevance_score": 0.9,
                    "keywords": keywords[:5] if keywords else ["기획", "전략", "실행"],
                    "user_type": user_type,
                    "document_type": "기획 가이드"
                },
                {
                    "id": "dummy_plan_2", 
                    "title": f"'{query}' 프로젝트 관리 전략",
                    "summary": f"{query} 관련 프로젝트의 성공적 관리를 위한 전략과 베스트 프랙티스입니다.",
                    "content": f"프로젝트 관리 관점에서 {query}를 다루는 방법론과 실무진들이 알아야 할 핵심 사항들을 정리한 문서입니다.",
                    "source": "PM 실무 가이드",
                    "relevance_score": 0.85,
                    "keywords": keywords[:5] if keywords else ["프로젝트", "관리", "전략"],
                    "user_type": user_type,
                    "document_type": "관리 전략"
                }
            ]
        elif user_type == "reporter":
            base_docs = [
                {
                    "id": "dummy_report_1",
                    "title": f"'{query}' 현황 분석 보고서",
                    "summary": f"{query}에 대한 종합적인 현황 분석과 데이터 기반 인사이트를 제공합니다.",
                    "content": f"이 보고서는 {query}에 대한 정량적 분석 결과와 시장 동향, 주요 지표들을 포함하여 의사결정에 필요한 근거 자료를 제공합니다.",
                    "source": "산업 분석 리포트",
                    "relevance_score": 0.92,
                    "keywords": keywords[:5] if keywords else ["분석", "보고서", "데이터"],
                    "user_type": user_type,
                    "document_type": "분석 보고서"
                },
                {
                    "id": "dummy_report_2",
                    "title": f"'{query}' 벤치마킹 스터디",
                    "summary": f"{query} 분야의 선도 기업들과 베스트 프랙티스 사례 연구 자료입니다.",
                    "content": f"업계 선도 기업들의 {query} 관련 전략과 성과를 분석한 벤치마킹 연구로, 비교 분석 데이터와 시사점을 제공합니다.",
                    "source": "벤치마킹 연구소",
                    "relevance_score": 0.88,
                    "keywords": keywords[:5] if keywords else ["벤치마킹", "사례", "연구"],
                    "user_type": user_type,
                    "document_type": "연구 보고서"
                }
            ]
        else:
            base_docs = [
                {
                    "id": "dummy_general_1",
                    "title": f"'{query}' 종합 가이드",
                    "summary": f"{query}에 대한 기본적인 이해부터 실무 적용까지 포괄하는 종합 자료입니다.",
                    "content": f"{query}의 개념, 중요성, 적용 방법 등을 체계적으로 설명하는 종합 가이드 문서입니다.",
                    "source": "전문 자료 DB",
                    "relevance_score": 0.8,
                    "keywords": keywords[:5] if keywords else ["가이드", "정보", "자료"],
                    "user_type": user_type,
                    "document_type": "종합 가이드"
                }
            ]
        
        return base_docs
    
    def refine_text(self, text: str, style: str = "clear", user_type: str = "general") -> str:
        """텍스트 다듬기 - 사용자 타입별 맞춤 스타일"""
        if not self.ai_available:
            return self._get_dummy_refined_text(text, style, user_type)
        
        style_prompts = {
            "clear": "명확하고 이해하기 쉽게 다듬어주세요. 복잡한 문장은 단순화하고 모호한 표현은 구체적으로 수정해주세요.",
            "professional": "전문적이고 정확한 표현으로 다듬어주세요. 해당 분야의 적절한 전문 용어를 사용하여 신뢰도를 높여주세요.",
            "concise": "간결하고 핵심적인 내용으로 다듬어주세요. 불필요한 수식어와 중복 표현을 제거해주세요.",
            "persuasive": "설득력 있고 임팩트 있게 다듬어주세요. 논리적 근거와 강력한 메시지로 구성해주세요."
        }
        
        # 사용자 타입별 추가 지침
        user_context = {
            "planner": "기획자 관점에서 실행 가능하고 구체적인 표현으로 수정해주세요.",
            "reporter": "보고서 작성자 관점에서 객관적이고 데이터 기반의 표현으로 수정해주세요.",
            "general": "일반 독자가 이해하기 쉽도록 수정해주세요."
        }
        
        try:
            system_prompt = f"""
            {style_prompts.get(style, '더 좋게')} 
            {user_context.get(user_type, '')}
            원본의 의미와 핵심 내용은 반드시 유지하면서 개선해주세요.
            """
            
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"다음 텍스트를 다듬어주세요:\n\n{text}"}
                ],
                max_tokens=min(AI_CONFIG["max_tokens"], len(text.split()) * 3),
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"텍스트 다듬기 중 오류 발생: {str(e)}")
            return self._get_dummy_refined_text(text, style, user_type)
    
    def _get_dummy_refined_text(self, text: str, style: str, user_type: str) -> str:
        """더미 텍스트 다듬기 결과"""
        if style == "clear":
            return f"[명확성 개선] {text}\n\n→ 핵심 내용을 더 명확하고 이해하기 쉽게 표현했습니다."
        elif style == "professional":
            return f"[전문성 강화] {text}\n\n→ 전문적인 표현과 정확한 용어를 사용하여 신뢰도를 높였습니다."
        elif style == "concise":
            return f"[간결성 개선] {text[:len(text)//2]}...\n\n→ 불필요한 표현을 제거하고 핵심만 남겼습니다."
        else:
            return f"[{style} 스타일] {text}\n\n→ {style} 스타일로 개선되었습니다."
    
    def structure_content(self, text: str, structure_type: str = "outline", user_type: str = "general") -> str:
        """내용 구조화 - 사용자 타입별 맞춤 구조"""
        if not self.ai_available:
            return self._get_dummy_structured_content(text, structure_type, user_type)
        
        structure_prompts = {
            "outline": "다음 내용을 목차와 소제목이 있는 체계적인 개요 형식으로 구조화해주세요.",
            "steps": "다음 내용을 단계별 가이드 형식(1단계, 2단계...)으로 구조화해주세요.",
            "qa": "다음 내용을 질문과 답변(Q&A) 형식으로 구조화해주세요.",
            "summary": "다음 내용을 핵심 요약, 상세 내용, 결론 형식으로 구조화해주세요.",
            "presentation": "다음 내용을 프레젠테이션용 슬라이드 구조로 정리해주세요."
        }
        
        # 사용자 타입별 구조화 지침
        user_guidance = {
            "planner": "실행 계획과 액션 아이템을 중심으로 구조화해주세요.",
            "reporter": "데이터와 근거를 중심으로 논리적으로 구조화해주세요.",
            "general": "독자가 이해하기 쉬운 논리적 흐름으로 구조화해주세요."
        }
        
        try:
            system_prompt = f"""
            {structure_prompts.get(structure_type, "다음 내용을 체계적으로 구조화해주세요.")}
            {user_guidance.get(user_type, '')}
            
            구조화 시 다음 사항을 고려해주세요:
            - 논리적 흐름과 연결성
            - 핵심 내용의 강조
            - 읽기 쉬운 형태
            """
            
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=AI_CONFIG["max_tokens"],
                temperature=0.4
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"내용 구조화 중 오류 발생: {str(e)}")
            return self._get_dummy_structured_content(text, structure_type, user_type)
    
    def _get_dummy_structured_content(self, text: str, structure_type: str, user_type: str) -> str:
        """더미 구조화 결과"""
        text_preview = text[:100] + "..." if len(text) > 100 else text
        
        if structure_type == "outline":
            return f"""# 주제 개요

## 1. 배경 및 현황
{text_preview}

## 2. 주요 내용
- 핵심 포인트 1: 주요 이슈 분석
- 핵심 포인트 2: 해결 방안 모색  
- 핵심 포인트 3: 기대 효과

## 3. 결론 및 제언
- 요약 정리
- 향후 계획
- 권고사항

[더미 모드로 생성된 구조입니다]"""
        
        elif structure_type == "steps":
            return f"""# 단계별 실행 가이드

**1단계: 현황 파악**
- {text_preview}
- 관련 데이터 수집 및 분석

**2단계: 계획 수립**
- 목표 설정 및 우선순위 결정
- 리소스 및 일정 계획

**3단계: 실행 및 모니터링**
- 단계별 실행
- 진행 상황 점검

**4단계: 평가 및 개선**
- 결과 분석
- 개선 방안 도출

[더미 모드로 생성된 단계입니다]"""
        
        elif structure_type == "qa":
            return f"""# Q&A 형식 정리

**Q1: 핵심 이슈는 무엇인가?**
A: {text_preview}

**Q2: 어떤 접근 방법이 필요한가?**
A: 체계적인 분석과 단계별 접근이 필요합니다.

**Q3: 기대되는 결과는?**
A: 효과적인 문제 해결과 성과 개선을 기대할 수 있습니다.

**Q4: 주의사항은?**
A: 지속적인 모니터링과 피드백이 중요합니다.

[더미 모드로 생성된 Q&A입니다]"""
        
        else:
            return f"""# 구조화된 내용

## 핵심 요약
{text_preview}

## 상세 내용
- 주요 요소들의 구체적 설명
- 관련 데이터 및 근거
- 실무 적용 방안

## 결론
요약된 결론과 향후 방향성

[더미 모드로 생성된 구조입니다]"""
    
    def enhance_user_prompt(self, user_input: str) -> str:
        """1단계: 사용자 입력을 AI가 더 잘 이해할 수 있도록 프롬프트 재생성 (캐시 적용)"""
        
        # 캐시 확인
        cache_key = self._get_cache_key("enhance_prompt", user_input)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            print(f"💾 캐시된 프롬프트 재생성 결과 사용")
            return cached_result
            
        if not self.ai_available:
            fallback = f"[프롬프트 최적화] {user_input}"
            self._set_cache(cache_key, fallback)
            return fallback
        
        try:
            system_prompt = """
            당신은 사용자의 의도를 정확히 파악하여 AI가 더 효과적으로 분석할 수 있도록 
            프롬프트를 최적화하는 전문가입니다.
            
            사용자의 입력을 분석하여:
            1. 핵심 의도와 목적을 파악하세요
            2. 구체적인 질문이나 요구사항으로 변환하세요  
            3. 검색에 유용한 키워드들을 포함하세요
            4. 명확하고 구조화된 프롬프트로 재작성하세요
            
            결과는 AI가 더 정확한 분석을 할 수 있도록 구체적이고 명확해야 합니다.
            """
            
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"다음 사용자 입력을 분석하여 AI가 더 잘 이해할 수 있는 구체적인 프롬프트로 재생성해주세요:\n\n{user_input}"}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            
            # 결과 캐시 저장
            self._set_cache(cache_key, enhanced_prompt)
            return enhanced_prompt
            
        except Exception as e:
            print(f"프롬프트 재생성 실패: {e}")
            fallback = f"[최적화된 프롬프트] {user_input} - 구체적인 분석 요청"
            self._set_cache(cache_key, fallback)
            return fallback
    
    def search_internal_documents(self, enhanced_prompt: str) -> List[Dict[str, Any]]:
        """2-1단계: 사내 문서 RAG 검색 (Azure AI Search) - 캐시 적용"""
        
        # 캐시 확인
        cache_key = self._get_cache_key("internal_search", enhanced_prompt)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            print(f"💾 캐시된 사내 검색 결과 사용")
            return cached_result
            
        try:
            if self.azure_search_available:
                # 실제 Azure Search API 호출
                result = self._search_azure_search_api(enhanced_prompt)
                self._set_cache(cache_key, result)
                return result
            else:
                # Azure Search 사용 불가능시 로컬 검색
                result = self._search_local_documents(enhanced_prompt)
                self._set_cache(cache_key, result)
                return result
            
        except Exception as e:
            print(f"사내 문서 검색 실패: {e}")
            fallback = self._get_dummy_internal_results(enhanced_prompt)
            self._set_cache(cache_key, fallback)
            return fallback
    
    def _search_azure_search_api(self, query: str) -> List[Dict[str, Any]]:
        """실제 Azure Search API 검색"""
        import requests
        
        try:
            # Azure Search REST API 호출
            search_url = f"{self.azure_search_endpoint}/indexes/{self.azure_search_index}/docs/search"
            
            headers = {
                'Content-Type': 'application/json',
                'api-key': self.azure_search_key
            }
            
            # 검색 쿼리 구성
            search_body = {
                "search": query,
                "searchMode": "any",
                "queryType": "simple",
                "select": "*",  # 모든 필드 선택 (실제로는 필요한 필드만 선택)
                "top": 10,  # 최대 10개 결과
                "highlight": "content",  # 내용 하이라이트
                "count": True
            }
            
            params = {
                'api-version': self.azure_search_api_version
            }
            
            print(f"🔍 Azure Search API 호출: {query}")
            response = requests.post(search_url, headers=headers, json=search_body, params=params)
            
            if response.status_code == 200:
                results = response.json()
                documents = results.get('value', [])
                total_count = results.get('@odata.count', 0)
                
                print(f"✅ Azure Search 결과: {len(documents)}개 (총 {total_count}개)")
                
                # 결과 변환
                converted_docs = []
                for i, doc in enumerate(documents):
                    converted_doc = {
                        "id": doc.get("id", f"azure_doc_{i}"),
                        "title": doc.get("title", doc.get("Title", "제목 없음")),
                        "content": doc.get("content", doc.get("Content", "")),
                        "summary": self._extract_summary_from_azure_doc(doc),
                        "source_detail": f"Azure AI Search - {self.azure_search_index}",
                        "relevance_score": doc.get("@search.score", 1.0) / 10.0,  # 점수 정규화
                        "search_type": "azure_search",
                        "keywords": self._extract_keywords_from_azure_doc(doc),
                        "highlights": doc.get("@search.highlights", {})
                    }
                    converted_docs.append(converted_doc)
                
                return converted_docs[:5]  # 상위 5개
                
            else:
                print(f"❌ Azure Search API 오류: {response.status_code} - {response.text}")
                return self._search_local_documents(query)
                
        except Exception as e:
            print(f"❌ Azure Search API 호출 실패: {e}")
            return self._search_local_documents(query)
    
    def _extract_summary_from_azure_doc(self, doc: Dict) -> str:
        """Azure Search 문서에서 요약 추출"""
        # 다양한 필드명 시도
        summary_fields = ["summary", "Summary", "description", "Description", "abstract", "Abstract"]
        
        for field in summary_fields:
            if field in doc and doc[field]:
                return doc[field][:300] + "..." if len(doc[field]) > 300 else doc[field]
        
        # 요약 필드가 없으면 content에서 첫 부분 추출
        content = doc.get("content", doc.get("Content", ""))
        if content:
            sentences = content.split('.')[:3]  # 처음 3문장
            return '. '.join(sentences) + "..." if len(sentences) >= 3 else content[:200] + "..."
        
        return "요약 없음"
    
    def _extract_keywords_from_azure_doc(self, doc: Dict) -> List[str]:
        """Azure Search 문서에서 키워드 추출"""
        # 키워드 필드가 있으면 사용
        keyword_fields = ["keywords", "Keywords", "tags", "Tags", "categories", "Categories"]
        
        for field in keyword_fields:
            if field in doc and doc[field]:
                if isinstance(doc[field], list):
                    return doc[field][:5]
                elif isinstance(doc[field], str):
                    return doc[field].split(',')[:5]
        
        # 키워드 필드가 없으면 제목과 내용에서 추출
        text = (doc.get("title", "") + " " + doc.get("content", "")).lower()
        return self._extract_keywords(text)[:5]
    
    def _search_local_documents(self, enhanced_prompt: str) -> List[Dict[str, Any]]:
        """로컬 샘플 데이터에서 검색 (Azure Search 대체)"""
        try:
            # 로컬 샘플 데이터에서 관련 문서 검색
            with open('data/sample_documents.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = data.get("documents", [])
            
            # 검색어 기반 관련도 계산
            search_terms = enhanced_prompt.lower().split()
            relevant_docs = []
            
            for doc in documents:
                relevance_score = 0
                content = (doc.get("title", "") + " " + doc.get("content", "") + " " + " ".join(doc.get("keywords", []))).lower()
                
                # 키워드 매칭으로 관련도 계산
                for term in search_terms:
                    if term in content:
                        relevance_score += content.count(term) * 0.1
                
                if relevance_score > 0.3:
                    doc_copy = doc.copy()
                    doc_copy["relevance_score"] = min(1.0, relevance_score)
                    doc_copy["search_type"] = "local_search"
                    doc_copy["source_detail"] = f"로컬 문서 DB - {doc.get('source', 'Unknown')}"
                    relevant_docs.append(doc_copy)
            
            # 관련도순 정렬
            relevant_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
            print(f"📁 로컬 검색 결과: {len(relevant_docs)}개")
            return relevant_docs[:5]  # 상위 5개
            
        except Exception as e:
            print(f"로컬 문서 검색 실패: {e}")
            return self._get_dummy_internal_results(enhanced_prompt)
    
    def _get_dummy_internal_results(self, enhanced_prompt: str) -> List[Dict[str, Any]]:
        """더미 사내 문서 결과"""
        return [
            {
                "id": "internal_1",
                "title": "사내 정책 문서 - 관련 가이드라인",
                "summary": f"'{enhanced_prompt[:30]}...'와 관련된 사내 정책 및 가이드라인입니다.",
                "content": f"사내에서 {enhanced_prompt[:50]}...에 대한 표준 절차와 방법론을 정의한 문서입니다.",
                "source_detail": "사내 문서 관리 시스템 (더미)",
                "relevance_score": 0.9,
                "search_type": "dummy",
                "keywords": ["정책", "가이드라인", "절차"]
            }
        ]
    
    def search_external_references(self, enhanced_prompt: str) -> List[Dict[str, Any]]:
        """2-2단계: 사외 인터넷 검색 (Tavily) - 유사사례, 레퍼런스 (캐시 적용)"""
        
        # 캐시 확인
        cache_key = self._get_cache_key("external_search", enhanced_prompt)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            print(f"💾 캐시된 외부 검색 결과 사용")
            return cached_result
            
        try:
            if self.search_available and self.tavily_client:
                # Tavily로 실제 웹 검색 (디버깅 로그 추가)
                # enhanced_prompt가 너무 길면 처음 100자만 사용
                short_prompt = enhanced_prompt[:100] if len(enhanced_prompt) > 100 else enhanced_prompt
                search_query = f"{short_prompt} 사례 레퍼런스 best practice"
                print(f"🔍 Tavily 외부검색 호출: query='{search_query}', depth=advanced, max=6")
                response = self.tavily_client.search(
                    query=search_query,
                    search_depth="advanced",
                    max_results=6
                )
                print(f"✅ Tavily 외부검색 응답: {len(response.get('results', []))}개 결과")
                
                external_docs = []
                for i, result in enumerate(response.get("results", [])):
                    doc = {
                        "id": f"external_{i+1}",
                        "title": result.get("title", "제목 없음"),
                        "summary": result.get("content", "")[:300] + "...",
                        "content": result.get("content", ""),
                        "source_detail": f"외부 참조 - {result.get('url', '')}",
                        "url": result.get("url", ""),
                        "relevance_score": result.get("score", 0.5),
                        "search_type": "external",
                        "keywords": self._extract_keywords(result.get("content", ""))[:5]
                    }
                    external_docs.append(doc)
                
                # 결과 캐시 저장
                self._set_cache(cache_key, external_docs)
                return external_docs
                
            else:
                # Tavily 사용 불가능시 더미 데이터
                fallback = self._get_dummy_external_results(enhanced_prompt)
                self._set_cache(cache_key, fallback)
                return fallback
                
        except Exception as e:
            print(f"❌ 외부 검색 실패: {str(e)}")
            print(f"❌ 오류 타입: {type(e).__name__}")
            import traceback
            print(f"❌ 상세 오류:\n{traceback.format_exc()}")
            fallback = self._get_dummy_external_results(enhanced_prompt)
            self._set_cache(cache_key, fallback)
            return fallback
    
    def _get_dummy_external_results(self, enhanced_prompt: str) -> List[Dict[str, Any]]:
        """외부 검색 더미 결과"""
        return [
            {
                "id": "external_1",
                "title": f"Best Practices for {enhanced_prompt[:30]}... - Industry Report",
                "summary": f"업계에서 검증된 {enhanced_prompt[:20]}...에 대한 모범 사례와 성공 사례들을 정리한 보고서입니다.",
                "content": f"다양한 기업들이 {enhanced_prompt[:30]}... 관련 프로젝트에서 얻은 인사이트와 교훈들을 종합한 자료입니다.",
                "source_detail": "외부 참조 - Industry Research Portal",
                "url": "https://example.com/best-practices",
                "relevance_score": 0.85,
                "search_type": "external",
                "keywords": ["best practice", "industry", "case study"]
            },
            {
                "id": "external_2", 
                "title": f"Case Study: Successful Implementation of {enhanced_prompt[:25]}...",
                "summary": f"실제 기업에서 {enhanced_prompt[:20]}...를 성공적으로 구현한 사례 연구입니다.",
                "content": f"A사에서 {enhanced_prompt[:30]}... 프로젝트를 통해 얻은 성과와 구현 과정의 세부사항을 다룹니다.",
                "source_detail": "외부 참조 - Business Case Studies",
                "url": "https://example.com/case-study",
                "relevance_score": 0.82,
                "search_type": "external", 
                "keywords": ["case study", "implementation", "success"]
            }
        ]
    
    def generate_optimized_analysis(self, enhanced_prompt: str, internal_docs: List[Dict], external_docs: List[Dict], original_input: str) -> Dict[str, Any]:
        """3단계: 최적화된 통합 분석 결과 생성 (단일 API 호출)"""
        try:
            if not self.ai_available:
                return self._get_fallback_analysis(enhanced_prompt, internal_docs, external_docs)
            
            # 검색 결과 요약
            internal_summary = self._summarize_search_results(internal_docs, "사내 문서")
            external_summary = self._summarize_search_results(external_docs, "외부 레퍼런스")
            
            # 통합 분석을 위한 프롬프트 구성
            system_prompt = """당신은 전문적인 비즈니스 분석가입니다. 
사용자의 요청을 분석하고, 제공된 사내 문서와 외부 레퍼런스를 종합하여 
실용적이고 구체적인 분석 결과를 제공해주세요.

분석 결과는 다음 구조로 작성해주세요:
1. 요약 및 핵심 인사이트
2. 사내 관점 분석
3. 외부 벤치마킹 분석
4. 통합 권고사항
5. 구체적 실행 방안"""

            user_prompt = f"""
## 분석 요청
**원본 입력:** {original_input}
**최적화된 분석 범위:** {enhanced_prompt}

## 검색 결과
### 사내 문서 분석
{internal_summary}

### 외부 레퍼런스 분석
{external_summary}

위 정보를 바탕으로 종합적이고 실용적인 분석 결과를 제공해주세요.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis_content = response.choices[0].message.content
            
            return {
                "title": "🎯 통합 AI 분석 결과",
                "content": analysis_content,
                "internal_docs_count": len(internal_docs),
                "external_docs_count": len(external_docs),
                "confidence": 0.9,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"최적화된 분석 생성 실패: {e}")
            return self._get_fallback_analysis(enhanced_prompt, internal_docs, external_docs)
    
    def _get_fallback_analysis(self, prompt: str, internal_docs: List[Dict], external_docs: List[Dict]) -> Dict[str, Any]:
        """API 호출 실패 시 폴백 분석"""
        return {
            "title": "📋 기본 분석 결과",
            "content": f"""
## 📋 분석 결과 (폴백 모드)

### 🎯 분석 요청
{prompt[:200]}...

### 📊 검색 결과 요약
- **사내 문서**: {len(internal_docs)}개 문서 검색됨
- **외부 레퍼런스**: {len(external_docs)}개 참조 자료 발견

### 💡 기본 인사이트
검색된 자료들을 바탕으로 추가 분석이 필요합니다. 
AI 서비스 연결 후 다시 시도해주세요.

### 🔍 참고 자료
""" + "\n".join([f"- {doc.get('title', 'N/A')}" for doc in (internal_docs + external_docs)[:5]]),
            "internal_docs_count": len(internal_docs),
            "external_docs_count": len(external_docs),
            "confidence": 0.5,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def generate_multiple_analysis_versions(self, enhanced_prompt: str, internal_docs: List[Dict], external_docs: List[Dict], original_input: str) -> List[Dict[str, Any]]:
        """3단계: 여러 버전의 분석 결과 생성 (레거시 지원용)"""
        try:
            # 최적화된 버전을 사용하되, 기존 형식으로 래핑
            optimized_result = self.generate_optimized_analysis(enhanced_prompt, internal_docs, external_docs, original_input)
            
            # 기존 다중 버전 형식으로 변환
            return [{
                "title": optimized_result["title"],
                "description": "사내 문서와 외부 레퍼런스를 통합한 최적화된 분석",
                "content": optimized_result["content"],
                "priority": 1,
                "confidence": optimized_result["confidence"]
            }]
            
        except Exception as e:
            print(f"다중 버전 생성 실패: {e}")
            return self._get_dummy_analysis_versions(enhanced_prompt, original_input)
    
    def _summarize_search_results(self, docs: List[Dict], source_type: str) -> str:
        """검색 결과 요약"""
        if not docs:
            return f"{source_type}에서 관련 자료를 찾지 못했습니다."
        
        summaries = []
        for doc in docs[:3]:  # 상위 3개만
            title = doc.get("title", "제목 없음")
            summary = doc.get("summary", "")[:100]
            summaries.append(f"- {title}: {summary}...")
        
        return f"{source_type} 검색 결과 ({len(docs)}개):\n" + "\n".join(summaries)
    
    def _generate_comprehensive_version(self, prompt: str, internal_summary: str, external_summary: str, original_input: str) -> Dict[str, Any]:
        """종합 분석 버전"""
        return {
            "title": "🎯 종합 분석 (사내+외부 통합)",
            "description": "사내 문서와 외부 레퍼런스를 종합한 균형잡힌 분석",
            "content": f"""
## 🎯 종합 분석 결과

### 📋 분석 개요
**원본 요청:** {original_input[:100]}...
**최적화된 분석 범위:** {prompt[:150]}...

### 🏢 사내 관점
{internal_summary}

### 🌐 외부 벤치마킹
{external_summary}

### 💡 통합 인사이트
1. **사내-외부 gap 분석**: 현재 사내 방식과 업계 모범사례 비교
2. **적용 가능한 외부 사례**: 우리 조직에 적합한 레퍼런스 식별  
3. **균형잡힌 접근법**: 내부 역량과 외부 트렌드를 모두 고려한 방향성

### 🚀 통합 실행 방안
- 단기: 사내 기준 보완 + 외부 모범사례 일부 도입
- 중기: 점진적 외부 표준 적용 
- 장기: 사내 고유 모델과 업계 표준의 최적 조합
""",
            "priority": 1,
            "confidence": 0.9
        }
    
    def _generate_internal_focused_version(self, prompt: str, internal_docs: List[Dict], original_input: str) -> Dict[str, Any]:
        """사내 중심 분석 버전"""
        return {
            "title": "🏢 사내 정책 중심 분석", 
            "description": "기존 사내 문서와 정책을 기반으로 한 분석",
            "content": f"""
## 🏢 사내 정책 중심 분석

### 📋 분석 기준
기존 사내 문서, 정책, 가이드라인을 기반으로 현실적이고 실행 가능한 방안을 제시합니다.

### 📚 참조 사내 자료
""" + "\n".join([f"- {doc.get('title', '')}: {doc.get('summary', '')[:100]}..." for doc in internal_docs[:3]]) + f"""

### 💼 사내 관점 분석
1. **현행 정책 부합성**: 기존 사내 규정과의 정합성 검토
2. **내부 리소스 활용**: 현재 가용한 인력, 예산, 시스템 고려
3. **조직 문화 적합성**: 우리 조직의 특성에 맞는 접근법

### 🎯 사내 실행 방안
- **즉시 실행 가능**: 기존 프로세스 개선
- **단기 적용**: 현행 정책 범위 내 변화
- **승인 필요**: 정책 변경이 필요한 중장기 계획
""",
            "priority": 2,
            "confidence": 0.85
        }
    
    def _generate_external_focused_version(self, prompt: str, external_docs: List[Dict], original_input: str) -> Dict[str, Any]:
        """외부 벤치마킹 중심 분석 버전"""  
        return {
            "title": "🌐 외부 벤치마킹 분석",
            "description": "업계 모범사례와 외부 레퍼런스 중심의 혁신적 접근",
            "content": f"""
## 🌐 외부 벤치마킹 분석

### 🎯 분석 관점
업계 선도 기업들의 모범사례와 최신 트렌드를 바탕으로 혁신적 방안을 제시합니다.

### 📊 외부 레퍼런스
""" + "\n".join([f"- {doc.get('title', '')}: {doc.get('summary', '')[:100]}..." for doc in external_docs[:3]]) + f"""

### 🏆 업계 모범사례 분석
1. **선도기업 사례**: 업계 1위 기업들의 접근법 
2. **혁신적 방법론**: 최신 트렌드와 신기술 활용
3. **성공 요인**: 외부 성공사례의 핵심 포인트

### 🚀 혁신 실행 방안  
- **벤치마킹 포인트**: 즉시 참고할 수 있는 외부 사례
- **적용 로드맵**: 단계적 도입을 위한 계획
- **차별화 전략**: 우리만의 고유한 경쟁우위 창출
""",
            "priority": 3,
            "confidence": 0.8
        }
    
    def _generate_action_focused_version(self, prompt: str, internal_summary: str, external_summary: str, original_input: str) -> Dict[str, Any]:
        """실행 계획 중심 분석 버전"""
        return {
            "title": "⚡ 실행 계획 중심 분석",
            "description": "구체적이고 실행 가능한 액션 플랜 중심의 분석", 
            "content": f"""
## ⚡ 실행 계획 중심 분석

### 🎯 실행 우선순위
즉시 실행 가능한 것부터 단계적으로 추진할 수 있는 구체적 방안을 제시합니다.

### 🚀 즉시 실행 (1-2주)
1. **현황 파악**: 관련 데이터 수집 및 분석  
2. **팀 구성**: 실행 담당자 및 지원팀 편성
3. **초기 계획**: 세부 실행 계획 수립

### 📅 단기 실행 (1-3개월)  
1. **파일럿 운영**: 소규모 테스트 실행
2. **피드백 수집**: 초기 결과 분석 및 개선점 파악
3. **프로세스 정립**: 표준 운영 절차 확립

### 🎯 중장기 실행 (3-12개월)
1. **전면 도입**: 조직 전체로 확대 적용  
2. **성과 측정**: KPI 기반 성과 평가
3. **지속 개선**: 정기적 리뷰 및 업데이트

### 📊 필요 리소스 및 예산
- **인력**: 프로젝트 매니저 1명, 실행팀 3-5명
- **예산**: 초기 투자 및 운영 비용 계획
- **시스템**: 필요 도구 및 인프라 구축
""",
            "priority": 4, 
            "confidence": 0.9
        }
    
    def _get_dummy_analysis_versions(self, enhanced_prompt: str, original_input: str) -> List[Dict[str, Any]]:
        """더미 분석 버전들"""
        return [
            {
                "title": "🎯 종합 분석 (더미)",
                "description": "사내외 자료를 종합한 균형잡힌 분석",
                "content": f"[더미 모드] {enhanced_prompt}에 대한 종합적 분석 결과입니다.",
                "priority": 1,
                "confidence": 0.7
            },
            {
                "title": "🏢 사내 정책 중심 (더미)",
                "description": "기존 사내 기준에 맞춘 현실적 방안",
                "content": f"[더미 모드] 사내 정책을 기반으로 한 {enhanced_prompt} 분석입니다.",
                "priority": 2, 
                "confidence": 0.7
            }
        ]

    def generate_action_plan(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """분석 결과 기반 액션 플랜 생성"""
        if not self.ai_available:
            return self._get_dummy_action_plan(analysis_result)
        
        try:
            text = analysis_result.get("original_text", "")
            user_type = analysis_result.get("user_type", "general")
            analysis = analysis_result.get("analysis", {})
            
            system_prompt = f"""
            다음 분석 결과를 바탕으로 구체적이고 실행 가능한 액션 플랜을 생성해주세요.
            
            사용자 타입: {user_type}
            
            액션 플랜에는 다음을 포함해주세요:
            1. 즉시 실행 항목 (1-3개)
            2. 단기 계획 (1주-1개월)
            3. 중장기 계획 (1-6개월)
            4. 필요 리소스
            5. 성공 지표
            """
            
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"분석 내용: {text}\n\n분석 결과: {analysis}"}
                ],
                max_tokens=AI_CONFIG["max_tokens"],
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            
            return {
                "action_plan": content,
                "user_type": user_type,
                "generated_at": time.time()
            }
            
        except Exception as e:
            st.error(f"액션 플랜 생성 중 오류: {str(e)}")
            return self._get_dummy_action_plan(analysis_result)
    
    def _get_dummy_action_plan(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """더미 액션 플랜"""
        user_type = analysis_result.get("user_type", "general")
        
        if user_type == "planner":
            plan = """# 기획 실행 액션 플랜

## 🚀 즉시 실행 항목
1. 현황 분석 데이터 수집
2. 핵심 이해관계자 미팅 일정 조율
3. 프로젝트 범위 및 목표 명확화

## 📅 단기 계획 (1주-1개월)
- 상세 기획서 작성
- 예산 및 리소스 계획 수립
- 팀 구성 및 역할 배정

## 🎯 중장기 계획 (1-6개월)
- 단계별 실행 및 모니터링
- 중간 평가 및 조정
- 성과 측정 및 보고

## 📊 필요 리소스
- 인력: 기획팀, 실행팀
- 예산: 프로젝트 규모에 따라
- 시스템: 협업 도구, 분석 도구

## ✅ 성공 지표
- 목표 달성률
- 일정 준수율
- 품질 만족도"""
        
        elif user_type == "reporter":
            plan = """# 보고서 작성 액션 플랜

## 🚀 즉시 실행 항목
1. 보고서 목적과 대상 독자 명확화
2. 필요 데이터 및 자료 리스트 작성
3. 보고서 구조 및 목차 초안 작성

## 📅 단기 계획 (1주-1개월)
- 데이터 수집 및 분석
- 초안 작성 및 검토
- 시각 자료(차트, 그래프) 제작

## 🎯 중장기 계획 (1-6개월)
- 정기 보고서 템플릿 개발
- 데이터 수집 자동화 시스템 구축
- 보고서 품질 개선 프로세스 정립

## 📊 필요 리소스
- 데이터: 관련 통계, 분석 자료
- 도구: 분석 소프트웨어, 디자인 툴
- 시간: 충분한 검토 및 수정 기간

## ✅ 성공 지표
- 보고서 완성도
- 데이터 정확성
- 독자 만족도"""
        
        else:
            plan = """# 종합 액션 플랜

## 🚀 즉시 실행 항목
1. 핵심 이슈 정리 및 우선순위 설정
2. 관련 자료 및 정보 수집
3. 실행 팀 구성 및 역할 분담

## 📅 단기 계획 (1주-1개월)
- 세부 계획 수립
- 초기 실행 및 테스트
- 피드백 수집 및 개선

## 🎯 중장기 계획 (1-6개월)
- 본격적인 실행 단계
- 성과 모니터링 및 조정
- 최종 평가 및 정리

## 📊 필요 리소스
- 인력: 다양한 분야 전문가
- 도구: 업무 효율성 도구
- 예산: 프로젝트 규모별 적정 예산

## ✅ 성공 지표
- 목표 달성 여부
- 효율성 개선도
- 만족도 평가"""
        
        return {
            "action_plan": plan,
            "user_type": user_type,
            "generated_at": time.time()
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출 - 개선된 알고리즘"""
        if not text.strip():
            return []
        
        # 불용어 리스트 (한국어)
        stop_words = {
            '있는', '있어', '있다', '그리고', '하지만', '그러나', '또한', '그런데',
            '이는', '이것', '그것', '저것', '여기서', '거기서', '저기서', '때문에',
            '따라서', '그래서', '하는', '하고', '한다', '됩니다', '입니다', '입니다.',
            '것을', '것이', '것은', '수', '등', '및', '또는', '그리고', '의', '를', '을',
            '이', '가', '은', '는', '에', '에서', '로', '으로', '과', '와', '도', '만',
            '부터', '까지', '위해', '대해', '대한', '통해', '위한', '같은', '다른'
        }
        
        # 텍스트 전처리
        import re
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        words = text.split()
        
        # 키워드 후보 추출
        keyword_candidates = []
        for word in words:
            clean_word = word.strip().lower()
            
            # 길이 제한 및 불용어 제거
            if (len(clean_word) > 2 and 
                clean_word not in stop_words and
                not clean_word.isdigit()):
                keyword_candidates.append(clean_word)
        
        # 빈도수 계산
        from collections import Counter
        word_freq = Counter(keyword_candidates)
        
        # 상위 빈도 키워드 추출 (최대 10개)
        top_keywords = [word for word, freq in word_freq.most_common(10)]
        
        return top_keywords
    
    def _extract_topic(self, content: str) -> str:
        """주제 추출 - 개선된 알고리즘"""
        if not content:
            return "주제 추출 실패"
        
        lines = content.split('\n')
        
        # 주제를 나타낼 수 있는 패턴들
        topic_patterns = [
            r'주제[:\s]*(.+)',
            r'topic[:\s]*(.+)',
            r'제목[:\s]*(.+)',
            r'title[:\s]*(.+)',
            r'핵심[:\s]*(.+)',
            r'#\s*(.+)'  # 마크다운 제목
        ]
        
        for line in lines[:5]:  # 첫 5줄에서 찾기
            line = line.strip()
            for pattern in topic_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    topic = match.group(1).strip()
                    if len(topic) > 5 and len(topic) < 100:  # 적절한 길이
                        return topic
        
        # 패턴으로 찾지 못한 경우 첫 번째 문장 사용
        sentences = content.split('.')
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if len(sentence) > 10 and len(sentence) < 100:
                return sentence + "."
        
        return "주제 분석 필요"
    
    def _extract_summary(self, content: str) -> str:
        """요약 추출 - 개선된 알고리즘"""
        if not content:
            return "요약 없음"
        
        lines = content.split('\n')
        
        # 요약을 나타낼 수 있는 패턴들
        summary_patterns = [
            r'요약[:\s]*(.+)',
            r'summary[:\s]*(.+)', 
            r'핵심[:\s]*(.+)',
            r'결론[:\s]*(.+)',
            r'개요[:\s]*(.+)'
        ]
        
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in summary_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    summary_lines.append(match.group(1).strip())
        
        if summary_lines:
            summary = ' '.join(summary_lines)
            if len(summary) > 20:
                return summary[:200] + "..." if len(summary) > 200 else summary
        
        # 패턴으로 찾지 못한 경우 내용의 처음 부분 사용
        sentences = content.split('.')
        key_sentences = []
        
        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if len(sentence) > 20:  # 의미있는 문장 길이
                key_sentences.append(sentence)
                if len(' '.join(key_sentences)) > 150:
                    break
        
        if key_sentences:
            summary = '. '.join(key_sentences[:2]) + "."
            return summary[:200] + "..." if len(summary) > 200 else summary
        
        return "요약 생성 필요"
