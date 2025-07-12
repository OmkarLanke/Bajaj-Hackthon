# setup_streamlit.py
import subprocess
import sys
import os

def install_requirements():
    """Install required packages for the Streamlit app."""
    print("🚀 Setting up Bajaj Finserv AI Chatbot...")
    
    try:
        # Install requirements
        print("📦 Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_streamlit.txt"])
        print("✅ Packages installed successfully!")
        
        # Check if .env file exists
        if not os.path.exists(".env"):
            print("⚠️  .env file not found!")
            print("📝 Please create a .env file with your Google Gemini API key:")
            print("   GOOGLE_API_KEY=your_api_key_here")
        else:
            print("✅ .env file found!")
        
        # Check if data folder exists
        if not os.path.exists("data"):
            print("⚠️  data folder not found!")
            print("📁 Please ensure your data files are in the 'data' folder:")
            print("   • BFS_Share_Price.csv")
            print("   • Earnings call transcripts (PDF files)")
        else:
            print("✅ data folder found!")
        
        print("\n🎉 Setup complete!")
        print("🚀 To run the Streamlit app:")
        print("   streamlit run streamlit_app.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        print("💡 Try running: pip install -r requirements_streamlit.txt")
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    install_requirements() 