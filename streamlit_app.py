# -------------------------------------------
# Sucuri-style scanner input bar
# -------------------------------------------
st.markdown(
    """
    <style>
    .scan-bar-container {
        display: flex;
        justify-content: center;
        margin-top: 10px;
        margin-bottom: 25px;
    }

    .scan-bar {
        display: flex;
        width: 90%;
        max-width: 900px;
        border: 2px solid #0b8f81;
        border-radius: 6px;
        overflow: hidden;
        background: white;
    }

    .scan-input {
        flex: 1;
        padding: 14px 18px;
        font-size: 18px;
        border: none;
        outline: none;
        color: #333;
    }

    .scan-input::placeholder {
        color: #999;
        font-size: 17px;
    }

    .scan-btn {
        background: #0b8f81;
        color: white;
        padding: 0 24px;
        font-size: 18px;
        font-weight: 600;
        border: none;
        cursor: pointer;
    }

    .scan-btn:hover {
        background: #0a7a6e;
    }
    </style>

    <div class="scan-bar-container">
        <div class="scan-bar">
            <input type="text" id="url_input" class="scan-input" placeholder="example.com">
            <button onclick="scanSite()" class="scan-btn">Scan Website</button>
        </div>
    </div>

    <script>
    function scanSite() {
        const inputElement = window.parent.document.querySelector('input[data-testid="stTextInput"]');
        const htmlInput = document.getElementById("url_input").value;
        inputElement.value = htmlInput;
        inputElement.dispatchEvent(new Event("input", { bubbles: true }));
        const button = window.parent.document.querySelector('button[kind="primary"]');
        button.click();
    }
    </script>
    """,
    unsafe_allow_html=True
)

# Streamlit invisible input field (syncs with JS above)
url = st.text_input("Enter URL", placeholder="https://example.com", label_visibility="collapsed")
