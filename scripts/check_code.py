#!/usr/bin/env python3
"""
Скрипт для автоматической проверки качества кода.
Выполняет последовательно:
1. Сортировку импортов (isort)
2. Форматирование кода (black)
3. Проверку стиля (ruff)
"""

import subprocess
import sys
from pathlib import Path
from typing import List


class CodeQualityChecker:
    def __init__(self, file_paths: List[str]):
        self.file_paths = [Path(p) for p in file_paths]
        self.failed_checks = 0

    def run_checks(self) -> bool:
        """Запускает все проверки и возвращает True если все успешно"""
        print("\n🔍 Starting code quality checks...\n")

        for file_path in self.file_paths:
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                self.failed_checks += 1
                continue

            print(f"\n📄 Processing file: {file_path}")

            # 1. Сортировка импортов
            if not self.run_isort(file_path):
                self.failed_checks += 1

            # 2. Форматирование кода
            if not self.run_black(file_path):
                self.failed_checks += 1

            # 3. Проверка стиля (ruff)
            if not self.run_ruff(file_path):
                self.failed_checks += 1

        if self.failed_checks == 0:
            print("\n✅ All code quality checks passed successfully!")
            return True
        else:
            print(f"\n❌ {self.failed_checks} checks failed!")
            return False

    def run_command(self, cmd: List[str], check_name: str) -> bool:
        """Запускает команду и обрабатывает результат"""
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  ✔ {check_name} passed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ {check_name} failed:")
            print(e.stderr or e.stdout)
            return False

    def run_isort(self, file_path: Path) -> bool:
        return self.run_command(["isort", str(file_path)], "Import sorting (isort)")

    def run_black(self, file_path: Path) -> bool:
        return self.run_command(["black", str(file_path)], "Code formatting (black)")

    def run_ruff(self, file_path: Path) -> bool:
        return self.run_command(
            ["ruff", "check", "--fix", str(file_path)],
            "Style check and auto-fix (ruff)",
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_code.py <file1> [<file2> ...]")
        print(
            "Example: poetry run python scripts/check_code.py app/presentation/api/v1/endpoints/data.py"
        )
        sys.exit(1)

    checker = CodeQualityChecker(sys.argv[1:])
    success = checker.run_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
