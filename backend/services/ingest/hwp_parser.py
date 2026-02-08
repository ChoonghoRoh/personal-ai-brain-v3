"""HWP/HWPX 파일 파서

Phase 9-4-1: HWP 파일 지원
- HWPX (HWP 5.0+): XML 기반, zipfile로 직접 파싱
- HWP (OLE): olefile을 활용한 바이너리 파싱
"""

import logging
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import re
import struct

logger = logging.getLogger(__name__)


@dataclass
class HWPParseResult:
    """HWP 파싱 결과"""
    text: str
    metadata: Dict[str, Any]
    sections: List[str]
    tables: List[List[List[str]]]
    success: bool
    error: Optional[str] = None
    file_type: str = "unknown"  # "hwpx" or "hwp"


class HWPXParser:
    """HWPX (HWP 5.0+, Open XML 형식) 파서"""

    # HWPX 내부 XML 네임스페이스
    NAMESPACES = {
        'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        'hc': 'http://www.hancom.co.kr/hwpml/2011/core',
        'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
        'config': 'urn:oasis:names:tc:opendocument:xmlns:config:1.0'
    }

    def parse(self, file_path: Path) -> HWPParseResult:
        """HWPX 파일 파싱"""
        try:
            if not zipfile.is_zipfile(file_path):
                return HWPParseResult(
                    text="",
                    metadata={},
                    sections=[],
                    tables=[],
                    success=False,
                    error="유효한 HWPX 파일이 아닙니다.",
                    file_type="hwpx"
                )

            text_parts = []
            sections = []
            tables = []
            metadata = {}

            with zipfile.ZipFile(file_path, 'r') as zf:
                # 메타데이터 추출
                metadata = self._extract_metadata(zf)

                # 섹션 파일 목록 찾기
                section_files = [
                    name for name in zf.namelist()
                    if name.startswith('Contents/') and name.endswith('.xml')
                    and 'section' in name.lower()
                ]

                # 섹션이 없으면 Contents 폴더의 모든 XML 검색
                if not section_files:
                    section_files = [
                        name for name in zf.namelist()
                        if name.startswith('Contents/') and name.endswith('.xml')
                    ]

                # 각 섹션 파싱
                for section_file in sorted(section_files):
                    try:
                        content = zf.read(section_file).decode('utf-8')
                        section_text, section_tables = self._parse_section_xml(content)
                        if section_text.strip():
                            sections.append(section_text)
                            text_parts.append(section_text)
                        tables.extend(section_tables)
                    except Exception as e:
                        logger.warning(f"섹션 파싱 실패 {section_file}: {e}")

            return HWPParseResult(
                text="\n\n".join(text_parts),
                metadata=metadata,
                sections=sections,
                tables=tables,
                success=True,
                file_type="hwpx"
            )

        except Exception as e:
            logger.error(f"HWPX 파싱 실패: {e}")
            return HWPParseResult(
                text="",
                metadata={},
                sections=[],
                tables=[],
                success=False,
                error=str(e),
                file_type="hwpx"
            )

    def _extract_metadata(self, zf: zipfile.ZipFile) -> Dict[str, Any]:
        """메타데이터 추출"""
        metadata = {}

        # META-INF/manifest.xml 또는 docInfo.xml에서 메타데이터 추출
        meta_files = ['META-INF/manifest.xml', 'docInfo.xml', 'Contents/header.xml']

        for meta_file in meta_files:
            if meta_file in zf.namelist():
                try:
                    content = zf.read(meta_file).decode('utf-8')
                    # 간단한 메타데이터 추출
                    if 'title' in content.lower():
                        metadata['has_title'] = True
                except Exception:
                    pass

        return metadata

    def _parse_section_xml(self, xml_content: str) -> tuple:
        """섹션 XML에서 텍스트와 테이블 추출"""
        text_parts = []
        tables = []

        try:
            # XML 파싱 (네임스페이스 제거 후 파싱)
            clean_xml = re.sub(r'xmlns[^"]*"[^"]*"', '', xml_content)
            root = ET.fromstring(clean_xml)

            # 모든 텍스트 노드 추출
            self._extract_text_recursive(root, text_parts)

            # 테이블 추출
            self._extract_tables_recursive(root, tables)

        except ET.ParseError as e:
            logger.warning(f"XML 파싱 에러: {e}")
            # 정규식으로 텍스트 추출 시도
            text_matches = re.findall(r'>([^<]+)<', xml_content)
            text_parts = [t.strip() for t in text_matches if t.strip() and len(t.strip()) > 1]

        return "\n".join(text_parts), tables

    def _extract_text_recursive(self, element: ET.Element, text_parts: List[str]):
        """재귀적으로 텍스트 추출"""
        # 텍스트 관련 태그들
        text_tags = ['t', 'text', 'p', 'run', 'char', 'lineseg']

        tag_name = element.tag.split('}')[-1].lower() if '}' in element.tag else element.tag.lower()

        # 현재 요소의 텍스트
        if element.text and element.text.strip():
            text_parts.append(element.text.strip())

        # 자식 요소 재귀 처리
        for child in element:
            self._extract_text_recursive(child, text_parts)

            # tail 텍스트 (태그 뒤의 텍스트)
            if child.tail and child.tail.strip():
                text_parts.append(child.tail.strip())

    def _extract_tables_recursive(self, element: ET.Element, tables: List[List[List[str]]]):
        """재귀적으로 테이블 추출"""
        tag_name = element.tag.split('}')[-1].lower() if '}' in element.tag else element.tag.lower()

        if tag_name in ['tbl', 'table']:
            table_data = self._parse_table(element)
            if table_data:
                tables.append(table_data)

        for child in element:
            self._extract_tables_recursive(child, tables)

    def _parse_table(self, table_element: ET.Element) -> List[List[str]]:
        """테이블 요소 파싱"""
        rows = []

        for row_elem in table_element.iter():
            tag_name = row_elem.tag.split('}')[-1].lower() if '}' in row_elem.tag else row_elem.tag.lower()

            if tag_name in ['tr', 'row']:
                cells = []
                for cell_elem in row_elem.iter():
                    cell_tag = cell_elem.tag.split('}')[-1].lower() if '}' in cell_elem.tag else cell_elem.tag.lower()
                    if cell_tag in ['tc', 'cell', 'td']:
                        cell_text = self._get_element_text(cell_elem)
                        cells.append(cell_text)

                if cells:
                    rows.append(cells)

        return rows

    def _get_element_text(self, element: ET.Element) -> str:
        """요소의 모든 텍스트 추출"""
        texts = []
        if element.text:
            texts.append(element.text)
        for child in element.iter():
            if child.text:
                texts.append(child.text)
            if child.tail:
                texts.append(child.tail)
        return " ".join(texts).strip()


