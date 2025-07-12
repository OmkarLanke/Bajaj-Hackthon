# 🏦 Bajaj Finserv AI Chatbot - Streamlit App

A modern, user-friendly web interface for the enhanced Bajaj Finserv AI chatbot built with Streamlit.

## 🚀 Features

- **Modern Web Interface**: Clean, responsive design with professional styling
- **Real-time Chat**: Interactive chat interface with message history
- **Smart Query Classification**: Automatic categorization of different question types
- **Enhanced Stock Analysis**: Direct processing of stock price data
- **Source Attribution**: View the sources used for each response
- **Example Questions**: Quick access to common queries
- **Error Handling**: Robust error handling and user feedback
- **Session Management**: Persistent chat history during the session

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key
- Bajaj Finserv data files

## 🛠️ Quick Setup

### 1. Install Dependencies
```bash
# Option 1: Use the setup script
python setup_streamlit.py

# Option 2: Manual installation
pip install -r requirements_streamlit.txt
```

### 2. Configure API Key
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 3. Prepare Data Files
Ensure your data files are in the `data/` folder:
- `BFS_Share_Price.csv` - Historical stock price data
- Quarterly earnings call transcripts (PDF files)

### 4. Run the App
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 🎯 Usage

### Initial Setup
1. **Initialize Chatbot**: Click the "🔄 Initialize Chatbot" button in the sidebar
2. **Wait for Setup**: The app will load the vector database and initialize the AI model
3. **Start Chatting**: Once initialized, you can start asking questions

### Asking Questions
- **Type your question** in the chat input box
- **Click example questions** in the sidebar for quick access
- **View sources** by expanding the "📚 Sources" section for each response

### Example Questions by Category

#### 📈 Stock Price Queries
- "What was the highest stock price of Bajaj Finserv in 2022?"
- "What was the average stock price in 2023?"
- "Compare stock prices from 2022 to 2023"

#### 💼 Business Insights
- "Why is BAGIC facing headwinds in motor insurance business?"
- "What's the rationale of Hero partnership?"
- "Tell me about organic traffic of Bajaj Markets"

#### 📊 Financial Analysis
- "Act as a CFO of BAGIC and help me draft commentary for upcoming investor call"
- "What are the key financial highlights from Q4 FY25?"

#### 🔍 General Queries
- "What products does Bajaj Finserv offer?"
- "What are the key strategic initiatives?"

## 🎨 Interface Features

### Main Chat Area
- **Real-time messaging** with user and bot messages clearly distinguished
- **Source attribution** showing which documents were used
- **Error handling** with clear error messages
- **Loading indicators** during processing

### Sidebar
- **Initialization button** to start the chatbot
- **Status indicators** showing chatbot readiness
- **Example questions** organized by category
- **Chat management** (clear history)
- **About section** with app information

### Quick Stats
- **Chat message count**
- **Available data information**
- **Recent activity** tracking

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit with custom CSS styling
- **Backend**: Enhanced chatbot with query classification
- **Data Processing**: Vector database with ChromaDB
- **AI Model**: Google Gemini 2.0 Flash

### Error Handling
- **API Key Validation**: Checks for valid Google API key
- **Data Validation**: Ensures required files exist
- **Network Errors**: Handles API call failures gracefully
- **User Feedback**: Clear error messages and suggestions

### Performance Features
- **Session State Management**: Persistent chat history
- **Lazy Loading**: Chatbot initialized only when needed
- **Caching**: Vector database loaded once per session
- **Responsive Design**: Works on desktop and mobile

## 🐛 Troubleshooting

### Common Issues

#### "API Key not found"
- Ensure `.env` file exists in project root
- Check that `GOOGLE_API_KEY=your_key` is in the file
- Restart the Streamlit app

#### "Data folder not found"
- Create a `data/` folder in the project root
- Add your CSV and PDF files to the folder
- Ensure file names match expected format

#### "Failed to initialize chatbot"
- Check your internet connection
- Verify your API key is valid
- Ensure all dependencies are installed
- Check the console for detailed error messages

#### "No response from chatbot"
- Try rephrasing your question
- Check if the chatbot is properly initialized
- Look for error messages in the chat

### Debug Mode
To run with debug information:
```bash
streamlit run streamlit_app.py --logger.level debug
```

## 📊 Performance Tips

1. **First Run**: Initial setup may take 1-2 minutes for database loading
2. **Subsequent Runs**: Much faster as database is cached
3. **Memory Usage**: App uses ~500MB RAM during operation
4. **Response Time**: 2-5 seconds for most queries

## 🔒 Security

- **API Key**: Stored securely in `.env` file (not in code)
- **Data Privacy**: No data is sent to external services except Google Gemini API
- **Local Processing**: All data processing happens locally

## 🚀 Deployment

### Local Development
```bash
streamlit run streamlit_app.py
```

### Production Deployment
For production deployment, consider:
- Using Streamlit Cloud
- Setting up proper environment variables
- Implementing authentication if needed
- Adding monitoring and logging

## 📝 File Structure

```
Bajaj hackthon 2/
├── streamlit_app.py              # Main Streamlit application
├── setup_streamlit.py            # Setup script
├── requirements_streamlit.txt    # Streamlit-specific dependencies
├── README_STREAMLIT.md          # This file
├── config.py                    # API key configuration
├── enhanced_chatbot_logic.py    # Enhanced chatbot logic
├── enhanced_data_loader.py      # Enhanced data processing
├── data/                        # Data files
│   ├── BFS_Share_Price.csv     # Stock price data
│   └── *.pdf                   # Earnings call transcripts
└── chroma_db/                   # Vector database (auto-generated)
```

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Check the console for error messages
4. Ensure your API key has sufficient quota

## 🎉 Success!

Once everything is set up, you'll have a professional, error-free Streamlit app for your Bajaj Finserv AI chatbot that provides:

- ✅ **Modern web interface**
- ✅ **Robust error handling**
- ✅ **Enhanced query processing**
- ✅ **Professional user experience**
- ✅ **Comprehensive documentation**

Happy chatting! 🚀 