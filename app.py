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

    # ==================================================
    # PROCEDURE + ALGORITHM CHECK
    # ==================================================
    functions = re.findall(r"def\s+(\w+)\((.*?)\):", code)

    selected_function = None

    # Choose first function that has at least one parameter
    for name, params in functions:
        if params.strip():
            selected_function = (name, params)
            break

    if selected_function:
        function_name, parameters = selected_function
        results["procedure"].append(
            (f"✔ Procedure detected: {function_name}", "success")
        )

        param_name = parameters.split(",")[0].strip()

        # Extract function body using indentation
        function_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith(f"def {function_name}"):
                function_start = i
                break

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

        # Parameter usage
        if any(param_name in line for line in function_body):
            results["procedure"].append(
                ("✔ Parameter is used inside the procedure", "success")
            )
        else:
            results["procedure"].append(
                ("⚠ Parameter is not used inside the procedure. The parameter must affect the algorithm.", "warning")
            )

        # Check if procedure is called
        call_pattern = rf"{function_name}\("
        call_count = len(re.findall(call_pattern, code))

        if call_count > 1:
            results["procedure"].append(
                ("✔ Procedure is called in the program", "success")
            )
        else:
            results["procedure"].append(
                ("⚠ Procedure is defined but not called.", "warning")
            )

        # Algorithm checks (must be inside same procedure)
        has_if = any("if " in line for line in function_body)
        has_loop = any("for " in line or "while " in line for line in function_body)

        if has_if:
            results["algorithm"].append(
                ("✔ Selection (if/elif/else) detected inside procedure", "success")
            )
        else:
            results["algorithm"].append(
                ("⚠ No selection detected inside procedure. Your algorithm must include an if/else structure.", "warning")
            )

        if has_loop:
            results["algorithm"].append(
                ("✔ Iteration (for/while) detected inside procedure", "success")
            )
        else:
            results["algorithm"].append(
                ("⚠ No iteration detected inside procedure. Your algorithm must include a loop.", "warning")
            )

    else:
        results["procedure"].append(
            ("⚠ No valid procedure with at least one parameter detected.", "warning")
        )

    # ==================================================
    # LIST CHECK
    # ==================================================
    list_match = re.search(r"(\w+)\s*=\s*\[.*?\]", code)

    if list_match:
        results["list"].append(("✔ List detected", "success"))

        list_var = list_match.group(1)
        list_text = list_match.group()

        if list_text.count(",") < 1:
            results["list"].append(
                ("⚠ List appears to contain only one item. Lists should manage multiple related values.", "warning")
            )

        if list_var + "[" in code or f"for " in code and list_var in code:
            results["list"].append(
                ("✔ List appears to be used in the program", "success")
            )
        else:
            results["list"].append(
                ("⚠ List is declared but does not appear to be used.", "warning")
            )

    else:
        results["list"].append(
            ("⚠ No list detected. You must use a list to manage complexity.", "warning")
        )

    # ==================================================
    # INPUT CHECK
    # ==================================================
    if "input(" in code:
        results["input"].append(
            ("✔ User input detected using input()", "success")
        )
    else:
        results["input"].append(
            ("⚠ No user input detected using input().", "warning")
        )

    # ==================================================
    # OUTPUT CHECK
    # ==================================================
    if "print(" in code:
        results["output"].append(
            ("✔ Output detected using print()", "success")
        )
    else:
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
