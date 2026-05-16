#!/usr/bin/env python3
"""
TRIZ Batch Contradiction Matrix Solver
다중 모순 쌍을 일괄 처리하여 발명 원리를 반환합니다.
대량 특허 데이터 분석(Mode B)에 사용됩니다.

사용법:
  python3 batch_triz_solver.py --payload '[{"id":0,"imp":"14","wor":"1"},{"id":1,"imp":"9","wor":"36"}]'
  python3 batch_triz_solver.py --payload '[{"id":0,"imp":"14","wor":"1"}]' --matrix_file /path/to/matrix_data.json
"""

import json
import argparse
import os
import sys


def load_matrix_data(filepath: str) -> dict:
    """외부 JSON 파일에서 모순 행렬 데이터를 로드합니다."""
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
            data.pop("_comment", None)
            return data
    except FileNotFoundError:
        print(json.dumps([{
            "error": f"파일을 찾을 수 없습니다: {filepath}",
            "status": "error_file_not_found"
        }], ensure_ascii=False), file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(json.dumps([{
            "error": f"JSON 파싱 오류: {str(e)}",
            "status": "error_invalid_json"
        }], ensure_ascii=False), file=sys.stderr)
        return {}


def solve_single(imp: str, wor: str, matrix_data: dict) -> tuple:
    """
    단일 모순 쌍을 처리합니다.

    Returns:
        tuple: (principles_list, status_str, note_str)
    """
    # 유효 범위 검사
    try:
        imp_num = int(imp)
        wor_num = int(wor)
        if not (1 <= imp_num <= 39):
            return [], "error_out_of_range", f"개선 변수 범위 오류: #{imp} (유효 범위: 1-39)"
        if not (1 <= wor_num <= 39):
            return [], "error_out_of_range", f"악화 변수 범위 오류: #{wor} (유효 범위: 1-39)"
    except ValueError:
        return [], "error_invalid_parameter", f"숫자로 변환 불가: imp={imp}, wor={wor}"

    # 정방향 조회
    principles = matrix_data.get(imp, {}).get(wor)
    if principles:
        filtered = [p for p in principles if p]
        return filtered, "success", ""

    # 역방향 조회
    reverse = matrix_data.get(wor, {}).get(imp)
    if reverse:
        filtered = [p for p in reverse if p]
        return filtered, "success_reverse_lookup", "역방향 조회 결과입니다."

    return [], "no_matrix_intersection", f"#{imp} vs #{wor} 조합 데이터 없음"


def solve_batch(contradictions: list, matrix_data: dict) -> list:
    """
    여러 개의 모순 쌍을 일괄 처리합니다.

    Args:
        contradictions: [{"id": 0, "imp": "14", "wor": "1"}, ...]
        matrix_data: 모순 행렬 데이터

    Returns:
        list: 각 모순 쌍의 처리 결과 목록
    """
    results = []

    for item in contradictions:
        row_id = item.get("id", "unknown")
        imp = str(item.get("imp", "")).strip()
        wor = str(item.get("wor", "")).strip()

        # 예외 1: 변수 번호 누락
        if not imp or not wor:
            results.append({
                "id": row_id,
                "principles": [],
                "status": "error_missing_variable",
                "message": "개선(imp) 또는 악화(wor) 변수가 누락되었습니다."
            })
            continue

        # 예외 2: 동일 변수
        if imp == wor:
            results.append({
                "id": row_id,
                "principles": [],
                "status": "error_same_variable",
                "message": f"개선 변수와 악화 변수가 동일합니다: #{imp}"
            })
            continue

        # 단일 조회 처리
        principles, status, note = solve_single(imp, wor, matrix_data)

        result = {
            "id": row_id,
            "principles": principles,
            "improving_param": f"#{imp}",
            "worsening_param": f"#{wor}",
            "status": status
        }

        if note:
            result["message"] = note

        if principles:
            result["count"] = len(principles)

        results.append(result)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch TRIZ Contradiction Matrix Solver - 다중 모순 쌍을 일괄 처리합니다",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--payload", type=str, required=True,
        help="JSON 배열 형태의 모순 쌍 목록 (예: '[{\"id\":0,\"imp\":\"14\",\"wor\":\"1\"}]')"
    )
    parser.add_argument(
        "--matrix_file", type=str, default="",
        help="모순 행렬 JSON 파일 경로 (기본: 스크립트 기준 ../references/matrix_data.json)"
    )

    args = parser.parse_args()

    matrix = load_matrix_data(args.matrix_file)
    if not matrix:
        print(json.dumps([{
            "error": "모순 행렬 데이터를 로드할 수 없습니다.",
            "status": "error_no_data"
        }], ensure_ascii=False))
        sys.exit(1)

    try:
        contradictions = json.loads(args.payload)
        if not isinstance(contradictions, list):
            raise ValueError("payload는 JSON 배열이어야 합니다.")
    except (json.JSONDecodeError, ValueError) as e:
        print(json.dumps([{
            "error": f"payload 파싱 오류: {str(e)}",
            "status": "error_invalid_payload"
        }], ensure_ascii=False))
        sys.exit(1)

    batch_results = solve_batch(contradictions, matrix)
    print(json.dumps(batch_results, ensure_ascii=False, indent=2))
