"""
rag_pipeline.py — Pipeline automatizado para atualização do RAG.

Detecta mudanças nos XMLs via hashing SHA256, reconstrói o índice apenas
quando necessário, e monitora a pasta rag/ em tempo real para atualizações
automáticas com hot-reload do query engine.

Integra diretamente com o stack existente (LlamaIndex VectorStoreIndex).
"""

import hashlib
import json
import threading
from pathlib import Path
from typing import Callable, Optional

# ============================================================
# MANIFESTO DE HASHES — Detecta o que mudou
# ============================================================

MANIFEST_PATH = Path("storage/rag_manifest.json")
RAG_PATH = Path("rag")


def _file_hash(path: Path) -> str:
    """Calcula SHA256 de um arquivo."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_manifest() -> dict:
    """Carrega manifesto de hashes dos XMLs."""
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_manifest():
    """Salva manifesto de hashes dos XMLs atuais."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for f in RAG_PATH.glob("*.xml"):
        manifest[f.name] = _file_hash(f)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2)
    print(f"  📋 Manifesto salvo com {len(manifest)} XMLs rastreados")


def detect_changes() -> dict:
    """
    Compara estado atual dos XMLs com o manifesto salvo.

    Returns:
        {
            "added": ["new_file.xml"],
            "modified": ["changed_file.xml"],
            "removed": ["deleted_file.xml"],
            "unchanged": ["same_file.xml"]
        }
    """
    old_manifest = _load_manifest()
    current_files = {}
    for f in RAG_PATH.glob("*.xml"):
        current_files[f.name] = _file_hash(f)

    changes = {"added": [], "modified": [], "removed": [], "unchanged": []}

    for fname, fhash in current_files.items():
        if fname not in old_manifest:
            changes["added"].append(fname)
        elif old_manifest[fname] != fhash:
            changes["modified"].append(fname)
        else:
            changes["unchanged"].append(fname)

    for fname in old_manifest:
        if fname not in current_files:
            changes["removed"].append(fname)

    return changes


def needs_rebuild() -> bool:
    """
    Verifica se o índice precisa ser reconstruído.
    Retorna True se:
    - Não existe storage/
    - Não existe manifesto
    - Algum XML foi adicionado, modificado ou removido
    """
    storage = Path("storage")
    if not storage.exists() or not any(storage.iterdir()):
        return True

    if not MANIFEST_PATH.exists():
        return True

    changes = detect_changes()
    total_changes = len(changes["added"]) + len(changes["modified"]) + len(changes["removed"])
    if total_changes > 0:
        print(f"  ⚠️ Mudanças detectadas: +{len(changes['added'])} novos, "
              f"~{len(changes['modified'])} modificados, "
              f"-{len(changes['removed'])} removidos")
        return True

    return False


# ============================================================
# WATCHER — Monitora mudanças em tempo real
# ============================================================

class RAGFileWatcher:
    """
    Monitora a pasta rag/ por mudanças nos XMLs.
    Quando detecta uma mudança, marca que o rebuild é necessário
    e opcionalmente dispara hot-reload.

    Usa debouncing para evitar múltiplos triggers durante batch updates.
    """

    def __init__(
        self,
        debounce_seconds: float = 5.0,
        on_change: Optional[Callable] = None,
    ):
        self.debounce_seconds = debounce_seconds
        self.on_change = on_change
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._running = False
        self._observer = None

    def start(self):
        """Inicia o monitoramento em background."""
        try:
            from watchdog.observers import Observer  # type: ignore
            from watchdog.events import FileSystemEventHandler  # type: ignore
        except ImportError:
            print("  ℹ️ watchdog não instalado — monitoramento automático desabilitado")
            print("  ℹ️ Para habilitar: pip install watchdog")
            return False

        watcher_ref = self

        class XMLHandler(FileSystemEventHandler):
            def on_any_event(self, event):  # type: ignore
                if hasattr(event, 'src_path') and str(event.src_path).endswith(".xml"):
                    watcher_ref._schedule_update()

        self._observer = Observer()
        self._observer.schedule(XMLHandler(), str(RAG_PATH), recursive=False)
        self._observer.daemon = True
        self._observer.start()
        self._running = True
        print(f"  👁️ Monitorando {RAG_PATH}/ por mudanças em XMLs...")
        return True

    def stop(self):
        """Para o monitoramento."""
        if self._running and self._observer:
            self._observer.stop()
            self._observer.join(timeout=3)
            self._running = False
            print("  ⏹️ Monitor de XMLs parado.")

    def _schedule_update(self):
        """Agenda update com debouncing (evita triggers múltiplos)."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(
                self.debounce_seconds, self._on_files_changed
            )
            self._timer.daemon = True
            self._timer.start()

    def _on_files_changed(self):
        """Callback quando arquivos mudam (após debounce)."""
        if not needs_rebuild():
            return

        print("\n🔄 Mudanças nos XMLs detectadas! Reconstruindo índice...")

        if self.on_change:
            try:
                self.on_change()
            except Exception as e:
                print(f"  ❌ Erro no hot-reload: {e}")
        else:
            print("  ⚠️ Nenhum callback de hot-reload configurado")


# ============================================================
# HOT RELOAD — Reconstrói o índice sem reiniciar o servidor
# ============================================================

def hot_reload():
    """
    Reconstrói o índice e recarrega o query engine em memória.
    Chamado automaticamente pelo watcher quando XMLs mudam.
    """
    try:
        import mhw_rag  # type: ignore
        engine = mhw_rag.reload_engine()
        if engine:
            print("  🔥 Query engine recarregado com sucesso (hot-reload)")
            return True
        print("  ❌ reload_engine retornou None")
        return False
    except Exception as e:
        print(f"  ❌ Falha no hot-reload: {e}")
        return False


# ============================================================
# INSTÂNCIA GLOBAL DO WATCHER
# ============================================================

_watcher: Optional[RAGFileWatcher] = None


def start_watcher():
    """Inicia o watcher global. Chamado pelo main.py após setup do RAG."""
    global _watcher
    if _watcher and _watcher._running:
        return  # Já está rodando

    _watcher = RAGFileWatcher(
        debounce_seconds=5.0,
        on_change=hot_reload,
    )
    return _watcher.start()


def stop_watcher():
    """Para o watcher global."""
    global _watcher
    if _watcher:
        _watcher.stop()
        _watcher = None


# ============================================================
# TEST / DIAGNÓSTICO
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  RAG PIPELINE — Diagnóstico")
    print("=" * 60)

    print(f"\n📂 Pasta rag/: {RAG_PATH.resolve()}")
    xml_count = len(list(RAG_PATH.glob("*.xml")))
    print(f"   XMLs encontrados: {xml_count}")

    print(f"\n📋 Manifesto: {MANIFEST_PATH}")
    print(f"   Existe: {MANIFEST_PATH.exists()}")

    print(f"\n🔍 Análise de mudanças:")
    changes = detect_changes()
    print(f"   Novos:       {len(changes['added'])}")
    print(f"   Modificados: {len(changes['modified'])}")
    print(f"   Removidos:   {len(changes['removed'])}")
    print(f"   Inalterados: {len(changes['unchanged'])}")

    needs = needs_rebuild()
    print(f"\n🔨 Precisa rebuild: {'SIM' if needs else 'NÃO'}")

    if changes['added']:
        print(f"\n   Novos: {', '.join(changes['added'][:10])}")
    if changes['modified']:
        print(f"   Modificados: {', '.join(changes['modified'][:10])}")
    if changes['removed']:
        print(f"   Removidos: {', '.join(changes['removed'][:10])}")
