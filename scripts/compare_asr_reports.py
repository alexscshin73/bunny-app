import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two saved ASR evaluation reports."
    )
    parser.add_argument("baseline", type=Path, help="Baseline report JSON path.")
    parser.add_argument("candidate", type=Path, help="Candidate report JSON path.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON instead of human-readable text.",
    )
    return parser.parse_args()


def load_report(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def index_reports(payload: dict[str, object]) -> dict[tuple[str, str], dict[str, object]]:
    reports = payload.get("reports", [])
    indexed: dict[tuple[str, str], dict[str, object]] = {}
    if not isinstance(reports, list):
        return indexed

    for item in reports:
        if not isinstance(item, dict):
            continue
        model = str(item.get("model", ""))
        file_path = str(item.get("path") or item.get("file") or "")
        indexed[(model, file_path)] = item
    return indexed


def numeric_value(report: dict[str, object], key: str) -> float | None:
    comparison = report.get("comparison")
    if not isinstance(comparison, dict):
        return None
    value = comparison.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def bool_value(report: dict[str, object], key: str) -> bool | None:
    comparison = report.get("comparison")
    if not isinstance(comparison, dict):
        return None
    value = comparison.get(key)
    if isinstance(value, bool):
        return value
    return None


def score_report(report: dict[str, object]) -> float:
    similarity = numeric_value(report, "similarity") or 0.0
    contains_bonus = 0.15 if bool_value(report, "contains") is True else 0.0
    language_bonus = 0.15 if bool_value(report, "language_match") is True else 0.0
    unknown_penalty = -0.3 if str(report.get("detected_language", "")) in {"", "unknown"} else 0.0
    empty_penalty = -0.3 if not str(report.get("text", "")).strip() else 0.0
    return similarity + contains_bonus + language_bonus + unknown_penalty + empty_penalty


def compare_reports(
    baseline_payload: dict[str, object],
    candidate_payload: dict[str, object],
) -> dict[str, object]:
    baseline_index = index_reports(baseline_payload)
    candidate_index = index_reports(candidate_payload)
    shared_keys = sorted(set(baseline_index) & set(candidate_index))

    files: list[dict[str, object]] = []
    candidate_wins = 0
    baseline_wins = 0
    ties = 0

    for key in shared_keys:
        baseline = baseline_index[key]
        candidate = candidate_index[key]
        baseline_score = round(score_report(baseline), 3)
        candidate_score = round(score_report(candidate), 3)
        delta = round(candidate_score - baseline_score, 3)

        if delta > 0:
            winner = "candidate"
            candidate_wins += 1
        elif delta < 0:
            winner = "baseline"
            baseline_wins += 1
        else:
            winner = "tie"
            ties += 1

        files.append(
            {
                "model": key[0],
                "path": key[1],
                "winner": winner,
                "baseline_score": baseline_score,
                "candidate_score": candidate_score,
                "score_delta": delta,
                "baseline_text": baseline.get("text", ""),
                "candidate_text": candidate.get("text", ""),
                "baseline_language": baseline.get("detected_language", ""),
                "candidate_language": candidate.get("detected_language", ""),
                "baseline_comparison": baseline.get("comparison", {}),
                "candidate_comparison": candidate.get("comparison", {}),
            }
        )

    return {
        "baseline": str(baseline_payload.get("source", "baseline")),
        "candidate": str(candidate_payload.get("source", "candidate")),
        "shared_files": len(shared_keys),
        "candidate_wins": candidate_wins,
        "baseline_wins": baseline_wins,
        "ties": ties,
        "files": files,
    }


def print_human(result: dict[str, object]) -> None:
    print("REPORT COMPARISON")
    print(f"baseline: {result['baseline']}")
    print(f"candidate: {result['candidate']}")
    print(
        f"shared_files={result['shared_files']} | "
        f"candidate_wins={result['candidate_wins']} | "
        f"baseline_wins={result['baseline_wins']} | ties={result['ties']}"
    )
    print()

    for item in result["files"]:
        print(
            f"{item['winner'].upper():>9} | {item['model']} | {item['path']} | "
            f"delta={item['score_delta']}"
        )
        print(
            f"  baseline : lang={item['baseline_language']} text={item['baseline_text']!r}"
        )
        print(
            f"  candidate: lang={item['candidate_language']} text={item['candidate_text']!r}"
        )
        print()


def main() -> None:
    args = parse_args()
    baseline_payload = load_report(args.baseline)
    candidate_payload = load_report(args.candidate)
    baseline_payload["source"] = str(args.baseline)
    candidate_payload["source"] = str(args.candidate)

    result = compare_reports(baseline_payload, candidate_payload)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print_human(result)


if __name__ == "__main__":
    main()
