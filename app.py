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

    # ------------------------
    # PROCEDURE CHECK
    # ------------------------
    function_match = re.search(r"def\s+(\w+)\((.*?)\):", code)

    if function_match:
        function_name = function_match.group(1)
        parameters = function_match.group(2).strip()

        results["procedure"].append(("✔ Procedure detected", "success"))

        if parameters:
            results["procedure"].append(("✔ Parameter detected", "success"))
            param_name = parameters.split(",")[0].strip()

            # Extract function body
            function_start = None
            for i, line in enumerate(lines):
                if f"def {function_name}" in line:
                    function_start = i
                    break

            if function_start is not None:
                indent_level = len(lines[function_start]) - len(lines[function_start].lstrip())
                function_body = []
                for line in lines[function_start + 1:]:
                    if line.strip() == "":
                        continue
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent > indent_level:
                        function_body.append(line)
                    else:
                        break

                if param_name and not any(param_name in line for line in function_body):
                    results["procedure"].append(("⚠ Parameter is not used inside the procedure. The parameter must affect the algorithm.", "warning"))
                else:
                    results["procedure"].append(("✔ Parameter is used inside the procedure", "success"))

                # Algorithm checks
                has_if = any("if " in line for line in function_body)
                has_loop = any("for " in line or "while " in line for line in function_body)

                if has_if:
                    results["algorithm"].append(("✔ Selection (if/else) detected inside procedure", "success"))
                else:
                    results["algorithm"].append(("⚠ No selection detected inside procedure. Your algorithm must include an if/else structure.", "warning"))

                if has_loop:
                    results["algorithm"].append(("✔ Iteration (loop) detected inside procedure", "success"))
                else:
                    results["algorithm"].append(("⚠ No iteration detected inside procedure. Your algorithm must include a loop.", "warning"))

        else:
            results["procedure"].append(("⚠ Procedure has no parameter. You must include at least one parameter.", "warning"))

        # Check if procedure is called
        call_pattern = rf"{function_name}\("
        call_matches = re.findall(call_pattern, code)
        if len(call_matches) > 1:
            results["procedure"].append(("✔ Procedure is called in the program", "success"))
        else:
            results["procedure"].append(("⚠ Procedure is defined but not called.", "warning"))

    else:
        results["procedure"].append(("⚠ No procedure detected. You must define a function using 'def'.", "warning"))

    # ------------------------
    # LIST CHECK
    # ------------------------
    list_match = re.search(r"\w+\s*=\s*\[.*?\]", code)

    if list_match:
        results["list"].append(("✔ List detected", "success"))

        list_var = list_match.group().split("=")[0].strip()
        list_elements = list_match.group()

        if list_elements.count(",") < 1:
            results["list"].append(("⚠ List appears to contain only one item. Lists should manage multiple related values.", "warning"))

        if list_var + "[" in code or f"for " in code and list_var in code:
            results["list"].append(("✔ List appears to be used in the program", "success"))
        else:
            results["list"].append(("⚠ List is declared but does not appear to be used.", "warning"))
    else:
        results["list"].append(("⚠ No list detected. You must use a list to manage complexity.", "warning"))

    # ------------------------
    # INPUT CHECK
    # ------------------------
    input_match = re.search(r"(\w+)\s*=\s*input\(", code)

    if input_match:
        input_var = input_match.group(1)
        results["input"].append(("✔ Input detected", "success"))

        if code.count(input_var) > 1:
            results["input"].append(("✔ Input appears to affect program behavior", "success"))
        else:
            results["input"].append(("⚠ Input is collected but does not appear to impact logic.", "warning"))
    else:
        results["input"].append(("⚠ No user input detected using input().", "warning"))

    # ------------------------
    # OUTPUT CHECK
    # ------------------------
    if "print(" in code:
        results["output"].append(("✔ Output detected using print()", "success"))
    else:
        results["output"].append(("⚠ No output detected using print().", "warning"))

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
