"""
Load real judgments from the AWS Open Data Supreme Court dataset.

Expected local layout:
    data/supreme-court/
      metadata/parquet/year=2023/metadata.parquet
      data/tar/year=2023/english/english.tar

The parquet files contain metadata. The tar files contain judgment text/html/pdf
payloads. This loader maps a small configurable slice into the app's Judgment
dataclass so the rest of the BM25 + vector + graph pipeline stays unchanged.
"""

from __future__ import annotations

import hashlib
import os
import re
import tarfile
from pathlib import Path
from typing import Any

from .models import Judgment


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT_DIR / "data" / "supreme-court"


def _clean_text(text: str, limit: int = 9000) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _safe_str(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    try:
        if value != value:  # NaN
            return fallback
    except Exception:
        pass
    return str(value).strip() or fallback


def _find_column(columns: list[str], *needles: str) -> str | None:
    lowered = {c.lower(): c for c in columns}
    for needle in needles:
        for lower, original in lowered.items():
            if needle in lower:
                return original
    return None


def _infer_section(text: str) -> str:
    matches = re.findall(r"\b(?:section|s\.)\s*(\d+[a-z]?)\b", text, flags=re.I)
    if matches:
        return f"Section {matches[0].upper()}"
    return "Supreme Court Judgment"


def _infer_outcome(text: str) -> str:
    t = text.lower()
    if "appeal is allowed" in t or "appeals are allowed" in t or "petition is allowed" in t:
        return "allowed"
    if "appeal is dismissed" in t or "appeals are dismissed" in t or "petition is dismissed" in t:
        return "dismissed"
    if "conviction" in t and ("set aside" in t or "acquitted" in t):
        return "acquitted"
    if "conviction" in t or "convicted" in t:
        return "convicted"
    return "disposed"


def _case_id_from(*parts: str) -> str:
    raw = "|".join(parts)
    digest = hashlib.md5(raw.encode("utf-8", errors="ignore")).hexdigest()[:10].upper()
    return f"SC_REAL_{digest}"


def _read_tar_texts(data_dir: Path, years: set[int], max_docs: int) -> dict[str, str]:
    texts: dict[str, str] = {}
    tar_paths: list[Path] = []
    for year in sorted(years, reverse=True):
        tar_paths.extend((data_dir / "data" / "tar" / f"year={year}" / "english").glob("*.tar"))

    for tar_path in tar_paths:
        with tarfile.open(tar_path, "r:*") as tar:
            for member in tar:
                if len(texts) >= max_docs:
                    return texts
                if not member.isfile():
                    continue
                suffix = Path(member.name).suffix.lower()
                if suffix not in {".txt", ".html", ".htm", ".xml"}:
                    continue
                extracted = tar.extractfile(member)
                if not extracted:
                    continue
                payload = extracted.read()
                text = _clean_text(payload.decode("utf-8", errors="ignore"))
                if len(text) >= 400:
                    texts[Path(member.name).stem.lower()] = text
    return texts


def _metadata_records(data_dir: Path, years: set[int], max_docs: int) -> list[dict[str, Any]]:
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError(
            "Real data loading requires pandas + pyarrow. Run: "
            ".\\myenv\\Scripts\\pip.exe install -r backend\\requirements.txt"
        ) from exc

    parquet_paths: list[Path] = []
    for year in sorted(years, reverse=True):
        parquet_paths.extend((data_dir / "metadata" / "parquet" / f"year={year}").glob("*.parquet"))

    records: list[dict[str, Any]] = []
    for parquet_path in parquet_paths:
        frame = pd.read_parquet(parquet_path)
        for record in frame.head(max_docs - len(records)).to_dict("records"):
            record["_year"] = int(re.search(r"year=(\d+)", str(parquet_path)).group(1))
            records.append(record)
            if len(records) >= max_docs:
                return records
    return records


def load_real_judgments(
    data_dir: Path | str = DEFAULT_DATA_DIR,
    max_docs: int | None = None,
    years: list[int] | None = None,
) -> list[Judgment]:
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return []

    max_docs = max_docs or int(os.getenv("NYAY_REAL_MAX_DOCS", "200"))
    if years is None:
        env_years = os.getenv("NYAY_REAL_YEARS", "2024,2023,2022")
        years = [int(y.strip()) for y in env_years.split(",") if y.strip()]
    year_set = set(years)

    records = _metadata_records(data_dir, year_set, max_docs)
    if not records:
        return []

    columns = list(records[0].keys())
    title_col = _find_column(columns, "title", "case_name", "name", "diary")
    date_col = _find_column(columns, "date", "judgment_date", "judgement_date")
    bench_col = _find_column(columns, "bench", "judge", "coram")
    petitioner_col = _find_column(columns, "petitioner", "appellant")
    respondent_col = _find_column(columns, "respondent")
    file_col = _find_column(columns, "file", "path", "document", "pdf", "html")

    tar_texts = _read_tar_texts(data_dir, year_set, max_docs)
    judgments: list[Judgment] = []

    for index, record in enumerate(records):
        title = _safe_str(record.get(title_col), fallback=f"Supreme Court judgment {index + 1}") if title_col else f"Supreme Court judgment {index + 1}"
        date = _safe_str(record.get(date_col), fallback=str(record.get("_year", ""))) if date_col else str(record.get("_year", ""))
        judge = _safe_str(record.get(bench_col), fallback="Supreme Court bench") if bench_col else "Supreme Court bench"
        petitioner = _safe_str(record.get(petitioner_col), fallback="") if petitioner_col else ""
        respondent = _safe_str(record.get(respondent_col), fallback="") if respondent_col else ""

        file_hint = _safe_str(record.get(file_col), fallback="") if file_col else ""
        text = ""
        if file_hint:
            stem = Path(file_hint).stem.lower()
            text = tar_texts.get(stem, "")
        if not text and index < len(tar_texts):
            text = list(tar_texts.values())[index]

        raw_text = text or " ".join(
            part for part in [title, petitioner, respondent, judge, date] if part
        )
        facts = _clean_text(raw_text, limit=900)
        reasoning = _clean_text(raw_text[900:], limit=1200) if len(raw_text) > 900 else facts
        section = _infer_section(raw_text)
        outcome = _infer_outcome(raw_text)

        judgments.append(
            Judgment(
                case_id=_case_id_from(title, date, str(index)),
                court="Supreme Court of India",
                date=date,
                judge=judge,
                section_cited=section,
                outcome=outcome,
                facts_summary=facts or title,
                legal_reasoning=reasoning or facts or title,
                raw_text=raw_text,
                state="National",
                citations=[],
            )
        )

    return judgments
