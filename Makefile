# =============================================================
# KOERU — Makefile
# Dùng trên Linux/Mac: make <target>
# Trên Windows: bash tools/build.sh <step>
# =============================================================

PYTHON ?= python3
SHELL  := /bin/bash

.PHONY: all fetch fix validate clean test help

## all: Chạy toàn bộ pipeline (fetch → fix → validate)
all:
	@bash tools/build.sh all

## fetch: Chỉ fetch dữ liệu từ KanjiAPI
fetch:
	@bash tools/build.sh fetch

## fix: Chỉ chạy các bước fix/patch
fix:
	@bash tools/build.sh fix

## validate: Chỉ chạy QA + syntax check
validate:
	@bash tools/build.sh validate

## clean: Xóa cache files
clean:
	@bash tools/build.sh clean

## test: Chạy Playwright E2E tests
test:
	@echo "[test] Khởi động local server..."
	@$(PYTHON) -m http.server 8000 &
	@sleep 1
	@npx playwright test --project=chromium || true
	@kill $$(lsof -t -i:8000) 2>/dev/null || true

## help: Hiện tất cả commands
help:
	@echo ""
	@echo "KOERU Build Commands:"
	@grep -E '^## ' Makefile | sed 's/## /  make /'
	@echo ""
