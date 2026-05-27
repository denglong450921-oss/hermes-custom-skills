"""Small entrypoint for the ppt-translator skill."""

from pathlib import Path
import sys

from translate_pptx import build_output_path, log, process_presentation


def main():
    """Run the bundled PPT translator with a simple source+language interface."""
    if len(sys.argv) < 3:
        print("Usage: python run_ppt_translator.py <input.pptx> <target_lang> [output.pptx]")
        sys.exit(1)

    input_path = Path(sys.argv[1]).expanduser().resolve()
    target_lang = sys.argv[2]
    output_path = (
        Path(sys.argv[3]).expanduser().resolve()
        if len(sys.argv) >= 4
        else build_output_path(str(input_path), target_lang)
    )

    log(f"Entry wrapper accepted request: {input_path.name} -> {target_lang}")
    final_output = process_presentation(str(input_path), str(output_path), target_lang)
    print(f"OUTPUT_FILE={final_output}")


if __name__ == "__main__":
    main()
