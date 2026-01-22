import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-tex", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    input_tex = Path(args.input_tex)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_docx = output_dir / "exam.docx"

    cmd = [
        "pandoc",
        str(input_tex),
        "-o", str(output_docx),
        "--from=latex",
        "--to=docx",
        "--mathml"
    ]

    subprocess.run(cmd, check=True)
    print(f"DOCX generated: {output_docx}")

if __name__ == "__main__":
    main()
