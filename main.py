
import json
import time
from pathlib import Path


# ========================================
# 1. 기본 필터 만들기
# ========================================

cross = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]

x_filter = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
]


# ========================================
# 2. MAC 연산 함수
# ========================================

def mac(pattern, filter_data):
    if not isinstance(pattern, list):
        raise ValueError("패턴이 배열이 아닙니다.")

    n = len(pattern)

    if n == 0:
        raise ValueError("패턴이 비어 있습니다.")

    if not isinstance(filter_data, list):
        raise ValueError("필터가 배열이 아닙니다.")

    if len(filter_data) != n:
        raise ValueError("패턴과 필터 크기가 다릅니다.")

    for matrix in [pattern, filter_data]:
        for row in matrix:
            if not isinstance(row, list) or len(row) != n:
                raise ValueError("행과 열의 크기가 다릅니다.")

            for value in row:
                if type(value) not in (int, float):
                    raise ValueError("숫자가 아닌 값이 있습니다.")

    score = 0

    for i in range(n):
        for j in range(n):
            score += pattern[i][j] * filter_data[i][j]

    return score


# ========================================
# 3. 점수 비교 함수
# ========================================

def decide(score_a, score_b):
    epsilon = 1e-9

    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"

    elif score_a > score_b:
        return "A"

    else:
        return "B"


# ========================================
# 4. JSON 전용 판정 함수
# ========================================

def decide_json(cross_score, x_score):
    epsilon = 1e-9

    if abs(cross_score - x_score) < epsilon:
        return "UNDECIDED"

    elif cross_score > x_score:
        return "Cross"

    else:
        return "X"


# ========================================
# 5. 라벨 정규화
# ========================================

def normalize_label(label):
    label = str(label).strip().lower()

    if label == "+" or label == "cross":
        return "Cross"

    elif label == "x":
        return "X"

    else:
        return None


# ========================================
# 6. 사용자 입력 함수
# ========================================

def input_matrix(name):
    matrix = []

    print(f"\n{name} 입력 (3줄)")

    for i in range(3):
        while True:
            try:
                text = input(f"{i + 1}번째 줄: ")

                row = list(map(float, text.split()))

                if len(row) != 3:
                    print("오류: 숫자 3개를 입력하세요.")
                    continue

                matrix.append(row)
                break

            except ValueError:
                print("오류: 숫자만 입력하세요.")

    return matrix


# ========================================
# 7. MAC 연산 시간 측정
# ========================================

def measure_time(pattern, filter_data):
    repeat = 10

    start = time.perf_counter()

    for _ in range(repeat):
        mac(pattern, filter_data)

    end = time.perf_counter()

    average_ms = (end - start) * 1000 / repeat

    return average_ms


# ========================================
# 8. 성능 분석
# ========================================

def performance_test(data=None):
    print("\n=== 성능 분석 (평균 10회) ===")
    print("크기       평균 시간(ms)    연산 횟수")
    print("------------------------------------")

    for n in [3, 5, 13, 25]:

        if n == 3:
            pattern = cross
            filter_data = cross

        elif data is not None and f"size_{n}" in data["filters"]:
            filters = data["filters"][f"size_{n}"]
            filter_data = filters["cross"]
            pattern = filter_data

        else:
            pattern = [[1] * n for _ in range(n)]
            filter_data = [[1] * n for _ in range(n)]

        try:
            average = measure_time(pattern, filter_data)
            operations = n * n

            print(
                f"{n}x{n:<5} "
                f"{average:12.6f} "
                f"{operations:12d}"
            )

        except (ValueError, TypeError) as error:
            print(f"{n}x{n}: 측정 실패 - {error}")


# ========================================
# 9. 사용자 입력 모드
# ========================================

