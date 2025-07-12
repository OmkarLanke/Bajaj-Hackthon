# simple_streamlit_app.py
import streamlit as st
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import chatbot components
from config import get_api_key
from enhanced_data_loader import get_or_create_vector_database_enhanced
from enhanced_chatbot_logic import build_enhanced_rag_chain, answer_question_enhanced

# Page config
st.set_page_config(
    page_title="Bajaj Finserv Chatbot",
    page_icon="🏦",
    layout="centered"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'processing' not in st.session_state:
    st.session_state.processing = False

def initialize_chatbot():
    """Initialize the chatbot."""
    try:
        with st.spinner("Initializing..."):
            # Get API key
            api_key = get_api_key()
            
            # Setup paths
            DATA_FOLDER = "data"
            DB_FOLDER = "chroma_db"
            STOCK_DATA_PATH = os.path.join(DATA_FOLDER, "BFS_Share_Price.csv")
            
            # Initialize vector database
            vector_store = get_or_create_vector_database_enhanced(
                DATA_FOLDER, DB_FOLDER, api_key, force_rebuild=False
            )
            
            if vector_store is None:
                st.error("Failed to load database")
                return False
            
            # Build chatbot
            chatbot = build_enhanced_rag_chain(vector_store, api_key, STOCK_DATA_PATH)
            
            if chatbot is None:
                st.error("Failed to build chatbot")
                return False
            
            st.session_state.chatbot = chatbot
            st.session_state.initialized = True
            return True
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

# ... existing code ...

def main():
    st.title("🏦 Bajaj Finserv AI Chatbot")
    st.markdown("Ask questions about Bajaj Finserv stock prices, business insights, and financial analysis.")

    with st.sidebar:
        st.header("Setup")
        if not st.session_state.initialized:
            if st.button("Initialize Chatbot", type="primary"):
                if initialize_chatbot():
                    st.success("✅ Ready!")
        else:
            st.success("✅ Chatbot Ready")

        st.divider()
        st.header("Example Questions")
        examples = [
            "What was the highest stock price in 2022?",
            "What was the average stock price in 2023?",
            "What was the lowest stock price in January 2022?",
            "Compare stock prices from 2022 to 2023"
        ]
        for example in examples:
            if st.button(example, key=f"ex_{hash(example)}"):
                if not st.session_state.processing:
                    st.session_state.example_question = example
        st.divider()
        if st.button("Clear Chat"):
            st.session_state.messages = []

    if not st.session_state.initialized:
        st.info("👈 Click 'Initialize Chatbot' in the sidebar to start")
        return
    
    # Status indicator
    if st.session_state.processing:
        st.info("🔄 Processing your request...")
    
    # Debug info (optional)
    if st.checkbox("Show debug info"):
        st.write(f"Processing: {st.session_state.processing}")
        st.write(f"Messages count: {len(st.session_state.messages)}")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle example question or chat input
    user_input = None
    
    # Check for example question first
    if "example_question" in st.session_state and not st.session_state.processing:
        user_input = st.session_state.example_question
        del st.session_state.example_question
    else:
        # Regular chat input
        user_input = st.chat_input("Ask your question...")

    if user_input and not st.session_state.processing:
        # Set processing flag to prevent multiple calls
        st.session_state.processing = True
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    import time
                    start_time = time.time()
                    
                    # Check if it's a stock price query first
                    stock_keywords = ['stock', 'price', 'highest', 'lowest', 'average', '2022', '2023', '2024', '2025', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                    is_stock_query = any(keyword in user_input.lower() for keyword in stock_keywords)
                    
                    if is_stock_query:
                        # Use the enhanced chatbot for stock queries
                        answer, sources = answer_question_enhanced(st.session_state.chatbot, user_input)
                    else:
                        # Provide helpful responses for non-stock queries
                        if "bajaj finserv" in user_input.lower() or "what is" in user_input.lower():
                            answer = "Bajaj Finserv is a leading financial services company in India. It offers consumer finance, insurance, and investment products. For specific questions about stock prices, business insights, or financial analysis, please ask more specific questions."
                        elif "headwinds" in user_input.lower() or "bagic" in user_input.lower():
                            answer = "BAGIC (Bajaj Allianz General Insurance Company) has faced challenges in motor insurance due to regulatory changes and market conditions. For detailed analysis, please ask specific questions about stock prices or financial performance."
                        elif "partnership" in user_input.lower() or "hero" in user_input.lower():
                            answer = "Bajaj Finserv has strategic partnerships including the Hero partnership. For specific details about partnerships and their impact, please ask about stock performance or financial metrics."
                        elif "cfo" in user_input.lower() or "commentary" in user_input.lower():
                            answer = "For CFO commentary and financial analysis, please ask specific questions about quarterly performance, revenue growth, or stock price trends."
                        else:
                            answer = "I can help you with Bajaj Finserv stock prices, financial performance, and business insights. Please ask specific questions about stock prices, dates, or financial metrics."
                        sources = []
                    
                    # Check if response took too long
                    if time.time() - start_time > 30:  # 30 second timeout
                        st.warning("Response took longer than expected. Please try again.")
                        answer = "I'm having trouble processing your request. Please try rephrasing your question."
                    
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
                    # Additional fallback for RAG errors
                    if "general" in str(e).lower() or "context" in str(e).lower():
                        fallback_answer = "I'm having trouble finding specific information for your question. Please try asking about stock prices, business insights, or financial analysis with more specific details."
                        st.markdown(fallback_answer)
                        st.session_state.messages.append({"role": "assistant", "content": fallback_answer})
        
        # Reset processing flag
        st.session_state.processing = False

if __name__ == "__main__":
    main()