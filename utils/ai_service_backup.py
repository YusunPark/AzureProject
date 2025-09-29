"""
AI 서비스 모듈 - Azure OpenAI와 Tavily 검색을 사용
기획자와 보고서 제작자를 위한 전문 분석 도구
"""
import openai
import time
import streamlit as st
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from tavily import TavilyClient
from config import AI_CONFIG, TAVILY_CONFIG

class AIService:
    def __init__(self):
        # Azure OpenAI 설정
        try:
            if AI_CONFIG["openai_api_key"] and AI_CONFIG["openai_endpoint"]:
                self.client = openai.AzureOpenAI(
                    azure_endpoint=AI_CONFIG["openai_endpoint"],
                    api_key=AI_CONFIG["openai_api_key"],
                    api_version=AI_CONFIG["api_version"]
                )
                self.ai_available = True
            else:
                self.client = None
                self.ai_available = False
                print("⚠️ Azure OpenAI 설정이 없습니다. 더미 모드로 작동합니다.")
        except Exception as e:
            self.client = None
            self.ai_available = False
            print(f"⚠️ Azure OpenAI 초기화 실패: {e}")
        
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
                # 간단한 테스트 호출
                response = self.client.chat.completions.create(
                    model=AI_CONFIG["deployment_name"],
                    messages=[{"role": "user", "content": "안녕하세요. 간단히 인사해주세요."}],
                    max_tokens=50,
                    temperature=0.1
                )
                result["test_response"] = response.choices[0].message.content
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
            
            response = self.client.chat.completions.create(
                model=AI_CONFIG["deployment_name"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"다음 텍스트를 분석해주세요:\n\n{text}"}
                ],
                max_tokens=AI_CONFIG["max_tokens"],
                temperature=AI_CONFIG["temperature"]
            )
            
            print("✅ Azure OpenAI API 호출 성공!")
            print(f"📊 응답 길이: {len(response.choices[0].message.content)} 문자")
            
            content = response.choices[0].message.content
            
            # 구조화된 분석 결과 생성
            analysis_result = self._parse_analysis_response(content, user_type)
            
            return {
                "keywords": self._extract_keywords(text),
                "topic": self._extract_topic(content),
                "summary": self._extract_summary(content),
                "analysis": analysis_result,
                "user_type": user_type,
                "original_text": text[:500] + "..." if len(text) > 500 else text
            }
            
        except Exception as e:
            print(f"❌ Azure OpenAI API 호출 실패: {str(e)}")
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
            
            # Tavily 검색 실행
            response = self.tavily_client.search(
                query=search_query,
                search_depth=TAVILY_CONFIG["search_depth"],
                max_results=TAVILY_CONFIG["max_results"],
                include_domains=self._get_relevant_domains(user_type)
            )
            
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
