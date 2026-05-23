import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import io

# ===================== 配置区【可自行修改】=====================
ADMIN_PWD = "82704001"
SAVE_FILE = "blog_data.json"
# ============================================================

st.set_page_config(
    page_title="个人学习感悟随笔",
    layout="wide",
    initial_sidebar_state="auto"
)

# 初始化状态
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None
if "del_confirm" not in st.session_state:
    st.session_state.del_confirm = None

# 样式美化
st.markdown("""
<style>
.stContainer {
    border-radius: 16px !important;
}
.stButton button {
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.blank-tip {
    text-align: center;
    padding: 40px 0;
    font-size: 16px;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

# ===================== 数据功能 =====================
def init_data():
    if not os.path.exists(SAVE_FILE):
        default_data = [
            {
                "title": "我的云端学习博客上线啦",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "content": "这是使用 Streamlit 搭建的在线随笔博客，支持新增、修改、删除文章，数据云端保存。"
            }
        ]
        save_data(default_data)

def load_data():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_excel(data):
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    return buffer

init_data()
articles = load_data()

# ===================== 页面头部 =====================
st.title("📖 个人学习感悟随笔")
st.caption("记录成长 · 沉淀思考 · 全局云端同步")
st.divider()

# ===================== 侧边栏 =====================
with st.sidebar:
    st.header("🔐 管理员中心")

    if not st.session_state.is_admin:
        pwd = st.text_input("请输入管理密码", type="password")
        if st.button("登录管理", use_container_width=True):
            if pwd == ADMIN_PWD:
                st.session_state.is_admin = True
                st.success("✅ 登录成功")
                st.rerun()
            else:
                st.error("❌ 密码错误")
    else:
        st.success("✅ 已登录管理员")
        if st.button("退出登录", use_container_width=True):
            st.session_state.is_admin = False
            st.session_state.edit_idx = None
            st.session_state.del_confirm = None
            st.rerun()

        st.divider()
        st.header("✏️ 发布新文章")
        new_title = st.text_input("文章标题")
        new_date = datetime.now().strftime("%Y-%m-%d")
        new_content = st.text_area("文章内容", height=200)

        if st.button("发布文章", type="primary", use_container_width=True):
            if new_title.strip() and new_content.strip():
                articles.insert(0, {
                    "title": new_title.strip(),
                    "date": new_date,
                    "content": new_content.strip()
                })
                save_data(articles)
                st.success("发布成功！")
                st.rerun()

        st.divider()
        st.header("📥 导出Excel")
        excel_data = export_excel(articles)
        st.download_button(
            "导出全部文章",
            data=excel_data,
            file_name="学习博客.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ===================== 修改面板 =====================
if st.session_state.is_admin and st.session_state.edit_idx is not None:
    st.subheader("✏️ 修改文章")
    idx = st.session_state.edit_idx
    art = articles[idx]

    edit_title = st.text_input("标题", value=art["title"])
    edit_date = st.text_input("日期", value=art["date"])
    edit_content = st.text_area("内容", value=art["content"], height=220)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 保存修改", type="primary", use_container_width=True):
            articles[idx] = {
                "title": edit_title.strip(),
                "date": edit_date.strip(),
                "content": edit_content.strip()
            }
            save_data(articles)
            st.session_state.edit_idx = None
            st.success("保存成功")
            st.rerun()
    with c2:
        if st.button("❌ 取消", use_container_width=True):
            st.session_state.edit_idx = None
            st.rerun()
    st.divider()

# ===================== 文章列表 =====================
if not articles:
    st.markdown("<div class='blank-tip'>暂无文章，快去发布第一篇吧！</div>", unsafe_allow_html=True)
else:
    for idx, art in enumerate(articles):
        with st.container(border=True):
            st.subheader(art["title"])
            st.caption(f"发布于：{art['date']}")
            st.write(art["content"])

            if st.session_state.is_admin:
                cols = st.columns(2)
                with cols[0]:
                    if st.button("✏️ 修改", key=f"edit_{idx}"):
                        st.session_state.edit_idx = idx
                        st.session_state.del_confirm = None
                        st.rerun()
                with cols[1]:
                    if st.button("🗑️ 删除", key=f"del_{idx}"):
                        st.session_state.del_confirm = idx
                        st.session_state.edit_idx = None
                        st.rerun()

            if st.session_state.del_confirm == idx:
                st.warning(f"确定删除「{art['title']}」吗？删除无法恢复！")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ 确认删除", key=f"ok_{idx}", type="primary"):
                        articles.pop(idx)
                        save_data(articles)
                        st.session_state.del_confirm = None
                        st.success("删除成功")
                        st.rerun()
                with c2:
                    if st.button("❌ 取消", key=f"can_{idx}"):
                        st.session_state.del_confirm = None
                        st.rerun()