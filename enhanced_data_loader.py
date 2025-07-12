# enhanced_data_loader.py
import os
import PyPDF2
import csv
import pandas as pd
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

def load_documents_enhanced(folder_path):
    """
    Enhanced document loader that better handles different file types.
    """
    documents = []
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        
        if filename.endswith(".pdf"):
            try:
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page_num, page in enumerate(reader.pages):
                        page_text = page.extract_text() or ""
                        if page_text.strip():
                            # Add page number for better context
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    
                    if text.strip():
                        documents.append({
                            "content": text,
                            "source": filename,
                            "type": "pdf"
                        })
                        print(f"✅ Loaded PDF: {filename} ({len(text)} characters)")
            except Exception as e:
                print(f"❌ Error loading PDF {filename}: {e}")
                
        elif filename.endswith(".csv"):
            try:
                # Enhanced CSV processing for stock data
                df = pd.read_csv(filepath)
                
                if 'Date' in df.columns and 'Close Price' in df.columns:
                    # Process as stock price data
                    stock_summary = process_stock_data(df, filename)
                    documents.append({
                        "content": stock_summary,
                        "source": filename,
                        "type": "stock_data"
                    })
                    print(f"✅ Loaded stock data CSV: {filename} ({len(df)} records)")
                else:
                    # Process as general CSV
                    csv_content = df.to_string(index=False)
                    documents.append({
                        "content": csv_content,
                        "source": filename,
                        "type": "csv"
                    })
                    print(f"✅ Loaded CSV: {filename}")
                    
            except Exception as e:
                print(f"❌ Error loading CSV {filename}: {e}")
    
    return documents

def process_stock_data(df, filename):
    """
    Process stock price data into a more searchable format.
    """
    # Convert date column
    try:
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y')
    except:
        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except:
            pass
    
    # Create summary statistics by year
    yearly_stats = []
    for year in df['Date'].dt.year.unique():
        year_data = df[df['Date'].dt.year == year]
        stats = {
            'year': year,
            'highest': year_data['Close Price'].max(),
            'lowest': year_data['Close Price'].min(),
            'average': year_data['Close Price'].mean(),
            'records': len(year_data)
        }
        yearly_stats.append(stats)
    
    # Create searchable text
    summary_text = f"Bajaj Finserv Stock Price Data from {filename}\n\n"
    summary_text += "Yearly Statistics:\n"
    
    for stats in yearly_stats:
        summary_text += f"Year {stats['year']}:\n"
        summary_text += f"  - Highest Price: ₹{stats['highest']:.2f}\n"
        summary_text += f"  - Lowest Price: ₹{stats['lowest']:.2f}\n"
        summary_text += f"  - Average Price: ₹{stats['average']:.2f}\n"
        summary_text += f"  - Trading Days: {stats['records']}\n\n"
    
    # Add monthly breakdown for recent years
    recent_years = sorted(df['Date'].dt.year.unique())[-2:]  # Last 2 years
    for year in recent_years:
        year_data = df[df['Date'].dt.year == year]
        monthly_stats = year_data.groupby(year_data['Date'].dt.month).agg({
            'Close Price': ['max', 'min', 'mean']
        }).round(2)
        
        summary_text += f"Monthly Breakdown for {year}:\n"
        for month in monthly_stats.index:
            month_name = pd.Timestamp(year=year, month=month, day=1).strftime('%B')
            max_price = monthly_stats.loc[month, ('Close Price', 'max')]
            min_price = monthly_stats.loc[month, ('Close Price', 'min')]
            avg_price = monthly_stats.loc[month, ('Close Price', 'mean')]
            
            summary_text += f"  {month_name}: High ₹{max_price}, Low ₹{min_price}, Avg ₹{avg_price}\n"
        summary_text += "\n"
    
    return summary_text

def split_documents_enhanced(documents):
    """
    Enhanced document splitting with better metadata handling.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  # Increased for better context
        chunk_overlap=300,  # Increased overlap
        length_function=len,
        add_start_index=True,
    )
    
    all_chunks = []
    
    for doc in documents:
        chunks = text_splitter.split_text(doc["content"])
        
        for j, chunk in enumerate(chunks):
            metadata = {
                "source": doc["source"],
                "type": doc["type"],
                "chunk_id": j + 1,
                "total_chunks": len(chunks)
            }
            
            all_chunks.append({
                "page_content": chunk,
                "metadata": metadata
            })
    
    print(f"📊 Split {len(documents)} documents into {len(all_chunks)} chunks.")
    return all_chunks

def create_vector_database_enhanced(chunks, db_path, api_key):
    """
    Enhanced vector database creation with better error handling.
    """
    print("🔄 Creating enhanced vector database...")
    
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=api_key
        )

        # Convert chunks to LangChain Document objects
        langchain_documents = [
            Document(page_content=chunk["page_content"], metadata=chunk["metadata"])
            for chunk in chunks
        ]

        vectordb = Chroma.from_documents(
            documents=langchain_documents,
            embedding=embeddings,
            persist_directory=db_path
        )
        vectordb.persist()
        print(f"✅ Enhanced vector database created and persisted to {db_path}")
        return vectordb
        
    except Exception as e:
        print(f"❌ Error creating vector database: {e}")
        return None

def load_vector_database_enhanced(db_path, api_key):
    """
    Enhanced vector database loading.
    """
    print("🔄 Loading enhanced vector database...")
    
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=api_key
        )
        vectordb = Chroma(persist_directory=db_path, embedding_function=embeddings)
        print(f"✅ Enhanced vector database loaded from {db_path}")
        return vectordb
        
    except Exception as e:
        print(f"❌ Error loading vector database: {e}")
        return None

def get_or_create_vector_database_enhanced(data_folder, db_path, api_key, force_rebuild=False):
    """
    Enhanced function to get or create vector database.
    """
    if force_rebuild or not os.path.exists(db_path) or not os.listdir(db_path):
        print("🔄 Vector database not found or rebuild forced. Creating enhanced database...")
        documents = load_documents_enhanced(data_folder)
        
        if not documents:
            print("❌ No documents found to process. Please ensure data files are in the 'data' folder.")
            return None
            
        chunks = split_documents_enhanced(documents)
        vectordb = create_vector_database_enhanced(chunks, db_path, api_key)
    else:
        print("📁 Existing vector database found. Loading enhanced database...")
        vectordb = load_vector_database_enhanced(db_path, api_key)
    
    return vectordb

if __name__ == "__main__":
    # Test the enhanced data loader
    from config import get_api_key
    import os

    DATA_FOLDER = "data"
    DB_FOLDER = "chroma_db"
    os.makedirs(DATA_FOLDER, exist_ok=True)

    api_key = get_api_key()
    if api_key:
        print("\n--- Testing Enhanced Data Loader ---")
        vectordb = get_or_create_vector_database_enhanced(
            DATA_FOLDER, DB_FOLDER, api_key, force_rebuild=True
        )
        
        if vectordb:
            print("✅ Enhanced data loader test successful!")
        else:
            print("❌ Enhanced data loader test failed.")
    else:
        print("❌ API key not available for testing.") 