import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="তাপমাত্রার ডেটা / Temperature Data", layout="wide")

language = st.sidebar.radio("ভাষা নির্বাচন করুন / Select Language", ["বাংলা", "English"])

def t(bangla_text, english_text):
    return bangla_text if language == "বাংলা" else english_text

st.title(t("🌡️ তাপমাত্রার JSON ডেটা ভিজুয়ালাইজার", "🌡️ Temperature JSON Data Visualizer"))

uploaded_file = st.file_uploader(t("📂 JSON ফাইল আপলোড করুন", "📂 Upload JSON File"), type=["json"])

# প্লট সবসময় এই সাইজের হবে
def get_fig_size(num_points):
    return (12, 5)

scroll_style = """
<style>
.scroll-div {
    overflow-x: auto;
    white-space: nowrap;
    border: 1px solid #ccc;
    padding: 5px;
}
</style>
"""

st.markdown(scroll_style, unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        df = pd.DataFrame(data["data"])
        df['time'] = pd.to_datetime(df['time'])

        st.success(t("✅ ডেটা আপলোড হয়েছে!", "✅ Data uploaded successfully!"))
        st.dataframe(df, use_container_width=True)

        metrics = df.columns.drop('time').tolist()
        selected_metric = st.selectbox(t("মেট্রিক নির্বাচন করুন", "Select Metric"), metrics)

        start_date = st.date_input(t("শুরু তারিখ", "Start Date"), value=df['time'].min())
        end_date = st.date_input(t("শেষ তারিখ", "End Date"), value=df['time'].max())

        filtered_df = df[(df['time'] >= pd.to_datetime(start_date)) & (df['time'] <= pd.to_datetime(end_date))]

        st.subheader(t("📈 প্লট টাইপ নির্বাচন করুন:", "📈 Select Plot Type:"))
        plot_placeholder = st.empty()
        col1, col2, col3 = st.columns(3)

        fig = None  # প্লট সংরক্ষণের জন্য

        if col1.button(t("📊 বার প্লট", "📊 Bar Plot")):
            fig, ax = plt.subplots(figsize=get_fig_size(len(filtered_df)))
            ax.bar(filtered_df['time'], filtered_df[selected_metric], width=0.02)
            ax.set_title(t(f"{selected_metric} (বার প্লট)", f"{selected_metric} (Bar Plot)"))
            ax.set_xlabel(t("সময়", "Time"))
            ax.set_ylabel(selected_metric)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            with plot_placeholder.container():
                st.markdown('<div class="scroll-div">', unsafe_allow_html=True)
                st.pyplot(fig)
                st.markdown('</div>', unsafe_allow_html=True)

        if col2.button(t("🔸 স্ক্যাটার প্লট", "🔸 Scatter Plot")):
            fig, ax = plt.subplots(figsize=get_fig_size(len(filtered_df)))
            ax.scatter(filtered_df['time'], filtered_df[selected_metric], color='red', s=50, alpha=0.7)
            ax.set_title(t(f"{selected_metric} (স্ক্যাটার প্লট)", f"{selected_metric} (Scatter Plot)"))
            ax.set_xlabel(t("সময়", "Time"))
            ax.set_ylabel(selected_metric)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            with plot_placeholder.container():
                st.markdown('<div class="scroll-div">', unsafe_allow_html=True)
                st.pyplot(fig)
                st.markdown('</div>', unsafe_allow_html=True)

        if col3.button(t("📈 লাইন প্লট", "📈 Line Plot")):
            fig, ax = plt.subplots(figsize=get_fig_size(len(filtered_df)))
            ax.plot(filtered_df['time'], filtered_df[selected_metric], color='green', marker='o')
            ax.set_title(t(f"{selected_metric} (লাইন প্লট)", f"{selected_metric} (Line Plot)"))
            ax.set_xlabel(t("সময়", "Time"))
            ax.set_ylabel(selected_metric)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            with plot_placeholder.container():
                st.markdown('<div class="scroll-div">', unsafe_allow_html=True)
                st.pyplot(fig)
                st.markdown('</div>', unsafe_allow_html=True)

        # যদি প্লট তৈরি হয়, তাহলে ডাউনলোড বাটন দেখাও
        if fig is not None:
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            buf.seek(0)

            st.download_button(
                label=t("⬇️ প্লট ডাউনলোড করুন", "⬇️ Download Plot"),
                data=buf,
                file_name=f"{selected_metric}_plot.png",
                mime="image/png"
            )

    except Exception as e:
        st.error(t(f"❌ ডেটা পড়ার সমস্যা হয়েছে: {e}", f"❌ Error reading data: {e}"))
else:
    st.info(t("👆 উপরে JSON ফাইল আপলোড করুন।", "👆 Upload a JSON file above."))
