
import sys
import os
import io
from pathlib import Path

sys.path.append(os.path.join(os.getcwd(), "backend"))
import rag_loader

def test_bone_full():
    rag_loader.RAG_PATH = Path("rag")
    docs = rag_loader._load_armor()
    
    with open("bone_full_data.txt", "w", encoding="utf-8") as f:
        for doc in docs:
            if "Óssea α+" in doc.text:
                f.write("--- BONE ALPHA+ SET ---\n")
                f.write(doc.text)
                f.write("\n" + "="*50 + "\n")
            if "Óssea β+" in doc.text:
                f.write("--- BONE BETA+ SET ---\n")
                f.write(doc.text)
                f.write("\n" + "="*50 + "\n")

if __name__ == "__main__":
    test_bone_full()
