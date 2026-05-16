#!/usr/bin/env python3
"""
TRIZ Contradiction Matrix Solver
단일 모순 쌍(개선 변수, 악화 변수)을 입력받아 추천 발명 원리 번호를 반환합니다.

사용법:
  python3 triz_matrix_solver.py --improving 14 --worsening 1
  python3 triz_matrix_solver.py --improving "강도" --worsening "속도"
  python3 triz_matrix_solver.py --improving 9 --worsening 36 --matrix_file /path/to/matrix_data.json
"""

import json
import argparse
import os
import sys


# 자연어 → 번호 매핑 딕셔너리
PARAMETER_MAP = {
    # 한국어
    "이동 물체의 무게": "1", "이동물체의무게": "1", "무게(이동)": "1",
    "정지 물체의 무게": "2", "정지물체의무게": "2", "무게(정지)": "2",
    "이동 물체의 길이": "3", "길이(이동)": "3",
    "정지 물체의 길이": "4", "길이(정지)": "4",
    "이동 물체의 면적": "5", "면적(이동)": "5",
    "정지 물체의 면적": "6", "면적(정지)": "6",
    "이동 물체의 부피": "7", "부피(이동)": "7",
    "정지 물체의 부피": "8", "부피(정지)": "8",
    "속도": "9",
    "힘": "10",
    "응력": "11", "압력": "11", "응력또는압력": "11",
    "형상": "12",
    "구조 안정성": "13", "안정성": "13", "구조안정성": "13",
    "강도": "14",
    "이동 물체의 작동 지속 시간": "15", "지속 시간(이동)": "15",
    "정지 물체의 작동 지속 시간": "16", "지속 시간(정지)": "16",
    "온도": "17",
    "조명 강도": "18", "조명": "18",
    "이동 물체의 에너지 소비": "19", "에너지 소비(이동)": "19",
    "정지 물체의 에너지 소비": "20", "에너지 소비(정지)": "20",
    "동력": "21",
    "에너지 손실": "22",
    "물질 손실": "23",
    "정보 손실": "24",
    "시간 손실": "25",
    "물질의 양": "26",
    "신뢰성": "27",
    "측정 정확도": "28", "측정정확도": "28",
    "제조 정밀도": "29",
    "물체에 작용하는 유해 효과": "30", "유해 효과": "30",
    "해로운 부작용": "31", "부작용": "31",
    "제조 용이성": "32",
    "작동 편의성": "33",
    "수리 편의성": "34",
    "적응성": "35", "다양성": "35",
    "장치 복잡성": "36", "복잡성": "36",
    "제어 및 측정의 어려움": "37",
    "자동화 정도": "38", "자동화": "38",
    "생산성": "39",
    # 영어
    "weight of moving object": "1",
    "weight of stationary object": "2",
    "length of moving object": "3",
    "length of stationary object": "4",
    "area of moving object": "5",
    "area of stationary object": "6",
    "volume of moving object": "7",
    "volume of stationary object": "8",
    "speed": "9",
    "force": "10",
    "stress": "11", "pressure": "11", "stress or pressure": "11",
    "shape": "12",
    "stability": "13", "stability of the object's composition": "13",
    "strength": "14",
    "duration of action by a moving object": "15",
    "duration of action by a stationary object": "16",
    "temperature": "17",
    "illumination intensity": "18", "illumination": "18",
    "use of energy by moving object": "19",
    "use of energy by stationary object": "20",
    "power": "21",
    "loss of energy": "22", "energy loss": "22",
    "loss of substance": "23",
    "loss of information": "24",
    "loss of time": "25",
    "quantity of substance": "26",
    "reliability": "27",
    "measurement accuracy": "28",
    "manufacturing precision": "29",
    "object-generated harmful side effects": "30",
    "harmful side effects": "31",
    "ease of manufacture": "32",
    "ease of operation": "33",
    "ease of repair": "34",
    "adaptability": "35", "versatility": "35",
    "device complexity": "36", "complexity": "36",
    "difficulty of detecting and measuring": "37",
    "extent of automation": "38", "automation": "38",
    "productivity": "39",
}


def load_matrix_data(filepath: str) -> dict:
    """외부 JSON 파일에서 모순 행렬 데이터를 로드합니다."""
    # 빈 경로인 경우 스크립트 기준 기본 경로 사용
    if not filepath:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, "..", "references", "matrix_data.json")
    elif not os.path.isabs(filepath):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filepath)

    filepath = os.path.normpath(filepath)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # _comment 키 제거
            data.pop("_comment", None)
            return data
    except FileNotFoundError:
        print(json.dumps({
            "error": f"파일을 찾을 수 없습니다: {filepath}",
            "status": "error_file_not_found"
        }, ensure_ascii=False), file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": f"JSON 파싱 오류: {str(e)}",
            "status": "error_invalid_json"
        }, ensure_ascii=False), file=sys.stderr)
        return {}


