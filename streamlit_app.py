import streamlit as st
import requests

st.set_page_config(page_title="GCP Multi-Agent Assistant", page_icon="🧠")

st.title("🧠 GCP Multi-Agent Assistant")
st.markdown(
    "Use this assistant to design architectures, get GCP service advice, or manage resources like buckets and Firestore databases."
)

# Text input prompt to drive agent decision
prompt = st.text_area(
    "What do you want to do?",
    placeholder=(
        "Examples:\n"
        "- Recommend GCP services for a scalable e-commerce platform.\n"
        "- Design a GCP architecture for a video analytics pipeline.\n"
        "- Create a new storage bucket called 'my-app-data' in us-central1.\n"
        "- Delete a Firestore database named 'test-db'."
    ),
    height=200
)

if st.button("Run Agent 🚀"):
    if not prompt.strip():
        st.warning("Please enter a task or goal.")
    else:
        payload = {"prompt": prompt}
        try:
            response = requests.post("http://localhost:8001/run", json=payload)

            if response.ok:
                data = response.json()

                results = data.get("results", {})

                if not results:
                    st.warning("No responses received from agents.")
                else:
                    for agent_name, agent_data in results.items():
                        st.subheader(f"🧑‍💻 Response from {agent_name}")
                        if isinstance(agent_data, dict):
                            content = agent_data.get("response") or agent_data.get("error") or str(agent_data)
                            st.markdown(content)
                        else:
                            st.markdown(str(agent_data))

            else:
                st.error("⚠️ Agent call failed. Please check the backend is running.")
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
