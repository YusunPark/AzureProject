# Azure Storage 구조 및 경로 정보

## 📂 스토리지 경로 구조

### 컨테이너 구조
```
documents/  (컨테이너 이름)
├── training/     (사내 학습 문서)
│   ├── 2025/
│   │   ├── 01/
│   │   │   ├── uuid1.txt
│   │   │   ├── uuid2.docx
│   │   │   └── uuid3.pdf
│   │   ├── 02/
│   │   └── ...
├── generated/    (생성된 문서) 
│   ├── 2025/
│   │   ├── 01/
│   │   │   ├── uuid4.txt
│   │   │   ├── uuid5.txt
│   │   │   └── uuid6.txt
│   │   ├── 02/
│   │   └── ...
```

### 파일 경로 패턴
- **사내 문서**: `training/{year}/{month}/{file_id}{extension}`
- **생성 문서**: `generated/{year}/{month}/{file_id}{extension}`

### 예시 경로
- 사내 문서: `training/2025/01/12345678-1234-5678-9012-123456789abc.txt`
- 생성 문서: `generated/2025/01/87654321-4321-8765-2109-987654321def.txt`

### 메타데이터 구조
각 Blob에는 다음 메타데이터가 저장됩니다:
- `original_filename`: 원본 파일명
- `document_type`: 문서 유형 (training/generated)
- `upload_date`: 업로드 날짜 (ISO 형식)
- `file_id`: 고유 파일 ID
- `file_size`: 파일 크기 (바이트)
- `meta_*`: 사용자 정의 메타데이터 (접두어 'meta_' 추가)

### 저장 시점
1. **사내 문서 학습**: 문서 업로드 시 `training/` 폴더에 저장
2. **AI 생성 문서**: 편집기에서 '저장' 버튼 클릭 시 `generated/` 폴더에 저장

### 파일명 처리
- 원본 파일명은 메타데이터에 보존
- Blob 이름은 UUID로 생성 (중복 방지)
- 한글 파일명은 ASCII로 안전하게 변환 후 메타데이터 저장