def normalize_parameter(param: str) -> str:
    """
    파라미터 입력값을 정규화하여 변수 번호(문자열)로 반환합니다.
    숫자 입력은 그대로, 자연어 입력은 매핑 딕셔너리로 변환합니다.
    """
    param = param.strip()

    # 이미 숫자인 경우
    if param.isdigit():
        return param

    # 소문자 정규화 후 매핑 시도
    normalized = param.lower().strip()
    if normalized in PARAMETER_MAP:
        return PARAMETER_MAP[normalized]

    # 원본 그대로도 시도
    if param in PARAMETER_MAP:
        return PARAMETER_MAP[param]

    # 부분 일치 시도 (변수명이 일부 포함된 경우)
    for key, val in PARAMETER_MAP.items():
        if normalized in key.lower() or key.lower() in normalized:
            return val

    # 매핑 실패 시 원본 반환 (에러는 solve에서 처리)
    return param


def solve(improving: str, worsening: str, matrix_data: dict) -> dict:
    """
    개선 변수와 악화 변수를 입력받아 해결 원리 번호 리스트를 반환합니다.

    Returns:
        dict: {
            "principles": ["1", "8", "15"],  # 발명 원리 번호
            "improving_param": "#14",
            "worsening_param": "#1",
            "status": "success"
        }
    """
    imp_key = normalize_parameter(improving)
    wor_key = normalize_parameter(worsening)

    # 유효 범위 검사 (1-39)
    try:
        imp_num = int(imp_key)
        wor_num = int(wor_key)
        if not (1 <= imp_num <= 39):
            return {
                "error": f"개선 변수 번호가 범위를 벗어났습니다: {imp_key} (유효 범위: 1-39)",
                "status": "error_out_of_range"
            }
        if not (1 <= wor_num <= 39):
            return {
                "error": f"악화 변수 번호가 범위를 벗어났습니다: {wor_key} (유효 범위: 1-39)",
                "status": "error_out_of_range"
            }
    except ValueError:
        # 숫자 변환 실패 = 자연어 매핑도 실패한 경우
        suggestions = []
        query = improving.lower()
        for key in PARAMETER_MAP:
            if any(word in key.lower() for word in query.split()):
                suggestions.append(f"'{key}' → #{PARAMETER_MAP[key]}")
        hint = f" 유사 변수: {', '.join(suggestions[:3])}" if suggestions else ""
        return {
            "error": f"인식할 수 없는 변수명: improving='{improving}', worsening='{worsening}'.{hint} 번호(1-39) 또는 정확한 변수명을 사용하세요.",
            "status": "error_unknown_parameter"
        }

    # 동일 변수 예외
    if imp_key == wor_key:
        return {
            "error": f"개선 변수와 악화 변수가 동일합니다 (#{imp_key}). 서로 다른 변수를 선택하세요.",
            "status": "error_same_variable"
        }

    # 정방향 행렬 조회
    principles = matrix_data.get(imp_key, {}).get(wor_key)

    if principles:
        filtered = [p for p in principles if p]
        return {
            "principles": filtered,
            "improving_param": f"#{imp_key}",
            "worsening_param": f"#{wor_key}",
            "status": "success",
            "count": len(filtered)
        }

    # 역방향 조회 시도 (행렬은 비대칭이지만 참고 가능)
    reverse = matrix_data.get(wor_key, {}).get(imp_key)
    if reverse:
        filtered = [p for p in reverse if p]
        return {
            "principles": filtered,
            "improving_param": f"#{imp_key}",
            "worsening_param": f"#{wor_key}",
            "status": "success_reverse_lookup",
            "note": "역방향 조회 결과입니다. 정확도를 위해 결과를 검토하세요.",
            "count": len(filtered)
        }

    return {
        "error": (
            f"변수 #{imp_key}(개선)와 #{wor_key}(악화) 조합에 대한 행렬 데이터가 없습니다. "
            f"인접 변수 번호(±1~2)로 재시도하거나 AI 추론을 활용하세요."
        ),
        "status": "no_matrix_intersection",
        "improving_param": f"#{imp_key}",
        "worsening_param": f"#{wor_key}"
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TRIZ Contradiction Matrix Solver - 모순 쌍으로부터 발명 원리를 도출합니다",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--improving", type=str, required=True,
        help="개선하려는 변수 번호(1-39) 또는 변수명 (예: 14, '강도', 'strength')"
    )
    parser.add_argument(
        "--worsening", type=str, required=True,
        help="악화되는 변수 번호(1-39) 또는 변수명 (예: 1, '이동 물체의 무게', 'speed')"
    )
    parser.add_argument(
        "--matrix_file", type=str, default="",
        help="모순 행렬 JSON 파일 경로 (기본: 스크립트 기준 ../references/matrix_data.json)"
    )

    args = parser.parse_args()

    matrix = load_matrix_data(args.matrix_file)
    if not matrix:
        print(json.dumps({
            "error": "모순 행렬 데이터를 로드할 수 없습니다.",
            "status": "error_no_data"
        }, ensure_ascii=False))
        sys.exit(1)

    result = solve(args.improving, args.worsening, matrix)
    print(json.dumps(result, ensure_ascii=False, indent=2))