class HWPParser:
    """HWP (OLE Compound Document 형식) 파서

    HWP 바이너리 형식은 복잡하므로 기본 텍스트 추출만 지원
    완전한 지원을 위해서는 외부 도구(hwp5txt 등) 사용 권장
    """

    # HWP 파일 시그니처
    HWP_SIGNATURE = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'

    def parse(self, file_path: Path) -> HWPParseResult:
        """HWP 파일 파싱"""
        try:
            # olefile 사용 시도
            try:
                import olefile
                return self._parse_with_olefile(file_path)
            except ImportError:
                logger.warning("olefile이 설치되지 않았습니다. 기본 파서를 사용합니다.")
                return self._parse_basic(file_path)

        except Exception as e:
            logger.error(f"HWP 파싱 실패: {e}")
            return HWPParseResult(
                text="",
                metadata={},
                sections=[],
                tables=[],
                success=False,
                error=str(e),
                file_type="hwp"
            )

    def _parse_with_olefile(self, file_path: Path) -> HWPParseResult:
        """olefile을 사용한 HWP 파싱"""
        import olefile

        if not olefile.isOleFile(file_path):
            return HWPParseResult(
                text="",
                metadata={},
                sections=[],
                tables=[],
                success=False,
                error="유효한 HWP(OLE) 파일이 아닙니다.",
                file_type="hwp"
            )

        text_parts = []
        metadata = {}

        with olefile.OleFileIO(file_path) as ole:
            # 스트림 목록 확인
            streams = ole.listdir()

            # 메타데이터 추출
            if ole.exists('DocInfo'):
                metadata['has_docinfo'] = True

            # 본문 텍스트 추출 시도
            # HWP의 본문은 'BodyText/Section0', 'BodyText/Section1' 등에 저장
            section_idx = 0
            while True:
                section_path = f'BodyText/Section{section_idx}'
                if ole.exists(section_path):
                    try:
                        section_data = ole.openstream(section_path).read()
                        section_text = self._extract_text_from_section(section_data)
                        if section_text:
                            text_parts.append(section_text)
                    except Exception as e:
                        logger.warning(f"섹션 {section_idx} 파싱 실패: {e}")
                    section_idx += 1
                else:
                    break

            # PrvText 스트림에서 미리보기 텍스트 추출 (fallback)
            if not text_parts and ole.exists('PrvText'):
                try:
                    prv_data = ole.openstream('PrvText').read()
                    prv_text = self._decode_prv_text(prv_data)
                    if prv_text:
                        text_parts.append(prv_text)
                except Exception as e:
                    logger.warning(f"PrvText 추출 실패: {e}")

        return HWPParseResult(
            text="\n\n".join(text_parts),
            metadata=metadata,
            sections=text_parts,
            tables=[],
            success=bool(text_parts),
            error=None if text_parts else "텍스트를 추출할 수 없습니다.",
            file_type="hwp"
        )

    def _extract_text_from_section(self, section_data: bytes) -> str:
        """섹션 데이터에서 텍스트 추출

        HWP 섹션 데이터는 압축되어 있을 수 있음
        """
        text_parts = []

        # 압축 해제 시도
        try:
            import zlib
            # HWP는 deflate 압축 사용 (처음 바이트 스킵)
            decompressed = zlib.decompress(section_data, -15)
            data = decompressed
        except Exception:
            data = section_data

        # 텍스트 추출 (UTF-16LE 또는 CP949)
        try:
            # UTF-16LE 시도
            text = self._extract_unicode_strings(data)
            if text:
                text_parts.append(text)
        except Exception:
            pass

        return "\n".join(text_parts)

    def _extract_unicode_strings(self, data: bytes) -> str:
        """바이너리 데이터에서 유니코드 문자열 추출"""
        text_parts = []

        # 연속된 유니코드 문자 찾기
        i = 0
        current_text = []

        while i < len(data) - 1:
            # 2바이트씩 읽어서 UTF-16LE로 해석
            try:
                char = data[i:i+2].decode('utf-16le')
                # 한글, 영문, 숫자, 공백, 구두점 등 출력 가능한 문자
                if char.isprintable() or char in '\n\r\t':
                    current_text.append(char)
                else:
                    if len(current_text) > 2:  # 최소 3자 이상
                        text_parts.append(''.join(current_text))
                    current_text = []
            except Exception:
                if len(current_text) > 2:
                    text_parts.append(''.join(current_text))
                current_text = []

            i += 2

        if len(current_text) > 2:
            text_parts.append(''.join(current_text))

        return ' '.join(text_parts)

    def _decode_prv_text(self, data: bytes) -> str:
        """PrvText 스트림 디코딩 (UTF-16LE)"""
        try:
            # BOM 제거 후 디코딩
            if data.startswith(b'\xff\xfe'):
                data = data[2:]
            return data.decode('utf-16le').strip('\x00')
        except Exception:
            return ""

    def _parse_basic(self, file_path: Path) -> HWPParseResult:
        """기본 파서 (olefile 없이)"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            # 파일 시그니처 확인
            if not data.startswith(self.HWP_SIGNATURE):
                return HWPParseResult(
                    text="",
                    metadata={},
                    sections=[],
                    tables=[],
                    success=False,
                    error="유효한 HWP 파일이 아닙니다.",
                    file_type="hwp"
                )

            # 기본 텍스트 추출 시도
            text = self._extract_unicode_strings(data)

            return HWPParseResult(
                text=text,
                metadata={},
                sections=[text] if text else [],
                tables=[],
                success=bool(text),
                error=None if text else "텍스트를 추출할 수 없습니다. olefile 설치를 권장합니다.",
                file_type="hwp"
            )

        except Exception as e:
            return HWPParseResult(
                text="",
                metadata={},
                sections=[],
                tables=[],
                success=False,
                error=str(e),
                file_type="hwp"
            )


class HWPFileParser:
    """통합 HWP 파서 (HWPX + HWP 모두 지원)"""

    def __init__(self):
        self.hwpx_parser = HWPXParser()
        self.hwp_parser = HWPParser()

    def parse(self, file_path: Path) -> HWPParseResult:
        """파일 확장자에 따라 적절한 파서 선택"""
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix == '.hwpx':
            return self.hwpx_parser.parse(file_path)
        elif suffix == '.hwp':
            # 먼저 HWPX 형식인지 확인 (일부 .hwp 파일이 실제로는 HWPX)
            if zipfile.is_zipfile(file_path):
                result = self.hwpx_parser.parse(file_path)
                if result.success:
                    return result

            # HWP (OLE) 형식으로 파싱
            return self.hwp_parser.parse(file_path)
        else:
            return HWPParseResult(
                text="",
                metadata={},
                sections=[],
                tables=[],
                success=False,
                error=f"지원하지 않는 확장자: {suffix}",
                file_type="unknown"
            )

    def extract_text(self, file_path: Path) -> Optional[str]:
        """텍스트만 추출"""
        result = self.parse(file_path)
        return result.text if result.success else None

    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """메타데이터 추출"""
        result = self.parse(file_path)
        return result.metadata


# 싱글톤 인스턴스
_hwp_parser_instance: Optional[HWPFileParser] = None


def get_hwp_parser() -> HWPFileParser:
    """HWP 파서 인스턴스 가져오기"""
    global _hwp_parser_instance
    if _hwp_parser_instance is None:
        _hwp_parser_instance = HWPFileParser()
    return _hwp_parser_instance


def parse_hwp_file(file_path: Path) -> Optional[str]:
    """HWP 파일에서 텍스트 추출 (편의 함수)"""
    parser = get_hwp_parser()
    return parser.extract_text(file_path)
