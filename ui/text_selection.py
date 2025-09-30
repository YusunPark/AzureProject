"""
텍스트 선택 감지 컴포넌트
"""
import streamlit as st
import streamlit.components.v1 as components

def render_text_selection_detector():
    """텍스트 선택 감지를 위한 JavaScript 컴포넌트"""
    
    # JavaScript 코드로 텍스트 선택 감지
    selection_js = """
    <script>
    function getSelectedText() {
        let selectedText = '';
        if (window.getSelection) {
            selectedText = window.getSelection().toString();
        } else if (document.selection && document.selection.type != "Control") {
            selectedText = document.selection.createRange().text;
        }
        return selectedText;
    }
    
    // 텍스트 선택 이벤트 리스너
    document.addEventListener('mouseup', function() {
        const selectedText = getSelectedText();
        if (selectedText && selectedText.trim().length > 0) {
            // Streamlit과 통신하기 위한 이벤트
            window.parent.postMessage({
                type: 'textSelected',
                text: selectedText.trim()
            }, '*');
        }
    });
    
    // 텍스트 선택 해제 이벤트
    document.addEventListener('mousedown', function() {
        setTimeout(function() {
            const selectedText = getSelectedText();
            if (!selectedText || selectedText.trim().length === 0) {
                window.parent.postMessage({
                    type: 'textDeselected'
                }, '*');
            }
        }, 100);
    });
    </script>
    
    <style>
    .selectable-text {
        user-select: text;
        -webkit-user-select: text;
        -moz-user-select: text;
        -ms-user-select: text;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #f9f9f9;
        margin: 10px 0;
    }
    
    .selected-text-info {
        background-color: #e7f3ff;
        border: 1px solid #0066cc;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    </style>
    """
    
    # JavaScript 컴포넌트 렌더링
    components.html(selection_js, height=0)

def render_selectable_document_area():
    """선택 가능한 문서 영역 렌더링"""
    
    # 현재 문서 내용
    document_content = st.session_state.get('document_content', '')
    
    if not document_content:
        st.info("📝 문서에 내용을 입력하면 텍스트를 선택하여 AI 분석할 수 있습니다.")
        return
    
    # 선택 가능한 텍스트 영역
    st.markdown("### 📖 문서 내용 (텍스트 선택 가능)")
    
    # JavaScript로 텍스트 선택 감지 가능한 영역
    selectable_html = f"""
    <div class="selectable-text" id="document-content">
    {document_content.replace(chr(10), '<br>')}
    </div>
    
    <script>
    document.getElementById('document-content').addEventListener('mouseup', function() {{
        const selection = window.getSelection();
        const selectedText = selection.toString();
        
        if (selectedText && selectedText.trim().length > 0) {{
            // Streamlit 세션 상태 업데이트를 위한 커스텀 이벤트
            const event = new CustomEvent('textSelected', {{
                detail: {{
                    text: selectedText.trim()
                }}
            }});
            window.dispatchEvent(event);
            
            // 시각적 피드백
            console.log('선택된 텍스트:', selectedText.trim());
        }}
    }});
    </script>
    """
    
    components.html(selectable_html, height=200, scrolling=True)

