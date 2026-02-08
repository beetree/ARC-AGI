#!/usr/bin/env python3
"""
Build a self-contained paper bundle under ./output/:
  - output/paper.md  (concatenated Markdown)
  - output/paper.tex (Pandoc -> LaTeX)
  - output/paper.pdf (LaTeX -> PDF)

Dependencies:
  - pandoc (required for .tex)
  - latexmk (preferred) or pdflatex (required for .pdf unless --skip-pdf)
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_SECTION_FILES = {
    # Title/author/abstract are rendered from metadata/template.
    "00_front_matter.md",
    "00_abstract.md",
}

CONFIG_FILES = [
    "metadata.yaml",
    "refs.bib",
    "template.tex",
    "IEEEtran.cls",
    "IEEEtran.bst",
]


def _run(cmd: list[str], *, cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd))
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}")


def _which(name: str) -> str | None:
    return shutil.which(name)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _copytree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def build_markdown(out_dir: Path) -> Path:
    section_paths = sorted(ROOT.glob("[0-9][0-9]_*.md"))
    section_paths = [p for p in section_paths if p.name not in EXCLUDED_SECTION_FILES]
    if not section_paths:
        raise FileNotFoundError(
            "No section files found. Expected files like 01_introduction.md, 02_....md"
        )

    parts: list[str] = []
    for p in section_paths:
        content = _read_text(p).rstrip() + "\n"
        parts.append(content)

    paper_md = "\n\n".join(parts).rstrip() + "\n"

    # Sanity checks: title/abstract come from metadata/template.
    if re.search(r"^#\\s", paper_md, flags=re.MULTILINE):
        raise ValueError(
            "Found a top-level '# ' heading in concatenated markdown. "
            "Remove it (title comes from metadata.yaml)."
        )
    if "paper_data/" in paper_md:
        raise ValueError("Found forbidden reference to 'paper_data/' in output markdown.")

    out_path = out_dir / "paper.md"
    _write_text(out_path, paper_md)
    return out_path


def copy_assets(out_dir: Path) -> None:
    _copytree(ROOT / "figures", out_dir / "figures")

    for rel in CONFIG_FILES:
        src = ROOT / rel
        if not src.exists():
            raise FileNotFoundError(f"Missing config file: {rel}")
        shutil.copy2(src, out_dir / rel)

    # Optional CSL style directory (kept if present).
    if (ROOT / "csl").exists():
        _copytree(ROOT / "csl", out_dir / "csl")


_MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_HTML_IMG_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", flags=re.IGNORECASE)
_LATEX_GRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def validate_self_contained(out_dir: Path, md_path: Path) -> None:
    text = _read_text(md_path)
    refs: set[str] = set()

    for m in _MD_IMG_RE.finditer(text):
        refs.add(m.group(1))
    for m in _HTML_IMG_RE.finditer(text):
        refs.add(m.group(1))
    for m in _LATEX_GRAPHICS_RE.finditer(text):
        refs.add(m.group(1))

    missing: list[str] = []
    for ref in sorted(refs):
        if ref.startswith(("http://", "https://", "data:")):
            continue
        # Strip any fragment/query (rare in local refs, but cheap to support).
        ref_clean = ref.split("#", 1)[0].split("?", 1)[0]
        if not (out_dir / ref_clean).exists():
            missing.append(ref)

    if missing:
        raise FileNotFoundError(
            "Missing referenced assets in output bundle:\n- " + "\n- ".join(missing)
        )


def build_latex(out_dir: Path, md_path: Path) -> Path:
    if _which("pandoc") is None:
        raise FileNotFoundError(
            "pandoc not found in PATH. Install pandoc to build output/paper.tex.\n"
            "On Ubuntu: sudo apt-get install -y pandoc"
        )

    tex_path = out_dir / "paper.tex"

    cmd = [
        "pandoc",
        str(md_path.name),
        "--from",
        "markdown",
        "--to",
        "latex",
        "--standalone",
        "--shift-heading-level-by=-1",
        "--metadata-file",
        "metadata.yaml",
        "--template",
        "template.tex",
        "--citeproc",
        "--bibliography",
        "refs.bib",
        "--resource-path",
        ".:figures",
        "-o",
        str(tex_path.name),
    ]
    _run(cmd, cwd=out_dir)

    # Post-process: replace longtable with tabular for two-column IEEE compatibility.
    tex_content = _read_text(tex_path)
    tex_content = re.sub(
        r"\\begin\{longtable\}\[]\{([^}]*)\}",
        r"\\begin{table}[htbp]\n\\centering\n\\footnotesize\n\\begin{tabular}{\1}",
        tex_content,
    )
    tex_content = tex_content.replace(r"\endhead", "")
    tex_content = tex_content.replace(r"\endlastfoot", "")
    tex_content = tex_content.replace(
        r"\end{longtable}", r"\end{tabular}" + "\n" + r"\end{table}"
    )
    _write_text(tex_path, tex_content)

    return tex_path


def build_pdf(out_dir: Path, tex_path: Path) -> Path:
    pdf_path = out_dir / "paper.pdf"

    if _which("latexmk") is not None:
        _run(
            [
                "latexmk",
                "-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                str(tex_path.name),
            ],
            cwd=out_dir,
        )
    elif _which("pdflatex") is not None:
        # Two passes for references/TOC. Bibliography is handled by --citeproc.
        for _ in range(2):
            _run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    str(tex_path.name),
                ],
                cwd=out_dir,
            )
    else:
        raise FileNotFoundError(
            "Neither latexmk nor pdflatex found in PATH. Install TeX to build output/paper.pdf.\n"
            "On Ubuntu: sudo apt-get install -y texlive-latex-base texlive-latex-recommended texlive-latex-extra latexmk"
        )

    if not pdf_path.exists():
        raise FileNotFoundError("PDF build completed without producing output/paper.pdf")
    return pdf_path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="output", help="Output directory (default: output)")
    ap.add_argument(
        "--md-only",
        action="store_true",
        help="Only write output/paper.md (skip pandoc and PDF compilation)",
    )
    ap.add_argument("--skip-pdf", action="store_true", help="Skip PDF compilation")
    args = ap.parse_args(argv)

    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    copy_assets(out_dir)
    md_path = build_markdown(out_dir)
    validate_self_contained(out_dir, md_path)

    if args.md_only:
        print(f"Wrote: {md_path}")
        return 0

    tex_path = build_latex(out_dir, md_path)
    if not args.skip_pdf:
        build_pdf(out_dir, tex_path)

    print(f"Wrote: {md_path}")
    print(f"Wrote: {tex_path}")
    if not args.skip_pdf:
        print(f"Wrote: {out_dir / 'paper.pdf'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
