# enhanced_chatbot_logic.py
import pandas as pd
import re
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

class EnhancedBajajChatbot:
    def __init__(self, vector_store, api_key, stock_data_path=None):
        self.vector_store = vector_store
        self.api_key = api_key
        self.stock_data = None
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=api_key, 
            temperature=0.1
        )
        
        # Load stock data if available
        if stock_data_path:
            try:
                self.stock_data = pd.read_csv(stock_data_path)
                # Handle the date format in the CSV (e.g., "3-Jan-22")
                self.stock_data['Date'] = pd.to_datetime(self.stock_data['Date'], format='%d-%b-%y')
                print(f"Loaded stock data with {len(self.stock_data)} records")
                print(f"Date range: {self.stock_data['Date'].min()} to {self.stock_data['Date'].max()}")
            except Exception as e:
                print(f"Error loading stock data: {e}")
                # Try alternative date parsing
                try:
                    self.stock_data = pd.read_csv(stock_data_path)
                    self.stock_data['Date'] = pd.to_datetime(self.stock_data['Date'])
                    print(f"Loaded stock data with {len(self.stock_data)} records (alternative parsing)")
                    print(f"Date range: {self.stock_data['Date'].min()} to {self.stock_data['Date'].max()}")
                except Exception as e2:
                    print(f"Failed to load stock data: {e2}")
    
    def classify_query(self, question):
        """Classify the type of query to apply appropriate handling."""
        question_lower = question.lower()
        
        # Stock price queries
        if any(word in question_lower for word in ['stock price', 'share price', 'highest', 'lowest', 'average', 'price', '2022', '2023', '2024', '2025', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
            if any(word in question_lower for word in ['compare', 'comparison', 'vs', 'versus']):
                return 'stock_comparison'
            else:
                return 'stock_price'
        
        # Financial analysis queries
        elif any(word in question_lower for word in ['cfo', 'commentary', 'investor call', 'financial performance']):
            return 'financial_analysis'
        
        # Business insight queries
        elif any(word in question_lower for word in ['headwinds', 'partnership', 'rationale', 'organic traffic', 'stake sale']):
            return 'business_insights'
        
        # Comparison queries
        elif any(word in question_lower for word in ['compare', 'comparison', 'vs', 'versus']):
            return 'comparison'
        
        else:
            return 'general'
    
    def extract_date_range(self, question):
        """Extract date ranges from questions."""
        # Patterns for date extraction
        patterns = [
            r'(\d{4})',  # Year
            r'(\w{3}-\d{2})',  # MMM-YY format
            r'(\d{1,2}-\w{3}-\d{2})',  # DD-MMM-YY format
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, question)
            dates.extend(matches)
        
        # Also extract month names
        month_patterns = [
            r'january|jan', r'february|feb', r'march|mar', r'april|apr',
            r'may', r'june|jun', r'july|jul', r'august|aug',
            r'september|sep', r'october|oct', r'november|nov', r'december|dec'
        ]
        
        month_map = {
            'january': 'jan', 'jan': 'jan', 'february': 'feb', 'feb': 'feb',
            'march': 'mar', 'mar': 'mar', 'april': 'apr', 'apr': 'apr',
            'may': 'may', 'june': 'jun', 'jun': 'jun', 'july': 'jul', 'jul': 'jul',
            'august': 'aug', 'aug': 'aug', 'september': 'sep', 'sep': 'sep',
            'october': 'oct', 'oct': 'oct', 'november': 'nov', 'nov': 'nov',
            'december': 'dec', 'dec': 'dec'
        }
        
        for pattern in month_patterns:
            matches = re.findall(pattern, question.lower())
            for match in matches:
                if match in month_map:
                    dates.append(month_map[match])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_dates = []
        for date in dates:
            if date not in seen:
                seen.add(date)
                unique_dates.append(date)
        
        print(f"Extracted dates from question: {unique_dates}")
        return unique_dates
    
    def get_stock_price_data(self, question):
        """Extract relevant stock price data based on the question."""
        if self.stock_data is None:
            return "Stock price data not available."
        
        dates = self.extract_date_range(question)
        question_lower = question.lower()
        
        if not dates:
            return "No specific date range found in the question."
        
        try:
            # Filter data based on extracted dates
            filtered_data = self.stock_data.copy()
            
            # If year is mentioned, filter by year
            years = [d for d in dates if len(d) == 4]
            if years:
                year = int(years[0])
                filtered_data = filtered_data[filtered_data['Date'].dt.year == year]
                print(f"Filtering data for year: {year}")
            
            # If month is mentioned, filter by month
            months = []
            for date in dates:
                if len(date) == 3 and '-' in date:  # MMM-YY format
                    try:
                        month_str = date.split('-')[0]
                        month_map = {
                            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                        }
                        if month_str.lower() in month_map:
                            months.append(month_map[month_str.lower()])
                    except:
                        pass
            
            if months:
                filtered_data = filtered_data[filtered_data['Date'].dt.month.isin(months)]
                print(f"Filtering data for months: {months}")
            
            if filtered_data.empty:
                available_years = sorted(self.stock_data['Date'].dt.year.unique())
                return f"No stock data available for the specified period. Available data: {available_years}"
            
            # Calculate statistics
            highest = filtered_data['Close Price'].max()
            lowest = filtered_data['Close Price'].min()
            average = filtered_data['Close Price'].mean()
            
            # Get date range for context
            start_date = filtered_data['Date'].min().strftime('%Y-%m-%d')
            end_date = filtered_data['Date'].max().strftime('%Y-%m-%d')
            
            # Format response based on question type
            if 'highest' in question_lower:
                return f"📈 Highest stock price: ₹{highest:.2f} (Period: {start_date} to {end_date})"
            elif 'lowest' in question_lower:
                return f"📉 Lowest stock price: ₹{lowest:.2f} (Period: {start_date} to {end_date})"
            elif 'average' in question_lower:
                return f"📊 Average stock price: ₹{average:.2f} (Period: {start_date} to {end_date})"
            else:
                return f"📈 Stock Price Statistics (Period: {start_date} to {end_date}):\n- Highest: ₹{highest:.2f}\n- Lowest: ₹{lowest:.2f}\n- Average: ₹{average:.2f}"
                
        except Exception as e:
            return f"Error processing stock data: {str(e)}"
    
    def build_enhanced_prompt(self, query_type):
        """Build enhanced prompts based on query type."""
        
        base_prompt = """
        You are an expert financial analyst and chatbot for Bajaj Finserv. 
        Your role is to provide accurate, detailed, and professional responses based on the provided context.
        
        IMPORTANT GUIDELINES:
        1. Always base your answers on the provided context
        2. Be specific and quantitative when possible
        3. Use professional financial terminology
        4. Structure your responses clearly with bullet points or sections
        5. If information is not available in the context, clearly state this
        """
        
        if query_type == 'stock_price':
            prompt = base_prompt + """
            
            For stock price queries:
            - Provide specific numerical values with proper formatting (₹ symbol)
            - Include date ranges when relevant
            - If calculating averages, explain the methodology
            - Present data in a structured format
            """
        
        elif query_type == 'financial_analysis':
            prompt = base_prompt + """
            
            For financial analysis and CFO commentary:
            - Focus on key financial metrics (revenue, profit, growth rates)
            - Highlight strategic initiatives and their impact
            - Discuss market position and competitive advantages
            - Address risks and opportunities
            - Use professional financial language
            - Structure as a formal investor communication
            """
        
        elif query_type == 'business_insights':
            prompt = base_prompt + """
            
            For business insights and strategic questions:
            - Provide detailed analysis of business drivers
            - Explain strategic rationale behind decisions
            - Discuss market conditions and their impact
            - Address challenges and mitigation strategies
            - Include relevant financial implications
            """
        
        elif query_type == 'comparison':
            prompt = base_prompt + """
            
            For comparison queries:
            - Present data in a side-by-side format
            - Highlight key differences and similarities
            - Provide percentage changes where relevant
            - Explain the significance of the comparison
            - Use tables or structured format for clarity
            """
        
        else:
            prompt = base_prompt + """
            
            For general queries:
            - Provide comprehensive but concise answers
            - Include relevant context and background
            - Structure information logically
            - Highlight key takeaways
            """
        
        prompt += """
        
        Context: {context}
        Question: {question}
        
        Answer:"""
        
        return PromptTemplate(template=prompt, input_variables=["context", "question"])
    
    def build_rag_chain(self, query_type):
        """Build RAG chain with enhanced retrieval."""
        prompt = self.build_enhanced_prompt(query_type)
        
        # Enhanced retriever with more context
        retriever = self.vector_store.as_retriever(
            search_kwargs={
                "k": 5  # Increased from 3 to 5
            }
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        
        return qa_chain
    
    def answer_question(self, question):
        """Enhanced question answering with query classification and specialized handling."""
        try:
            # Classify the query
            query_type = self.classify_query(question)
            print(f"Query classified as: {query_type}")
            
            # Handle stock price queries with structured data
            if query_type in ['stock_price', 'stock_comparison']:
                stock_response = self.get_stock_price_data(question)
                if "Stock price data not available" not in stock_response and "No specific date range" not in stock_response:
                    return stock_response, []
            
            # Build appropriate RAG chain
            rag_chain = self.build_rag_chain(query_type)
            
            # Get response
            response = rag_chain.invoke({"query": question})
            answer = response["result"]
            sources = response["source_documents"]
            
            # Post-process answer for better formatting
            answer = self.post_process_answer(answer, query_type)
            
            return answer, sources
            
        except Exception as e:
            print(f"Error answering question: {e}")
            return f"An error occurred while processing your question: {str(e)}. Please try rephrasing your question.", []

    def post_process_answer(self, answer, query_type):
        """Post-process the answer for better formatting and clarity."""
        # Remove excessive whitespace
        answer = re.sub(r'\n\s*\n', '\n\n', answer)
        
        # Add formatting for different query types
        if query_type == 'financial_analysis':
            if 'CFO' in answer or 'commentary' in answer.lower():
                answer = "📊 **CFO Commentary**\n\n" + answer
        
        elif query_type == 'stock_price':
            if '₹' in answer:
                answer = "📈 **Stock Price Analysis**\n\n" + answer
        
        elif query_type == 'business_insights':
            answer = "💼 **Business Insights**\n\n" + answer
        
        return answer

def build_enhanced_rag_chain(vector_store, api_key, stock_data_path=None):
    """Factory function to create enhanced chatbot."""
    return EnhancedBajajChatbot(vector_store, api_key, stock_data_path)

def answer_question_enhanced(chatbot, question):
    """Enhanced question answering function."""
    return chatbot.answer_question(question)

if __name__ == "__main__":
    # Test the enhanced chatbot
    from config import get_api_key
    from enhanced_data_loader import get_or_create_vector_database_enhanced
    import os

    DATA_FOLDER = "data"
    DB_FOLDER = "chroma_db"
    STOCK_DATA_PATH = os.path.join(DATA_FOLDER, "BFS_Share_Price.csv")

    api_key = get_api_key()
    if api_key:
        print("\n--- Testing Enhanced Chatbot ---")
        vectordb = get_or_create_vector_database_enhanced(DATA_FOLDER, DB_FOLDER, api_key, force_rebuild=False)
        
        if vectordb:
            chatbot = build_enhanced_rag_chain(vectordb, api_key, STOCK_DATA_PATH)
            
            test_questions = [
                "What was the average stock price of Bajaj Finserv in 2022?",
                "What was the highest stock price in 2023?",
                "Why is BAGIC facing headwinds in motor insurance business?",
                "Act as a CFO of BAGIC and help me draft commentary for upcoming investor call"
            ]
            
            for question in test_questions:
                print(f"\n{'='*50}")
                print(f"Question: {question}")
                answer, sources = answer_question_enhanced(chatbot, question)
                print(f"Answer: {answer}")
                print(f"Sources: {len(sources)} documents")
    else:
        print("API key not available for testing.") 