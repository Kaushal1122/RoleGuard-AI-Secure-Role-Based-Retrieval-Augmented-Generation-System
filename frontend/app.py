import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Company Internal Chatbot",
    layout="wide"
)

# ---------------- Session State ----------------
if "token" not in st.session_state:
    st.session_state.token = None


# ================= LOGIN UI =================
if st.session_state.token is None:
    st.title("🔐 Company Internal Chatbot")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            with st.spinner("Connecting to backend, please wait..."):
                response = requests.post(
                    f"{API_URL}/login",
                    data={
                        "username": username,
                        "password": password
                    },
                    timeout=25
                )

        except requests.exceptions.ReadTimeout:
            st.error("⏳ Backend is still starting. Please wait a few seconds and try again.")
            st.stop()

        except requests.exceptions.ConnectionError:
            st.error("❌ Backend server is not running. Please start the backend.")
            st.stop()

        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


# ================= LOGGED-IN STATE =================
else:
    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    # -------- Fetch user info safely --------
    try:
        response = requests.get(
            f"{API_URL}/me",
            headers=headers,
            timeout=25
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        st.error("❌ Backend not responding. Please refresh.")
        st.stop()

    if response.status_code != 200:
        st.error("Authentication failed. Please login again.")
        st.session_state.token = None
        st.stop()

    user = response.json()

    # ---------------- Sidebar ----------------
    st.sidebar.title("👤 User Info")
    st.sidebar.write(f"**Username:** {user['username']}")
    st.sidebar.write(f"**Role:** {user['role']}")

    # 🔹 STEP 13: Logout (SAFE)
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.success("Logged out successfully")
        st.stop()

    # ---------------- Main Chat UI ----------------
    st.title("💬 Company Internal Chatbot")

    query = st.text_input("Ask a question related to company documents")

    if st.button("Ask") and query.strip():
        try:
            with st.spinner("Processing your query..."):
                chat_response = requests.post(
                    f"{API_URL}/chat",
                    json={"query": query},
                    headers=headers,
                    timeout=35
                )

        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            st.error("❌ Backend is busy processing your request. Please try again.")
            st.stop()

        # 🔹 STEP 12: Handle RBAC errors
        if chat_response.status_code == 403:
            st.error("🚫 You are not authorized to access this information.")

        elif chat_response.status_code == 200:
            data = chat_response.json()

            # Answer
            st.markdown("### 🧠 Answer")
            if data.get("answer"):
                st.write(data["answer"])
            else:
                st.warning("No direct answer generated.")

            # Confidence
            st.markdown(f"**Confidence Score:** {data.get('confidence', 0.0)}")

            # Sources
            st.markdown("### 📚 Source Documents")
            if data.get("sources"):
                for src in data["sources"]:
                    st.write("-", src)
            else:
                st.write("No sources returned.")

        else:
            st.error("Something went wrong while processing your request.")


