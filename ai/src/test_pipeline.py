from pathlib import Path

from pipeline import run_pipeline


def main():
    # 테스트할 이미지 경로
    image_path = Path("images/4.png")

    # 백엔드에서 UploadFile.read() 한 것처럼 bytes로 읽음
    image_bytes = image_path.read_bytes()

    result = run_pipeline(image_bytes)

    print("\n===== PIPELINE RESULT =====")
    print("OCR:")
    print(result["ocr_text"])

    print("\nCAPTION:")
    print(result["caption"])

    print("\nEVENT:")
    print(result["event"])

    print("\nUSED MODEL:")
    print(result["used_model"])

    print("\nFALLBACK USED:")
    print(result["fallback_used"])

    print("\nFALLBACK REASONS:")
    print(result["fallback_reasons"])


if __name__ == "__main__":
    main()