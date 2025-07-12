# enhanced_main.py
import os
from config import get_api_key
from enhanced_data_loader import get_or_create_vector_database_enhanced
from enhanced_chatbot_logic import build_enhanced_rag_chain, answer_question_enhanced

# --- Configuration ---
DATA_FOLDER = "data"
DB_FOLDER = "chroma_db"
STOCK_DATA_PATH = os.path.join(DATA_FOLDER, "BFS_Share_Price.csv")

def main():
    print("🚀 Starting Enhanced Bajaj Finserv RAG Chatbot...")
    print("=" * 60)

    # Ensure data folder exists
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # 1. Load API Key
    try:
        api_key = get_api_key()
        print("✅ Google API Key loaded successfully.")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please set GOOGLE_API_KEY in your .env file.")
        return

    # 2. Data Loading & Vector Database Creation/Loading
    force_rebuild_db = False
    if not os.path.exists(DB_FOLDER) or not os.listdir(DB_FOLDER):
        print("📁 ChromaDB folder not found or empty. Forcing initial build.")
        force_rebuild_db = True

    print("🔄 Initializing enhanced vector database...")
    vector_store = get_or_create_vector_database_enhanced(
        DATA_FOLDER,
        DB_FOLDER,
        api_key,
        force_rebuild=force_rebuild_db
    )

    if vector_store is None:
        print("❌ Failed to initialize vector database. Exiting.")
        return

    # 3. Build Enhanced Chatbot
    print("🤖 Building enhanced chatbot...")
    chatbot = build_enhanced_rag_chain(vector_store, api_key, STOCK_DATA_PATH)

    print("\n" + "=" * 60)
    print("🎯 Enhanced Chatbot is ready!")
    print("💡 Example questions you can ask:")
    print("   • What was the highest stock price of Bajaj Finserv in 2022?")
    print("   • Compare Bajaj Finserv performance from 2022 to 2023")
    print("   • Why is BAGIC facing headwinds in motor insurance business?")
    print("   • What's the rationale of Hero partnership?")
    print("   • Act as a CFO of BAGIC and help me draft commentary")
    print("   • Give me table with dates explaining Allianz stake sale discussions")
    print("=" * 60)
    print("Type 'exit' to quit or 'help' for more examples.")

    # 4. Enhanced Question Answering Loop
    while True:
        try:
            user_question = input("\n🤔 Your Question: ").strip()
            
            if user_question.lower() == 'exit':
                print("👋 Exiting chatbot. Goodbye!")
                break
            
            if user_question.lower() == 'help':
                print_help_examples()
                continue
            
            if not user_question:
                print("⚠️  Please enter a question.")
                continue

            print("🔄 Processing your question...")
            answer, sources = answer_question_enhanced(chatbot, user_question)

            print("\n" + "📝" + "=" * 50)
            print("💬 ANSWER:")
            print("=" * 50)
            print(answer)
            print("=" * 50)

            if sources:
                print(f"\n📚 Sources ({len(sources)} documents):")
                for i, source in enumerate(sources[:3], 1):  # Show top 3 sources
                    source_id = source.metadata.get('source', 'Unknown Source')
                    content_preview = source.page_content[:150] + "..." if len(source.page_content) > 150 else source.page_content
                    print(f"  {i}. {source_id}")
                    print(f"     Preview: {content_preview}")
            else:
                print("\n📚 No specific sources found for this answer.")

        except KeyboardInterrupt:
            print("\n\n👋 Exiting chatbot. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error processing question: {e}")
            print("Please try rephrasing your question.")

def print_help_examples():
    """Print helpful examples for users."""
    print("\n" + "=" * 60)
    print("💡 EXAMPLE QUESTIONS BY CATEGORY:")
    print("=" * 60)
    
    examples = {
        "📈 Stock Price Queries": [
            "What was the highest stock price of Bajaj Finserv in 2022?",
            "What was the average stock price in 2023?",
            "What was the lowest stock price in January 2022?",
            "Compare stock prices from 2022 to 2023"
        ],
        "💼 Business Insights": [
            "Why is BAGIC facing headwinds in motor insurance business?",
            "What's the rationale of Hero partnership?",
            "Tell me about organic traffic of Bajaj Markets",
            "What are the discussions regarding Allianz stake sale?"
        ],
        "📊 Financial Analysis": [
            "Act as a CFO of BAGIC and help me draft commentary for upcoming investor call",
            "What are the key financial highlights from Q4 FY25?",
            "Compare Bajaj Finserv performance from Q1 to Q4 FY25"
        ],
        "🔍 General Queries": [
            "What products does Bajaj Finserv offer?",
            "What are the key strategic initiatives?",
            "How is the company performing in different business segments?"
        ]
    }
    
    for category, questions in examples.items():
        print(f"\n{category}:")
        for i, question in enumerate(questions, 1):
            print(f"  {i}. {question}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 