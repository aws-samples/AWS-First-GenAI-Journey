import streamlit as st

pg = st.navigation([
    st.Page("pages/home.py", title="Home", icon="🇻🇳"),
    st.Page("pages/document_summary.py", title="Tóm tắt tài liệu", icon="✍"),
    st.Page("pages/document_answer.py", title="Hỏi đáp về tài liệu", icon="🙋‍♀️"),
    st.Page("pages/stock_analytics.py", title="Phân tích kỹ thuật cổ phiếu", icon="🧑‍💻"),
    st.Page("pages/stock_advisor.py", title="Tra cứu thông tin chứng khoán", icon="🤠"),
    st.Page("pages/stock_agent.py", title="Trợ lý chứng khoán", icon="👨‍🏫"),
])
pg.run()
