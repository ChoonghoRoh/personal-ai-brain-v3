#!/usr/bin/env python3
"""
Phase 7.9.9: 메뉴별 코드 리뷰 스크립트
- 메뉴별로 리뷰 실행
- 취약점, 개선점, 코드 길이, 공통모듈 분리 부분 검토
- frontend 리팩토링 부분
- backend 리팩토링 부분
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 메뉴 구조 정의
MENU_STRUCTURE = {
    "사용자 메뉴": {
        "dashboard": {
            "route": "/dashboard",
            "frontend": {
                "html": "web/src/pages/dashboard.html",
                "js": "web/public/js/dashboard.js",
                "css": "web/public/css/dashboard.css"
            },
            "backend": {
                "router": "backend/routers/system.py"
            }
        },
        "search": {
            "route": "/search",
            "frontend": {
                "html": "web/src/pages/search.html",
                "js": "web/public/js/search.js",
                "css": "web/public/css/search.css"
            },
            "backend": {
                "router": "backend/routers/search.py"
            }
        },
        "knowledge": {
            "route": "/knowledge",
            "frontend": {
                "html": "web/src/pages/knowledge.html",
                "js": "web/public/js/knowledge.js",
                "css": "web/public/css/knowledge.css"
            },
            "backend": {
                "router": "backend/routers/knowledge.py"
            }
        },
        "reason": {
            "route": "/reason",
            "frontend": {
                "html": "web/src/pages/reason.html",
                "js": "web/public/js/reason.js",
                "css": "web/public/css/reason.css"
            },
            "backend": {
                "router": "backend/routers/reason.py"
            }
        },
        "ask": {
            "route": "/ask",
            "frontend": {
                "html": "web/src/pages/ask.html",
                "js": "web/public/js/ask.js",
                "css": "web/public/css/ask.css"
            },
            "backend": {
                "router": "backend/routers/ai.py"
            }
        },
        "logs": {
            "route": "/logs",
            "frontend": {
                "html": "web/src/pages/logs.html",
                "js": "web/public/js/logs.js",
                "css": "web/public/css/logs.css"
            },
            "backend": {
                "router": "backend/routers/logs.py"
            }
        }
    },
    "관리자 메뉴": {
        "admin_labels": {
            "route": "/admin/labels",
            "frontend": {
                "html": "web/src/pages/admin/labels.html",
                "js": "web/public/js/admin-labels.js",
                "css": "web/public/css/admin-labels.css"
            },
            "backend": {
                "router": "backend/routers/labels.py"
            }
        },
        "admin_groups": {
            "route": "/admin/groups",
            "frontend": {
                "html": "web/src/pages/admin/groups.html",
                "js": "web/public/js/admin-groups.js",
                "css": "web/public/css/admin-groups.css"
            },
            "backend": {
                "router": "backend/routers/suggestions.py"
            }
        },
        "admin_approval": {
            "route": "/admin/approval",
            "frontend": {
                "html": "web/src/pages/admin/approval.html",
                "js": "web/public/js/admin-approval.js",
                "css": "web/public/css/admin-approval.css"
            },
            "backend": {
                "router": "backend/routers/approval.py"
            }
        }
    }
}

# 공통 모듈 정의
COMMON_MODULES = {
    "frontend": [
        "web/public/js/layout-component.js",
        "web/public/js/header-component.js",
        "web/public/js/document-utils.js",
        "web/public/js/text-formatter.js",
        "web/public/js/utils.js",
        "web/public/js/admin-common.js",
        "web/public/js/pagination-component.js"
    ],
    "backend": [
        "backend/models/models.py",
        "backend/models/database.py",
        "backend/config.py"
    ]
}


class CodeReviewer:
    """코드 리뷰 클래스"""
    
    def __init__(self):
        self.results = {}
        
    def analyze_file(self, file_path: Path) -> Dict:
        """파일 분석"""
        if not file_path.exists():
            return {"error": "파일 없음"}
        
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        stats = {
            "file_path": str(file_path.relative_to(PROJECT_ROOT)),
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('//')]),
            "file_size_kb": round(file_path.stat().st_size / 1024, 2),
            "vulnerabilities": [],
            "improvements": [],
            "long_functions": [],
            "duplicate_code": [],
            "complexity": 0
        }
        
        # 취약점 검사
        stats["vulnerabilities"] = self.check_vulnerabilities(content, file_path)
        
        # 개선점 검사
        stats["improvements"] = self.check_improvements(content, file_path)
        
        # 긴 함수 검사
        stats["long_functions"] = self.check_long_functions(content, file_path)
        
        # 중복 코드 검사
        stats["duplicate_code"] = self.check_duplicate_code(content, file_path)
        
        # 복잡도 계산
        stats["complexity"] = self.calculate_complexity(content, file_path)
        
        return stats
    
    def check_vulnerabilities(self, content: str, file_path: Path) -> List[Dict]:
        """취약점 검사"""
        vulnerabilities = []
        ext = file_path.suffix.lower()
        
        # XSS 취약점 (JavaScript/HTML)
        if ext in ['.js', '.html']:
            # innerHTML 직접 사용
            if re.search(r'\.innerHTML\s*=', content):
                vulnerabilities.append({
                    "type": "XSS",
                    "severity": "high",
                    "description": "innerHTML 직접 사용 - XSS 취약점 가능",
                    "recommendation": "textContent 또는 DOMPurify 사용"
                })
            
            # eval 사용
            if re.search(r'\beval\s*\(', content):
                vulnerabilities.append({
                    "type": "Code Injection",
                    "severity": "critical",
                    "description": "eval() 사용 - 코드 주입 취약점",
                    "recommendation": "eval() 사용 금지"
                })
            
            # document.write 사용
            if re.search(r'document\.write\s*\(', content):
                vulnerabilities.append({
                    "type": "XSS",
                    "severity": "medium",
                    "description": "document.write() 사용 - XSS 취약점 가능",
                    "recommendation": "DOM 조작 메서드 사용"
                })
        
        # SQL Injection (Python)
        if ext == '.py':
            # 문자열 연결로 SQL 구성
            if re.search(r'["\'].*\+.*%(.*%)', content) or re.search(r'["\'].*\+.*\{.*\}', content):
                if 'SELECT' in content or 'INSERT' in content or 'UPDATE' in content:
                    vulnerabilities.append({
                        "type": "SQL Injection",
                        "severity": "high",
                        "description": "문자열 연결로 SQL 구성 - SQL Injection 취약점",
                        "recommendation": "파라미터화된 쿼리 사용"
                    })
        
        # 하드코딩된 비밀번호/키
        if re.search(r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
            vulnerabilities.append({
                "type": "Security",
                "severity": "critical",
                "description": "하드코딩된 비밀번호/키 발견",
                "recommendation": "환경 변수 또는 설정 파일 사용"
            })
        
        return vulnerabilities
    
    def check_improvements(self, content: str, file_path: Path) -> List[Dict]:
        """개선점 검사"""
        improvements = []
        ext = file_path.suffix.lower()
        
        # 긴 파일
        lines = content.split('\n')
        if len(lines) > 1000:
            improvements.append({
                "type": "Code Length",
                "priority": "high",
                "description": f"파일이 너무 깁니다 ({len(lines)}줄)",
                "recommendation": "모듈 분리 고려"
            })
        
        # 주석 부족
        comment_ratio = len([l for l in lines if l.strip().startswith('#') or l.strip().startswith('//')]) / max(len(lines), 1)
        if comment_ratio < 0.1 and len(lines) > 100:
            improvements.append({
                "type": "Documentation",
                "priority": "medium",
                "description": "주석이 부족합니다",
                "recommendation": "함수 및 복잡한 로직에 주석 추가"
            })
        
        # 중첩 깊이
        max_nesting = self.get_max_nesting(content)
        if max_nesting > 4:
            improvements.append({
                "type": "Complexity",
                "priority": "medium",
                "description": f"중첩 깊이가 깊습니다 (최대 {max_nesting}단계)",
                "recommendation": "함수 분리로 복잡도 감소"
            })
        
        # 매직 넘버
        if ext == '.js':
            magic_numbers = re.findall(r'\b\d{3,}\b', content)
            if len(magic_numbers) > 5:
                improvements.append({
                    "type": "Code Quality",
                    "priority": "low",
                    "description": "매직 넘버가 많습니다",
                    "recommendation": "상수로 정의"
                })
        
        # 에러 처리 부족
        if ext == '.js':
            async_functions = len(re.findall(r'async\s+function|async\s+\(', content))
            try_catch = len(re.findall(r'try\s*\{', content))
            if async_functions > 0 and try_catch < async_functions * 0.5:
                improvements.append({
                    "type": "Error Handling",
                    "priority": "medium",
                    "description": "비동기 함수의 에러 처리가 부족합니다",
                    "recommendation": "try-catch 또는 .catch() 추가"
                })
        
        return improvements
    
    def check_long_functions(self, content: str, file_path: Path) -> List[Dict]:
        """긴 함수 검사"""
        long_functions = []
        ext = file_path.suffix.lower()
        
        if ext == '.js':
            # JavaScript 함수
            function_pattern = r'(function\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?\([^)]*\)\s*=>|async\s+function\s+\w+)'
            functions = list(re.finditer(function_pattern, content))
            
            for i, func_match in enumerate(functions):
                start = func_match.start()
                end = functions[i + 1].start() if i + 1 < len(functions) else len(content)
                func_content = content[start:end]
                func_lines = func_content.count('\n')
                
                if func_lines > 50:
                    func_name = func_match.group(1) if func_match.group(1) else "익명 함수"
                    long_functions.append({
                        "name": func_name[:50],
                        "lines": func_lines,
                        "recommendation": "함수를 더 작은 단위로 분리"
                    })
        
        elif ext == '.py':
            # Python 함수
            function_pattern = r'def\s+(\w+)\s*\('
            functions = list(re.finditer(function_pattern, content))
            
            for i, func_match in enumerate(functions):
                start = func_match.start()
                end = functions[i + 1].start() if i + 1 < len(functions) else len(content)
                func_content = content[start:end]
                func_lines = func_content.count('\n')
                
                if func_lines > 100:
                    func_name = func_match.group(1)
                    long_functions.append({
                        "name": func_name,
                        "lines": func_lines,
                        "recommendation": "함수를 더 작은 단위로 분리"
                    })
        
        return long_functions
    
    def check_duplicate_code(self, content: str, file_path: Path) -> List[Dict]:
        """중복 코드 검사 (간단한 버전)"""
        duplicates = []
        lines = content.split('\n')
        
        # 동일한 라인 블록 찾기 (5줄 이상)
        for i in range(len(lines) - 5):
            block = '\n'.join(lines[i:i+5])
            if block.strip():
                # 다른 위치에서 동일한 블록 찾기
                for j in range(i + 5, len(lines) - 5):
                    other_block = '\n'.join(lines[j:j+5])
                    if block == other_block:
                        duplicates.append({
                            "lines": f"{i+1}-{i+5}",
                            "duplicate_at": f"{j+1}-{j+5}",
                            "recommendation": "공통 함수로 추출"
                        })
                        break
        
        return duplicates[:5]  # 최대 5개만 반환
    
    def calculate_complexity(self, content: str, file_path: Path) -> int:
        """복잡도 계산 (간단한 버전)"""
        complexity = 0
        ext = file_path.suffix.lower()
        
        # 조건문
        complexity += len(re.findall(r'\bif\s*\(', content))
        complexity += len(re.findall(r'\belse\s+if\s*\(', content))
        complexity += len(re.findall(r'\bswitch\s*\(', content))
        complexity += len(re.findall(r'\bcase\s+', content))
        
        # 반복문
        complexity += len(re.findall(r'\bfor\s*\(', content))
        complexity += len(re.findall(r'\bwhile\s*\(', content))
        complexity += len(re.findall(r'\bdo\s*\{', content))
        
        # 예외 처리
        complexity += len(re.findall(r'\btry\s*\{', content))
        complexity += len(re.findall(r'\bcatch\s*\(', content))
        
        return complexity
    
    def get_max_nesting(self, content: str) -> int:
        """최대 중첩 깊이 계산"""
        max_depth = 0
        current_depth = 0
        
        for char in content:
            if char in ['{', '(', '[']:
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ['}', ')', ']']:
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def check_common_module_usage(self, file_path: Path, common_modules: List[str]) -> Dict:
        """공통 모듈 사용 여부 확인"""
        if not file_path.exists():
            return {"error": "파일 없음"}
        
        content = file_path.read_text(encoding='utf-8')
        ext = file_path.suffix.lower()
        
        usage = {
            "uses_common_modules": [],
            "potential_extractions": [],
            "duplicate_functions": []
        }
        
        # 공통 모듈 import 확인
        for module in common_modules:
            module_name = Path(module).stem
            if ext == '.js':
                if f'{module_name}' in content or module_name.replace('-', '_') in content:
                    usage["uses_common_modules"].append(module)
            elif ext == '.py':
                if module_name in content:
                    usage["uses_common_modules"].append(module)
        
        return usage
    
    def review_menu(self, menu_name: str, menu_config: Dict) -> Dict:
        """메뉴별 리뷰"""
        print(f"\n{'='*80}")
        print(f"📋 메뉴 리뷰: {menu_name} ({menu_config.get('route', 'N/A')})")
        print(f"{'='*80}")
        
        review_result = {
            "menu_name": menu_name,
            "route": menu_config.get("route", ""),
            "frontend": {},
            "backend": {},
            "common_modules": {},
            "summary": {}
        }
        
        # Frontend 리뷰
        if "frontend" in menu_config:
            print(f"\n🔍 Frontend 리뷰")
            print("-" * 80)
            frontend_result = {}
            
            for file_type, file_path in menu_config["frontend"].items():
                full_path = PROJECT_ROOT / file_path
                print(f"\n  📄 {file_type.upper()}: {file_path}")
                
                if full_path.exists():
                    stats = self.analyze_file(full_path)
                    frontend_result[file_type] = stats
                    
                    print(f"    - 총 라인: {stats['total_lines']}")
                    print(f"    - 코드 라인: {stats['code_lines']}")
                    print(f"    - 파일 크기: {stats['file_size_kb']} KB")
                    print(f"    - 복잡도: {stats['complexity']}")
                    
                    if stats['vulnerabilities']:
                        print(f"    ⚠️  취약점: {len(stats['vulnerabilities'])}개")
                        for vuln in stats['vulnerabilities']:
                            print(f"      - [{vuln['severity']}] {vuln['type']}: {vuln['description']}")
                    
                    if stats['improvements']:
                        print(f"    💡 개선점: {len(stats['improvements'])}개")
                        for imp in stats['improvements'][:3]:  # 최대 3개만 표시
                            print(f"      - [{imp['priority']}] {imp['type']}: {imp['description']}")
                    
                    if stats['long_functions']:
                        print(f"    📏 긴 함수: {len(stats['long_functions'])}개")
                        for func in stats['long_functions'][:3]:  # 최대 3개만 표시
                            print(f"      - {func['name']}: {func['lines']}줄")
                else:
                    print(f"    ❌ 파일 없음")
                    frontend_result[file_type] = {"error": "파일 없음"}
            
            review_result["frontend"] = frontend_result
            
            # 공통 모듈 사용 확인
            js_file = menu_config["frontend"].get("js")
            if js_file:
                js_path = PROJECT_ROOT / js_file
                common_usage = self.check_common_module_usage(js_path, COMMON_MODULES["frontend"])
                review_result["common_modules"]["frontend"] = common_usage
                
                if common_usage.get("uses_common_modules"):
                    print(f"\n  ✅ 공통 모듈 사용: {len(common_usage['uses_common_modules'])}개")
                else:
                    print(f"\n  ⚠️  공통 모듈 미사용 - 리팩토링 고려")
        
        # Backend 리뷰
        if "backend" in menu_config:
            print(f"\n🔍 Backend 리뷰")
            print("-" * 80)
            backend_result = {}
            
            router_file = menu_config["backend"].get("router")
            if router_file:
                full_path = PROJECT_ROOT / router_file
                print(f"\n  📄 Router: {router_file}")
                
                if full_path.exists():
                    stats = self.analyze_file(full_path)
                    backend_result["router"] = stats
                    
                    print(f"    - 총 라인: {stats['total_lines']}")
                    print(f"    - 코드 라인: {stats['code_lines']}")
                    print(f"    - 파일 크기: {stats['file_size_kb']} KB")
                    print(f"    - 복잡도: {stats['complexity']}")
                    
                    if stats['vulnerabilities']:
                        print(f"    ⚠️  취약점: {len(stats['vulnerabilities'])}개")
                        for vuln in stats['vulnerabilities']:
                            print(f"      - [{vuln['severity']}] {vuln['type']}: {vuln['description']}")
                    
                    if stats['improvements']:
                        print(f"    💡 개선점: {len(stats['improvements'])}개")
                        for imp in stats['improvements'][:3]:
                            print(f"      - [{imp['priority']}] {imp['type']}: {imp['description']}")
                    
                    if stats['long_functions']:
                        print(f"    📏 긴 함수: {len(stats['long_functions'])}개")
                        for func in stats['long_functions'][:3]:
                            print(f"      - {func['name']}: {func['lines']}줄")
                else:
                    print(f"    ❌ 파일 없음")
                    backend_result["router"] = {"error": "파일 없음"}
            
            review_result["backend"] = backend_result
        
        # 요약
        total_vulns = sum(
            len(r.get('vulnerabilities', []))
            for r in review_result.get("frontend", {}).values()
            if isinstance(r, dict) and 'vulnerabilities' in r
        ) + sum(
            len(r.get('vulnerabilities', []))
            for r in review_result.get("backend", {}).values()
            if isinstance(r, dict) and 'vulnerabilities' in r
        )
        
        total_improvements = sum(
            len(r.get('improvements', []))
            for r in review_result.get("frontend", {}).values()
            if isinstance(r, dict) and 'improvements' in r
        ) + sum(
            len(r.get('improvements', []))
            for r in review_result.get("backend", {}).values()
            if isinstance(r, dict) and 'improvements' in r
        )
        
        review_result["summary"] = {
            "total_vulnerabilities": total_vulns,
            "total_improvements": total_improvements,
            "frontend_files": len([f for f in review_result.get("frontend", {}).values() if isinstance(f, dict) and "error" not in f]),
            "backend_files": len([f for f in review_result.get("backend", {}).values() if isinstance(f, dict) and "error" not in f])
        }
        
        print(f"\n📊 요약:")
        print(f"  - 취약점: {total_vulns}개")
        print(f"  - 개선점: {total_improvements}개")
        
        return review_result
    
    def generate_report(self, all_results: Dict) -> str:
        """리뷰 보고서 생성"""
        report_lines = []
        report_lines.append("# Phase 7.9.9: 메뉴별 코드 리뷰 보고서\n")
        report_lines.append(f"**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")
        
        # 전체 요약
        total_vulns = sum(
            menu.get("summary", {}).get("total_vulnerabilities", 0)
            for category in all_results.values()
            for menu in category.values()
        )
        total_improvements = sum(
            menu.get("summary", {}).get("total_improvements", 0)
            for category in all_results.values()
            for menu in category.values()
        )
        
        report_lines.append("## 📊 전체 요약\n")
        report_lines.append(f"- **총 취약점**: {total_vulns}개\n")
        report_lines.append(f"- **총 개선점**: {total_improvements}개\n")
        report_lines.append("---\n")
        
        # 메뉴별 상세
        for category_name, menus in all_results.items():
            report_lines.append(f"\n## {category_name}\n")
            
            for menu_name, menu_result in menus.items():
                route = menu_result.get("route", "")
                summary = menu_result.get("summary", {})
                
                report_lines.append(f"\n### {menu_name} ({route})\n")
                report_lines.append(f"- 취약점: {summary.get('total_vulnerabilities', 0)}개\n")
                report_lines.append(f"- 개선점: {summary.get('total_improvements', 0)}개\n")
                
                # Frontend
                if menu_result.get("frontend"):
                    report_lines.append("\n#### Frontend\n")
                    for file_type, file_data in menu_result["frontend"].items():
                        if isinstance(file_data, dict) and "error" not in file_data:
                            report_lines.append(f"- **{file_type}**: {file_data.get('total_lines', 0)}줄, {file_data.get('file_size_kb', 0)} KB\n")
                            if file_data.get('vulnerabilities'):
                                report_lines.append("  - 취약점:\n")
                                for vuln in file_data['vulnerabilities']:
                                    report_lines.append(f"    - [{vuln['severity']}] {vuln['type']}: {vuln['description']}\n")
                            if file_data.get('long_functions'):
                                report_lines.append(f"  - 긴 함수: {len(file_data['long_functions'])}개\n")
                
                # Backend
                if menu_result.get("backend"):
                    report_lines.append("\n#### Backend\n")
                    for file_type, file_data in menu_result["backend"].items():
                        if isinstance(file_data, dict) and "error" not in file_data:
                            report_lines.append(f"- **{file_type}**: {file_data.get('total_lines', 0)}줄, {file_data.get('file_size_kb', 0)} KB\n")
                            if file_data.get('vulnerabilities'):
                                report_lines.append("  - 취약점:\n")
                                for vuln in file_data['vulnerabilities']:
                                    report_lines.append(f"    - [{vuln['severity']}] {vuln['type']}: {vuln['description']}\n")
                            if file_data.get('long_functions'):
                                report_lines.append(f"  - 긴 함수: {len(file_data['long_functions'])}개\n")
        
        return "".join(report_lines)


def main():
    """메인 함수"""
    print("="*80)
    print("Phase 7.9.9: 메뉴별 코드 리뷰")
    print("="*80)
    
    reviewer = CodeReviewer()
    all_results = {}
    
    # 각 메뉴별로 리뷰 실행
    for category_name, menus in MENU_STRUCTURE.items():
        all_results[category_name] = {}
        
        for menu_name, menu_config in menus.items():
            result = reviewer.review_menu(menu_name, menu_config)
            all_results[category_name][menu_name] = result
    
    # 보고서 생성
    print(f"\n{'='*80}")
    print("📝 보고서 생성 중...")
    print(f"{'='*80}")
    
    report = reviewer.generate_report(all_results)
    
    # 보고서 저장
    report_path = PROJECT_ROOT / "docs" / "dev" / "phase7-9-9-review-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    
    print(f"\n✅ 보고서 저장 완료: {report_path.relative_to(PROJECT_ROOT)}")
    
    # JSON 결과도 저장
    json_path = PROJECT_ROOT / "docs" / "dev" / "phase7-9-9-review-results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON 결과 저장 완료: {json_path.relative_to(PROJECT_ROOT)}")
    
    # 전체 통계 출력
    print(f"\n{'='*80}")
    print("📊 전체 통계")
    print(f"{'='*80}")
    
    total_vulns = sum(
        menu.get("summary", {}).get("total_vulnerabilities", 0)
        for category in all_results.values()
        for menu in category.values()
    )
    total_improvements = sum(
        menu.get("summary", {}).get("total_improvements", 0)
        for category in all_results.values()
        for menu in category.values()
    )
    
    print(f"총 취약점: {total_vulns}개")
    print(f"총 개선점: {total_improvements}개")
    print(f"리뷰 완료 메뉴: {sum(len(menus) for menus in all_results.values())}개")


if __name__ == "__main__":
    main()
