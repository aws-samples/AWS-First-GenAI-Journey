import streamlit as st
from analyzer import analyze_template

SEVERITY_COLORS = {
    "CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵", "INFO": "⚪"
}

st.set_page_config(page_title="AWS Infrastructure Analyzer", page_icon="🔍", layout="wide")
st.title("🔍 AWS Infrastructure Analyzer")
st.markdown("Upload a CloudFormation (YAML/JSON) or Terraform (HCL) template to analyze for security issues, cost optimization, and best practices.")

uploaded_file = st.file_uploader(
    "Upload template file", type=["yaml", "yml", "json", "tf", "hcl"]
)

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    with st.expander("📄 Template Preview", expanded=False):
        st.code(content[:3000], language="yaml" if uploaded_file.name.endswith((".yaml", ".yml")) else "json")

    if st.button("🚀 Analyze Template", type="primary"):
        with st.spinner("Analyzing template with Amazon Bedrock..."):
            try:
                findings = analyze_template(content, uploaded_file.name)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                findings = []

        if findings:
            st.subheader(f"📋 Findings ({len(findings)})")

            severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
            for severity in severity_order:
                items = [f for f in findings if f.get("severity") == severity]
                if not items:
                    continue
                st.markdown(f"### {SEVERITY_COLORS.get(severity, '⚪')} {severity} ({len(items)})")
                for finding in items:
                    with st.expander(f"{finding.get('category', 'General')} - {finding.get('resource', 'N/A')}: {finding.get('issue', '')[:80]}"):
                        st.markdown(f"**Resource:** `{finding.get('resource', 'N/A')}`")
                        st.markdown(f"**Category:** {finding.get('category', 'N/A')}")
                        st.markdown(f"**Issue:** {finding.get('issue', 'N/A')}")
                        st.markdown(f"**Recommendation:** {finding.get('recommendation', 'N/A')}")

            # Summary metrics
            st.divider()
            cols = st.columns(5)
            for i, sev in enumerate(severity_order):
                count = len([f for f in findings if f.get("severity") == sev])
                cols[i].metric(f"{SEVERITY_COLORS[sev]} {sev}", count)
        else:
            st.success("✅ No issues found!")