def user_mode():
    print("\n=== 사용자 입력 모드 ===")

    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")

    print("\n필터 저장 완료!")

    pattern = input_matrix("패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    result = decide(score_a, score_b)

    print("\n=== MAC 계산 결과 ===")
    print("A 점수:", score_a)
    print("B 점수:", score_b)
    print("최종 판정:", result)

    average = measure_time(pattern, filter_a)
    print(f"3x3 평균 연산 시간: {average:.6f} ms")

    performance_test()


# ========================================
# 10. JSON 데이터 분석 모드
# ========================================

def json_mode():
    print("\n=== JSON 데이터 분석 ===")

    file_path = Path(__file__).resolve().parent / "data.json"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다.")
        return

    except json.JSONDecodeError:
        print("오류: JSON 파일 형식이 올바르지 않습니다.")
        return

    if not isinstance(data, dict):
        print("오류: JSON 최상위 구조가 올바르지 않습니다.")
        return

    if not isinstance(data.get("filters"), dict):
        print("오류: filters 구조가 올바르지 않습니다.")
        return

    if not isinstance(data.get("patterns"), dict):
        print("오류: patterns 구조가 올바르지 않습니다.")
        return

    print("JSON 파일 읽기 성공!")

    print("\n=== 필터 목록 ===")

    for size, filters in data["filters"].items():
        if isinstance(filters, dict):
            print(size, ":", list(filters.keys()))
        else:
            print(size, ": 잘못된 필터 구조")

    print("\n=== JSON 자동 채점 ===")

    passed = 0
    failed = 0
    failed_cases = []

    for name, case in data["patterns"].items():

        try:
            # 문제 이름에서 크기 추출
            parts = name.split("_")

            if len(parts) != 3 or parts[0] != "size":
                raise ValueError("문제 이름 형식 오류")

            n = int(parts[1])

            if n not in [5, 13, 25]:
                raise ValueError("지원하지 않는 패턴 크기")

            # 크기에 맞는 필터 선택
            filters = data["filters"][f"size_{n}"]

            if not isinstance(filters, dict):
                raise ValueError("필터 구조 오류")

            cross_filter = filters["cross"]
            x_filter = filters["x"]

            # 패턴 및 정답 가져오기
            pattern = case["input"]
            expected = normalize_label(case["expected"])

            if expected is None:
                raise ValueError("정답 라벨 오류")

            # 패턴과 필터 크기 검사
            for matrix in [pattern, cross_filter, x_filter]:
                if not isinstance(matrix, list):
                    raise ValueError("배열 형식 오류")

                if len(matrix) != n:
                    raise ValueError("패턴 또는 필터 크기 불일치")

                for row in matrix:
                    if not isinstance(row, list) or len(row) != n:
                        raise ValueError("행 또는 열 크기 불일치")

            # MAC 점수 계산
            cross_score = mac(pattern, cross_filter)
            x_score = mac(pattern, x_filter)

            # 판정
            result = decide_json(cross_score, x_score)

            # PASS / FAIL 검사
            if result == expected:
                status = "PASS"
                passed += 1

            else:
                status = "FAIL"
                failed += 1

                if result == "UNDECIDED":
                    reason = "epsilon 동점 규칙으로 판정 불가"
                else:
                    reason = "판정 결과와 정답 불일치"

                failed_cases.append(f"{name}: {reason}")

            print(f"\n문제: {name}")
            print(f"Cross 점수: {cross_score}")
            print(f"X 점수: {x_score}")
            print(f"판정: {result}")
            print(f"정답: {expected}")
            print(f"결과: {status}")

        except (KeyError, ValueError, TypeError, IndexError) as error:
            failed += 1
            failed_cases.append(f"{name}: {error}")

            print(f"\n문제: {name}")
            print(f"결과: FAIL ({error})")

    # 성능 분석
    performance_test(data)

    # 결과 요약
    print("\n=== 최종 결과 리포트 ===")
    print("전체 문제:", passed + failed)
    print("통과:", passed)
    print("실패:", failed)

    print("\n=== 실패 케이스 목록 ===")

    if len(failed_cases) == 0:
        print("실패한 문제가 없습니다.")

    else:
        for case in failed_cases:
            print("-", case)


# ========================================
# 11. 프로그램 시작
# ========================================

def main():
    while True:
        print("\n==============================")
        print("     Mini NPU Simulator")
        print("==============================")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        print("0. 종료")

        choice = input("선택: ").strip()

        if choice == "1":
            user_mode()

        elif choice == "2":
            json_mode()

        elif choice == "0":
            print("프로그램을 종료합니다.")
            break

        else:
            print("오류: 0, 1, 2 중에서 선택하세요.")


if __name__ == "__main__":
    main()
