import streamlit as st
import json
import pandas as pd
import plotly.express as px
from io import BytesIO
import PIL.Image
import plotly.io as pio

# পেজ সেটআপ
st.set_page_config(page_title="তাপমাত্রার ডেটা", layout="wide")

# ভাষা নির্বাচন
language = st.sidebar.radio("ভাষা নির্বাচন করুন / Select Language", ["বাংলা", "English"])
def t(bangla, english): return bangla if language == "বাংলা" else english

st.title(t("🌡️ তাপমাত্রার JSON ডেটা ভিজুয়ালাইজার", "🌡️ Temperature JSON Data Visualizer"))

# ফাইল আপলোড
uploaded_file = st.file_uploader(t("📂 JSON ফাইল আপলোড করুন", "📂 Upload JSON File"), type=["json"])

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        df = pd.DataFrame(data["data"])
        df["time"] = pd.to_datetime(df["time"])

        st.success(t("✅ ডেটা আপলোড হয়েছে!", "✅ Data uploaded successfully!"))

        # Scroll সহ DataFrame
        st.dataframe(df, use_container_width=True, height=400)

        metrics = df.columns.drop("time").tolist()
        selected_metric = st.selectbox(t("📊 মেট্রিক নির্বাচন করুন", "📊 Select Metric"), metrics)

        # তারিখ নির্বাচন
        start_date = st.date_input(t("শুরুর তারিখ", "Start Date"), value=df["time"].min())
        end_date = st.date_input(t("শেষ তারিখ", "End Date"), value=df["time"].max())

        filtered_df = df[(df["time"] >= pd.to_datetime(start_date)) & (df["time"] <= pd.to_datetime(end_date))]

        st.subheader(t("📈 প্লট টাইপ:", "📈 Plot Type:"))
        col1, col2, col3 = st.columns(3)
        fig = None

        # ✅ উন্নত scrollbar ফাংশন
        def add_scrollbar(fig):
            if len(filtered_df) >= 100:
                fig.update_xaxes(
                    rangeslider_visible=True,
                    rangeslider_thickness=0.1,
                    rangeslider_bgcolor='rgba(200,200,200,0.3)',
                    rangeslider_bordercolor='gray',
                    rangeslider_borderwidth=1,
                )
            else:
                fig.update_xaxes(rangeslider_visible=False)

            fig.update_layout(
                dragmode='zoom',
                hovermode='x unified',
                xaxis=dict(fixedrange=False),
                yaxis=dict(fixedrange=False)
            )
            return fig

        # বার প্লট
        if col1.button(t("📊 বার প্লট", "📊 Bar Plot")):
            fig = px.bar(filtered_df, x="time", y=selected_metric, title=f"{selected_metric} - Bar Plot")
            fig = add_scrollbar(fig)
            st.plotly_chart(fig, use_container_width=True)

        # স্ক্যাটার প্লট
        if col2.button(t("🔸 স্ক্যাটার প্লট", "🔸 Scatter Plot")):
            fig = px.scatter(filtered_df, x="time", y=selected_metric, title=f"{selected_metric} - Scatter Plot")
            fig = add_scrollbar(fig)
            st.plotly_chart(fig, use_container_width=True)

        # লাইন প্লট
        if col3.button(t("📈 লাইন প্লট", "📈 Line Plot")):
            fig = px.line(filtered_df, x="time", y=selected_metric, title=f"{selected_metric} - Line Plot")
            fig = add_scrollbar(fig)
            st.plotly_chart(fig, use_container_width=True)

        # প্লট প্রিভিউ ও ডাউনলোড
        if fig:
            img_bytes = fig.to_image(format="png", engine="kaleido")  # kaleido ইঞ্জিন
            image = PIL.Image.open(BytesIO(img_bytes))


            # ডাউনলোড বাটন
            st.download_button(
                label=t("⬇️ প্লট ডাউনলোড করুন", "⬇️ Download Plot"),
                data=img_bytes,
                file_name=f"{selected_metric}_plot.png",
                mime="image/png"
            )

    except Exception as e:
        st.error(t(f"❌ ডেটা পড়ার সমস্যা হয়েছে: {e}", f"❌ Error reading data: {e}"))

else:
    st.info(t("👆 উপরে JSON ফাইল আপলোড করুন।", "👆 Upload a JSON file above."))