def create_text_selection_input():
    """텍스트 선택을 위한 개선된 입력 방식"""
    
    st.markdown("### 🎯 분석할 텍스트 선택 방법")
    
    # 탭으로 선택 방법 구분
    tab1, tab2, tab3 = st.tabs(["✍️ 직접 입력", "📋 붙여넣기", "📖 문서에서 선택"])
    
    with tab1:
        st.markdown("**직접 텍스트를 입력하세요:**")
        manual_text = st.text_area(
            "분석할 텍스트:",
            value=st.session_state.get('selected_text', ''),
            height=100,
            placeholder="분석하고 싶은 텍스트를 직접 입력하세요...",
            key="manual_text_input"
        )
        
        if st.button("🎯 이 텍스트로 분석", key="use_manual_text"):
            if manual_text.strip():
                st.session_state.selected_text = manual_text.strip()
                st.success(f"✅ 선택된 텍스트: {manual_text[:50]}...")
                st.rerun()
    
    with tab2:
        st.markdown("**클립보드에서 붙여넣기:**")
        
        # 클립보드 버튼 (JavaScript 사용)
        clipboard_js = """
        <button onclick="pasteFromClipboard()" style="
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
        ">📋 클립보드에서 붙여넣기</button>
        
        <div id="clipboard-result" style="margin-top: 10px;"></div>
        
        <script>
        async function pasteFromClipboard() {
            try {
                const text = await navigator.clipboard.readText();
                if (text && text.trim()) {
                    document.getElementById('clipboard-result').innerHTML = 
                        '<div style="background: #e7f3ff; padding: 10px; border-radius: 5px; border: 1px solid #0066cc;">' +
                        '<strong>클립보드 내용:</strong><br>' + 
                        text.substring(0, 200) + (text.length > 200 ? '...' : '') +
                        '</div>';
                    
                    // Streamlit으로 데이터 전달
                    window.parent.postMessage({
                        type: 'clipboardText',
                        text: text.trim()
                    }, '*');
                } else {
                    document.getElementById('clipboard-result').innerHTML = 
                        '<div style="color: red;">클립보드가 비어있거나 텍스트가 없습니다.</div>';
                }
            } catch (err) {
                document.getElementById('clipboard-result').innerHTML = 
                    '<div style="color: red;">클립보드 접근 권한이 필요합니다.</div>';
            }
        }
        </script>
        """
        
        components.html(clipboard_js, height=100)
        
        # 수동 붙여넣기 대안
        st.markdown("**또는 Ctrl+V로 직접 붙여넣기:**")
        paste_text = st.text_area(
            "여기에 Ctrl+V로 붙여넣으세요:",
            height=80,
            placeholder="Ctrl+V (또는 Cmd+V)로 클립보드 내용을 붙여넣으세요...",
            key="paste_text_input"
        )
        
        if paste_text.strip():
            if st.button("🎯 붙여넣은 텍스트로 분석", key="use_paste_text"):
                st.session_state.selected_text = paste_text.strip()
                st.success(f"✅ 선택된 텍스트: {paste_text[:50]}...")
                st.rerun()
    
    with tab3:
        st.markdown("**문서에서 텍스트 선택:**")
        
        # 현재 문서 내용 표시 (선택 가능한 형태)
        document_content = st.session_state.get('document_content', '')
        if document_content:
            st.markdown("아래 문서에서 원하는 텍스트를 복사하세요:")
            
            # 읽기 전용 텍스트 영역 (복사 가능)
            st.code(document_content, language=None)
            
            st.info("💡 팁: 위 문서에서 원하는 부분을 드래그해서 선택한 후 복사(Ctrl+C)하고, '붙여넣기' 탭에서 사용하세요.")
        else:
            st.info("📝 문서에 내용이 없습니다. 먼저 문서를 작성해주세요.")
    
    # 현재 선택된 텍스트 표시
    if st.session_state.get('selected_text'):
        st.markdown("---")
        st.markdown("### 🎯 현재 선택된 텍스트")
        
        selected_text = st.session_state.selected_text
        preview_length = 200
        
        if len(selected_text) > preview_length:
            preview_text = selected_text[:preview_length] + "..."
            st.markdown(f"**미리보기:** {preview_text}")
            st.caption(f"전체 길이: {len(selected_text):,}자")
            
            with st.expander("📖 전체 텍스트 보기"):
                st.text(selected_text)
        else:
            st.markdown(f"**선택된 텍스트:** {selected_text}")
        
        # 선택 텍스트 클리어 버튼
        if st.button("🗑️ 선택 해제", key="clear_selected_text"):
            st.session_state.selected_text = ""
            st.rerun()