# AI 분석 문제 해결 완료

## 🐛 발견된 문제
사용자가 보고한 대로, AI 패널에서 **본문 내용이 아닌 입력창(input)의 텍스트만으로 AI 분석을 실행하는 문제**가 있었습니다.

### 문제 상황
- 사용자가 문서 본문에 긴 내용을 작성
- "전체분석하기" 버튼 클릭
- AI 패널에서 "분석 목적/질문" 입력창에 입력한 짧은 텍스트만 분석
- **실제 문서 본문 내용은 분석되지 않음**

## 🔧 근본 원인 분석
1. **AI 사이드바에서 잘못된 매개변수 전달**
   - `_execute_analysis` 함수에서 `selection` 매개변수가 잘못 처리됨
   - 전체 문서 분석 시에도 `selection=None`으로 전달

2. **오케스트레이터에서 문서 내용 누락** 
   - `_refine_prompt`에서 문서 내용을 제대로 포함하지 못함
   - AI 서비스에 사용자 질문만 전달되고 실제 분석할 문서는 전달 안됨

3. **AI 서비스에서 불완전한 컨텍스트**
   - `generate_comprehensive_analysis`에서 문서 내용 매개변수 부재
   - 참고 자료만 있고 정작 분석할 핵심 문서가 빠짐

## ✅ 해결 방안 구현

### 1. AI 사이드바 수정 (`ui/ai_sidebar.py`)
```python
def _execute_analysis(user_input: str, analysis_text: str, mode: str):
    # 분석 모드와 텍스트 결정 개선
    if mode == 'selected_text':
        orchestrator_mode = "selection"
        selection = analysis_text
    elif mode == 'full_document':
        orchestrator_mode = "full"
        # 전체 문서 분석시에는 문서 내용을 selection으로 전달
        selection = analysis_text  # ✅ 핵심 수정
    else:
        orchestrator_mode = "full"
        # 수동 모드에서는 현재 문서 내용 사용
        selection = st.session_state.get('document_content', '') or analysis_text
```

### 2. 오케스트레이터 개선 (`services/ai_analysis_orchestrator_refactored.py`)
```python
def _refine_prompt(self, user_input: str, selection: str = None) -> str:
    # 분석 대상 문서 내용을 명확히 포함
    if selection and selection.strip():
        context = f"사용자 요청: {user_input}\n\n분석 대상 문서 내용:\n{selection[:2000]}..."
        # ✅ 실제 문서 내용을 컨텍스트에 포함
```

```python
def _get_analysis_target_content(self) -> str:
    """분석 대상 문서 내용 가져오기"""
    # 여러 소스에서 문서 내용을 순서대로 확인
    analysis_text = st.session_state.get('analysis_text', '')
    # ✅ 분석할 실제 문서 내용 확보
```

### 3. AI 서비스 확장 (`utils/ai_service.py`)
```python
def generate_comprehensive_analysis(self, query: str, internal_docs: List[Dict], 
                                   external_docs: List[Dict], document_content: str = "") -> str:
    # ✅ document_content 매개변수 추가
    context = self._build_comprehensive_context(query, document_content, internal_docs, external_docs)
```

```python
def _build_comprehensive_context(self, query: str, document_content: str, 
                                internal_docs: List[Dict], external_docs: List[Dict]) -> str:
    context = f"사용자 요청: {query}\n\n"
    
    # ✅ 분석 대상 문서 내용을 가장 먼저 배치
    if document_content and document_content.strip():
        context += f"===== 분석 대상 문서 내용 =====\n{document_content}\n\n"
```

## 🎯 개선 결과

### Before (문제 상황)
```
사용자 입력: "문서를 분석해주세요"
AI가 받는 내용: "문서를 분석해주세요" (질문만)
→ 실제 문서 본문 내용은 분석 안됨 ❌
```

### After (해결 후)
```
사용자 입력: "문서를 분석해주세요"  
AI가 받는 내용: 
- 사용자 요청: "문서를 분석해주세요"
- 분석 대상 문서 내용: [실제 본문 2000자...]
- 사내 참고 문서: [검색된 문서들]
- 외부 참고 자료: [검색된 자료들]
→ 완전한 컨텍스트로 정확한 분석 ✅
```

## 🧪 테스트 방법
1. http://localhost:8502 접속
2. "새문서 생성" 메뉴 선택  
3. 문서 내용에 긴 텍스트 입력
4. "전체분석하기" 버튼 클릭
5. AI 패널에서 "분석 대상 텍스트 미리보기"에 **실제 문서 내용** 표시 확인
6. 분석 결과가 입력창 텍스트가 아닌 **실제 문서 본문 기반**으로 생성되는지 확인

## 📋 수정된 파일
- `ui/ai_sidebar.py` - 문서 내용 전달 로직 수정
- `services/ai_analysis_orchestrator_refactored.py` - 분석 대상 문서 처리 개선  
- `utils/ai_service.py` - 완전한 컨텍스트 구성으로 AI 분석 품질 향상

이제 AI 분석이 **사용자가 작성한 실제 문서 본문을 기준으로** 정확하게 수행됩니다! 🎉