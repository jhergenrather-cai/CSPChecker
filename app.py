import streamlit as st
import re

st.set_page_config(page_title="AP CSP Create Task Checker", layout="wide")

st.title("AP CSP Create Task Structural Checker (Python)")
st.markdown("Paste your Python code below and click **Analyze My Code**.")

code_input = st.text_area("Paste your code here:", height=400)


def analyze_code(code):
    results = {
        "procedure": [],
        "algorithm": [],
        "list": [],
        "input": [],
        "output": []
    }

    lines = code.split("\n")

    # ============================
    # FUNCTION DETECTION
    # ============================
    functions = []
    for i, line in enumerate(lines):
        match = re.match(r"\s*def\s+(\w+)\((.*?)\):", line)
        if match:
            functions.append({
                "name": match.group(1),
                "params": match.group(2).strip(),
                "line": i + 1
            })

    if not functions:
        results["procedure"].append(("⚠ No functions detected using 'def'.", "warning"))
        return results

    for func in functions:
        name = func["name"]
        params = func["params"]
        line_number = func["line"]

        results["procedure"].append(
            (f"✔ Function '{name}' detected on line {line_number}", "success")
        )

        if params:
            results["procedure"].append(
                (f"✔ Function '{name}' has parameter(s): {params}", "success")
            )
        else:
            results["procedure"].append(
                (f"⚠ Function '{name}' has NO parameters.", "warning")
            )

        # Extract function body
        start_index = line_number - 1
        indent_level = len(lines[start_index]) - len(lines[start_index].lstrip())
        body_lines = []

        for line in lines[start_index + 1:]:
            if line.strip() == "":
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent > indent_level:
                body_lines.append(line)
            else:
                break

        # Check for parameter usage
        if params:
            param_name = params.split(",")[0].strip()
            if any(param_name in line for line in body_lines):
                results["procedure"].append(
                    (f"✔ Parameter '{param_name}' is used inside '{name}'", "success")
                )
            else:
                results["procedure"].append(
                    (f"⚠ Parameter '{param_name}' is NOT used inside '{name}'", "warning")
                )

        # Algorithm checks inside function
        has_if = False
        has_loop = False

        for idx, line in enumerate(body_lines):
            if "if " in line:
                has_if = True
                results["algorithm"].append(
                    (f"✔ Selection found in '{name}' on line {start_index + idx + 2}", "success")
                )
            if "for " in line or "while " in line:
                has_loop = True
                results["algorithm"].append(
                    (f"✔ Loop found in '{name}' on line {start_index + idx + 2}", "success")
                )

        if not has_if:
            results["algorithm"].append(
                (f"⚠ No selection (if/elif/else) found inside '{name}'", "warning")
            )

        if not has_loop:
            results["algorithm"].append(
                (f"⚠ No loop (for/while) found inside '{name}'", "warning")
            )

    # ============================
    # LIST CHECK
    # ============================
    for i, line in enumerate(lines):
        list_match = re.match(r"\s*(\w+)\s*=\s*\[.*\]", line)
        if list_match:
            list_name = list_match.group(1)
            results["list"].append(
                (f"✔ List '{list_name}' declared on line {i+1}", "success")
            )

    if not results["list"]:
        results["list"].append(
            ("⚠ No lists detected. You must use a list to manage complexity.", "warning")
        )

    # ============================
    # INPUT CHECK
    # ============================
    input_found = False
    for i, line in enumerate(lines):
        if "input(" in line:
            input_found = True
            results["input"].append(
                (f"✔ input() found on line {i+1}", "success")
            )

    if not input_found:
        results["input"].append(
            ("⚠ No user input detected using input().", "warning")
        )

    # ============================
    # OUTPUT CHECK
    # ============================
    output_found = False
    for i, line in enumerate(lines):
        if "print(" in line:
            output_found = True
            results["output"].append(
                (f"✔ print() found on line {i+1}", "success")
            )

    if not output_found:
        results["output"].append(
            ("⚠ No output detected using print().", "warning")
        )

    return results


if st.button("Analyze My Code"):
    if not code_input.strip():
        st.warning("Please paste your code before analyzing.")
    else:
        results = analyze_code(code_input)

        for section, messages in results.items():
            with st.expander(section.capitalize(), expanded=True):
                for message, status in messages:
                    if status == "success":
                        st.success(message)
                    else:
                        st.warning(message)

        st.markdown("---")
        st.info("This tool checks structural components only. It does not guarantee a College Board score.")
