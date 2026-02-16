import mhw_rag
import sys
import io

# Force UTF-8 for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_context():
    # Setup the engine (it will rebuild because of new XML and code changes)
    mhw_rag.setup_rag_engine()
    
    # Get context for "drop rate de joia ataque"
    context = mhw_rag.get_rag_context("qual o drop rate da joia de ataque?")
    print("--- Context for 'drop rate joia ataque' ---")
    print(context)

if __name__ == "__main__":
    test_context()
