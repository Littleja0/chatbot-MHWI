
import sys
import os
from pathlib import Path

sys.path.append(os.path.join(os.getcwd(), "backend"))
import rag_loader # type: ignore

def check_for_r():
    rag_loader.RAG_PATH = Path("rag")
    docs = rag_loader._load_armor()
    
    for doc in docs:
        if "Óssea α+" in doc.text:
            if "\r" in doc.text:
                print(f"!!! FOUND REVENGE OF THE CARRIAGE RETURN in Bone set !!!")
                print(f"Occurrences: {doc.text.count('\r')}")
                # Replace \r with [R] for visibility
                print(doc.text.replace("\r", "[R]").replace("\n", "[N]\n"))
            else:
                print("No \\r found in Bone set.")
            break

if __name__ == "__main__":
    check_for_r()
