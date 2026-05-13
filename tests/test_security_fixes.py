"""
Tests to verify security fixes and model migration across the workspace.
"""
import ast
import os
import re
import glob
import pytest


# ============================================================
# 1. Syntax validation — all Python files must parse correctly
# ============================================================

def _all_py_files():
    """Collect all .py files in the workspace, excluding venv/node_modules."""
    for f in glob.glob("**/*.py", recursive=True):
        if any(skip in f for skip in ["node_modules", ".git", "env/", "venv/"]):
            continue
        yield f


@pytest.mark.parametrize("filepath", list(_all_py_files()), ids=lambda p: p)
def test_syntax_valid(filepath):
    """Every Python file must have valid syntax."""
    source = open(filepath).read()
    ast.parse(source)  # raises SyntaxError on failure


# ============================================================
# 2. Security: path traversal — git_handler._sanitize_name
# ============================================================

class TestSanitizeName:
    """Test the _sanitize_name helper in git_handler.py."""

    @staticmethod
    def _get_sanitize():
        # Import the function dynamically to avoid needing full deps
        src = open("AWS-GenAI-Code-Security-Review/code_review/git_handler.py").read()
        tree = ast.parse(src)
        # Extract the function source and exec it
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_sanitize_name":
                func_src = ast.get_source_segment(src, node)
                ns = {}
                exec("import re\n" + func_src, ns)
                return ns["_sanitize_name"]
        pytest.fail("_sanitize_name not found in git_handler.py")

    def test_normal_name(self):
        fn = self._get_sanitize()
        assert fn("my-repo") == "my-repo"

    def test_strips_path_traversal(self):
        fn = self._get_sanitize()
        result = fn("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_strips_leading_dot(self):
        fn = self._get_sanitize()
        result = fn(".hidden-repo")
        assert not result.startswith(".")

    def test_empty_becomes_unnamed(self):
        fn = self._get_sanitize()
        assert fn("...") == "unnamed"

    def test_special_chars_replaced(self):
        fn = self._get_sanitize()
        result = fn("repo;rm -rf /")
        assert ";" not in result
        assert " " not in result


# ============================================================
# 3. Security: app.py uses _sanitize_name and realpath checks
# ============================================================

class TestAppPathSecurity:
    """Verify app.py has path traversal protections."""

    @staticmethod
    def _read_app():
        return open("AWS-GenAI-Code-Security-Review/app.py").read()

    def test_has_sanitize_name(self):
        src = self._read_app()
        assert "_sanitize_name" in src

    def test_has_realpath_check(self):
        src = self._read_app()
        assert "os.path.realpath" in src

    def test_no_raw_fstring_path(self):
        """Should not use f-string to build report paths from raw user input."""
        src = self._read_app()
        # The old vulnerable pattern: f"report/{url.split(...)}"
        assert 'f"report/{url' not in src


# ============================================================
# 4. Security: generator.py uses os.path.basename for filenames
# ============================================================

class TestGeneratorPathSecurity:
    """Verify generator.py sanitizes uploaded filenames."""

    @staticmethod
    def _read_gen():
        return open(
            "Amazon-Bedrock-Alt-Text-Generator/pdf_image_alt_text_generator/generator.py"
        ).read()

    def test_uses_basename(self):
        src = self._read_gen()
        assert "os.path.basename" in src

    def test_uses_realpath_check(self):
        src = self._read_gen()
        assert "os.path.realpath" in src

    def test_no_raw_file_name(self):
        """Should not use file.name directly in open() without sanitization."""
        src = self._read_gen()
        # Old pattern: open(os.path.join("files", file.name.replace(...)))
        assert 'file.name.replace(" ", "_")), "wb"' not in src


# ============================================================
# 5. Security: git_handler.py has zip-slip protection
# ============================================================

class TestZipSlipProtection:
    """Verify git_handler.py validates zip entries before extraction."""

    @staticmethod
    def _read_handler():
        return open(
            "AWS-GenAI-Code-Security-Review/code_review/git_handler.py"
        ).read()

    def test_has_zip_entry_validation(self):
        src = self._read_handler()
        assert "zip_ref.namelist()" in src

    def test_checks_realpath_for_zip(self):
        src = self._read_handler()
        # Should validate each member path stays within extract_path
        assert "os.path.realpath" in src

    def test_raises_on_unsafe_entry(self):
        src = self._read_handler()
        assert "Unsafe zip entry" in src


# ============================================================
# 6. Security: stream JSON parsing has error handling
# ============================================================

LIBS_FILES = [
    "AWS-Educational-Assistant/Libs.py",
    "AWS-First-Cloud-Journey-Uniform-Detection/Libs.py",
    "Content-Moderation-with-Amazon-Bedrock/Libs.py",
    "TapVision-with-Amazon-Bedrock/Libs.py",
    "Location-Analysis-System-with-Amazon-Bedrock/Libs.py",
    "Product-Description-Generator-with-Amazon-Bedrock/Libs.py",
]


@pytest.mark.parametrize("filepath", LIBS_FILES)
def test_stream_parsing_has_error_handling(filepath):
    """All Libs.py files must wrap json.loads in try/except."""
    src = open(filepath).read()
    assert "json.JSONDecodeError" in src or "JSONDecodeError" in src
    assert "except" in src


# ============================================================
# 7. Model migration: no legacy model IDs in active code
# ============================================================

LEGACY_MODELS = [
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
    "stability.stable-diffusion-xl-v1",
]

# Files where legacy IDs are acceptable (comments, pricing tables, model lists)
ALLOWED_LEGACY_FILES = {
    # Evaluator apps keep old models in selection lists and pricing tables
    "GenAI-Model-Evaluator/pricing_calculator.py",
    "GenAI-Model-Evaluator/app.py",
    "Amazon-Bedrock-Model-Evaluator/pricing_calculator.py",
    "Amazon-Bedrock-Model-Evaluator/app.py",
    # Image generation app lists multiple Stability models as options
    "Generate-images-using-Amazon-Bedrock-with-stability-diffusion-model/app.py",
    # Nova samples reference their own models
    "amazon-nova-samples/multimodal-understanding/sample-apps/01-multimodal-with-helper-libraries/mm_understanding.py",
    # Prompt toolkit and Guardrails demo show model selection lists — legacy IDs intentional
    "AWS-Prompt-Engineering-Toolkit/app.py",
    "AWS-Bedrock-Guardrails-Demo/app.py",
}


def _active_code_files():
    """All .py files excluding allowed-legacy and non-code dirs."""
    for f in glob.glob("**/*.py", recursive=True):
        if any(skip in f for skip in ["node_modules", ".git", "env/", "venv/", "tests/"]):
            continue
        if f in ALLOWED_LEGACY_FILES:
            continue
        yield f


@pytest.mark.parametrize("filepath", list(_active_code_files()), ids=lambda p: p)
def test_no_legacy_model_in_active_code(filepath):
    """Active code should not reference legacy model IDs (comments are OK)."""
    src = open(filepath).read()
    for model in LEGACY_MODELS:
        # Find all occurrences
        for i, line in enumerate(src.splitlines(), 1):
            stripped = line.strip()
            # Skip comments and docstrings
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            # Skip lines that are inside docstrings (param descriptions)
            if ":param" in stripped or ":return" in stripped:
                continue
            if model in line and not stripped.startswith("#"):
                pytest.fail(
                    f"{filepath}:{i} still references legacy model '{model}': {stripped}"
                )


# ============================================================
# 8. Model migration: new model IDs are present in Libs.py
# ============================================================

NEW_SONNET = "anthropic.claude-sonnet-4-6"


@pytest.mark.parametrize("filepath", LIBS_FILES)
def test_libs_use_new_sonnet(filepath):
    """All Libs.py files should reference the new Sonnet 4.6 model."""
    src = open(filepath).read()
    assert NEW_SONNET in src, f"{filepath} does not contain {NEW_SONNET}"


IMAGE_LIB_FILES = [
    "AWS-First-Cloud-Journey-Uniform-Detection/image_lib.py",
    "Content-Moderation-with-Amazon-Bedrock/image_lib.py",
    "TapVision-with-Amazon-Bedrock/image_lib.py",
    "Product-Description-Generator-with-Amazon-Bedrock/image_lib.py",
    "Location-Analysis-System-with-Amazon-Bedrock/image_lib.py",
]


@pytest.mark.parametrize("filepath", IMAGE_LIB_FILES)
def test_image_libs_use_nova_canvas(filepath):
    """All image_lib.py files should use Nova Canvas instead of Stable Diffusion."""
    src = open(filepath).read()
    assert "amazon.nova-canvas-v1:0" in src
    assert "stability.stable-diffusion-xl-v1" not in src


def test_alt_text_generator_uses_nova_lite():
    """Alt text generator should use Nova 2 Lite instead of Haiku."""
    src = open(
        "Amazon-Bedrock-Alt-Text-Generator/pdf_image_alt_text_generator/generator.py"
    ).read()
    assert "amazon.nova-2-lite-v1:0" in src
    assert "claude-3-haiku" not in src
