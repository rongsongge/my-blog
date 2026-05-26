import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests

# ===================== 从 secrets 读取配置 =====================
# 本地在 .streamlit/secrets.toml 里配置，云端在 Streamlit 后台配置
FEISHU_APP_ID = st.secrets["feishu"]["app_id"]
FEISHU_APP_SECRET = st.secrets["feishu"]["app_secret"]
FEISHU_APP_TOKEN = st.secrets["feishu"]["app_token"]
FEISHU_TABLE_ID = st.secrets["feishu"]["table_id"]

ADMIN_PWD = "82704001"

st.set_page_config(
    page_title="个人学习感悟随笔",
    layout="wide",
    initial_sidebar_state="auto",
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
.stContainer { border-radius: 16px !important; }
.stButton button { border-radius: 8px !important; font-weight: 500 !important; }
.blank-tip { text-align: center; padding: 40px 0; font-size: 16px; color: #666; }
</style>
""", unsafe_allow_html=True)

# ===================== 飞书多维表格 API =====================
def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    res = requests.post(url, json=data)
    return res.json().get("tenant_access_token", "")

def add_record(title, date, content):
    token = get_feishu_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "fields": {
            "标题": title,
            "日期": date,
            "内容": content
        }
    }
    requests.post(url, json=data, headers=headers)

def get_all_articles():
    token = get_feishu_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records?page_size=500"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    items = res.json().get("data", {}).get("items", [])
    articles = []
    for item in items:
        f = item["fields"]
        articles.append({
            "title": f.get("标题", ""),
            "date": f.get("日期", ""),
            "content": f.get("内容", ""),
            "id": item["id"]
        })
    return articles

def update_record(record_id, title, date, content):
    token = get_feishu_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "fields": {
            "标题": title,
            "日期": date,
            "内容": content
        }
    }
    requests.put(url, json=data, headers=headers)

def delete_record(record_id):
    token = get_feishu_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}"}
    requests.delete(url, headers=headers)

# ===================== 页面功能 =====================
articles = get_all_articles()

st.title("📖 个人学习感悟随笔")
st.caption("✅ 数据存在飞书多维表格 · 永久不丢失")
st.divider()

# ===================== 侧边栏 =====================
with st.sidebar:
    st.header("🔐 管理员中心")
    if not st.session_state.is_admin:
        pwd = st.text_input("密码", type="password")
        if st.button("登录", use_container_width=True):
            if pwd == ADMIN_PWD:
                st.session_state.is_admin = True
                st.rerun()
    else:
        st.success("已登录")
        if st.button("退出"):
            st.session_state.is_admin = False
            st.rerun()

        st.divider()
        st.subheader("✏️ 发布文章")
        t = st.text_input("标题")
        c = st.text_area("内容", height=200)
        if st.button("发布", type="primary", use_container_width=True):
            if t and c:
                add_record(t, datetime.now().strftime("%Y-%m-%d"), c)
                st.success("发布成功！已存到飞书多维表格")
                st.rerun()

# ===================== 文章列表 =====================
for idx, art in enumerate(articles):
    with st.container(border=True):
        st.subheader(art["title"])
        st.caption(art["date"])
        st.write(art["content"])

        if st.session_state.is_admin:
            cols = st.columns(2)
            with cols[0]:
                if st.button("修改", key=f"e{idx}"):
                    st.session_state.edit_idx = idx
            with cols[1]:
                if st.button("删除", key=f"d{idx}"):
                    delete_record(art["id"])
                    st.rerun()

# 修改面板
if st.session_state.is_admin and st.session_state.edit_idx is not None:
    idx = st.session_state.edit_idx
    a = articles[idx]
    st.subheader("修改文章")
    t = st.text_input("标题", a["title"])
    c = st.text_area("内容", a["content"])
    if st.button("保存修改"):
        update_record(a["id"], t, a["date"], c)
        st.session_state.edit_idx = None
        st.rerun()