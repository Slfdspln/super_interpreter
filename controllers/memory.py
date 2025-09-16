import os, sqlite3, time, json, hashlib, math
from typing import Optional, List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("SUPERI_DB", os.path.expanduser("~/super_interpreter_memory.sqlite"))

# Check if we have OpenAI for embeddings
HAS_OPENAI = False
try:
    import openai
    HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
    if HAS_OPENAI:
        logger.info("🧠 OpenAI API key found - embeddings enabled")
except ImportError:
    logger.info("📝 OpenAI not available - using text-only storage")

# Check if we have sqlite-vss for vector search
HAS_VSS = False
try:
    import sqlite_vss
    # Test if we can actually use it
    con = sqlite3.connect(":memory:")
    try:
        con.enable_load_extension(True)
        sqlite_vss.load(con)
        con.enable_load_extension(False)
        HAS_VSS = True
        logger.info("🔍 sqlite-vss available and working - vector search enabled")
    except Exception as e:
        logger.info(f"📊 sqlite-vss installed but not working: {e} - using basic search only")
    con.close()
except ImportError:
    logger.info("📊 sqlite-vss not available - using basic search only")

SCHEMA = """
CREATE TABLE IF NOT EXISTS docs(
  id INTEGER PRIMARY KEY,
  namespace TEXT,               -- e.g., "windsurf", "scrapes", "notes"
  title TEXT,
  content TEXT,
  content_hash TEXT,            -- to avoid duplicate embeddings
  meta TEXT,                    -- JSON
  created_at REAL
);

CREATE INDEX IF NOT EXISTS idx_docs_namespace ON docs(namespace);
CREATE INDEX IF NOT EXISTS idx_docs_created_at ON docs(created_at);
CREATE INDEX IF NOT EXISTS idx_docs_hash ON docs(content_hash);
"""

VSS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS docs_embeddings USING vss0(
  embedding(1536),              -- OpenAI embedding dimension
  doc_id INTEGER
);
"""

# Fallback schema for embeddings without VSS
SIMPLE_EMBEDDINGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS docs_embeddings_simple(
  id INTEGER PRIMARY KEY,
  doc_id INTEGER,
  embedding_json TEXT,          -- JSON array of floats
  FOREIGN KEY (doc_id) REFERENCES docs(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_embeddings_doc_id ON docs_embeddings_simple(doc_id);
"""

def _conn():
    """Create database connection with optimizations"""
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    con.execute("PRAGMA cache_size=10000;")
    con.execute("PRAGMA temp_store=memory;")

    # Create basic tables
    con.executescript(SCHEMA)

    # Try to create vector search tables
    if HAS_VSS:
        try:
            con.enable_load_extension(True)
            sqlite_vss.load(con)
            con.enable_load_extension(False)
            con.execute(VSS_SCHEMA)
        except Exception as e:
            logger.warning(f"Could not create VSS table: {e}")
    elif HAS_OPENAI:
        # Create simple embeddings table as fallback
        con.executescript(SIMPLE_EMBEDDINGS_SCHEMA)

    return con

def _get_embedding(text: str) -> Optional[List[float]]:
    """Get OpenAI embedding for text"""
    if not HAS_OPENAI:
        return None

    try:
        client = openai.OpenAI()
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]  # Limit text length
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to get embedding: {e}")
        return None

def _content_hash(content: str) -> str:
    """Generate hash for content to avoid duplicate embeddings"""
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)

def save_doc(namespace: str, title: str, content: str, meta: Dict[str,Any] = {}) -> int:
    """Save document with optional embedding"""
    con = _conn()
    cur = con.cursor()

    content_hash = _content_hash(content)

    # Insert document
    cur.execute("""
        INSERT INTO docs(namespace,title,content,content_hash,meta,created_at)
        VALUES(?,?,?,?,?,?)
    """, (namespace, title, content, content_hash, json.dumps(meta), time.time()))

    doc_id = cur.lastrowid

    # Create embedding if possible
    if HAS_OPENAI:
        try:
            # Check if we already have an embedding for this content
            if HAS_VSS:
                table_check = "SELECT 1 FROM docs_embeddings WHERE doc_id IN (SELECT id FROM docs WHERE content_hash = ?)"
            else:
                table_check = "SELECT 1 FROM docs_embeddings_simple WHERE doc_id IN (SELECT id FROM docs WHERE content_hash = ?)"

            cur.execute(table_check, (content_hash,))
            if not cur.fetchone():
                embedding = _get_embedding(f"{title}\n\n{content}")
                if embedding:
                    if HAS_VSS:
                        # Use VSS format
                        embedding_blob = sqlite_vss.serialize_float32(embedding)
                        cur.execute("INSERT INTO docs_embeddings(doc_id, embedding) VALUES(?, ?)",
                                   (doc_id, embedding_blob))
                    else:
                        # Use simple JSON format
                        cur.execute("INSERT INTO docs_embeddings_simple(doc_id, embedding_json) VALUES(?, ?)",
                                   (doc_id, json.dumps(embedding)))
                    logger.info(f"💾 Created embedding for doc {doc_id}")
        except Exception as e:
            logger.error(f"Failed to create embedding for doc {doc_id}: {e}")

    con.commit()
    con.close()

    logger.info(f"📝 Saved doc {doc_id} in namespace '{namespace}': {title}")
    return doc_id

def list_docs(namespace: Optional[str] = None, limit: int = 50) -> List[Dict[str,Any]]:
    """List documents with optional namespace filter"""
    con = _conn()
    cur = con.cursor()

    if namespace:
        cur.execute("""
            SELECT id,namespace,title,created_at,
                   substr(content,1,100) as preview
            FROM docs WHERE namespace=?
            ORDER BY id DESC LIMIT ?
        """, (namespace, limit))
    else:
        cur.execute("""
            SELECT id,namespace,title,created_at,
                   substr(content,1,100) as preview
            FROM docs
            ORDER BY id DESC LIMIT ?
        """, (limit,))

    rows = cur.fetchall()
    con.close()

    return [{
        "id": r[0],
        "namespace": r[1],
        "title": r[2],
        "created_at": r[3],
        "preview": r[4] + "..." if len(r[4]) >= 100 else r[4]
    } for r in rows]

def get_doc(doc_id: int) -> Dict[str,Any]:
    """Get full document by ID"""
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        SELECT id,namespace,title,content,meta,created_at
        FROM docs WHERE id=?
    """, (doc_id,))
    r = cur.fetchone()
    con.close()

    if not r:
        return {}

    return {
        "id": r[0],
        "namespace": r[1],
        "title": r[2],
        "content": r[3],
        "meta": json.loads(r[4] or "{}"),
        "created_at": r[5]
    }

def search_docs(query: str, namespace: Optional[str] = None, limit: int = 10) -> List[Dict[str,Any]]:
    """Search documents by text similarity (if embeddings available) or text search"""
    con = _conn()
    cur = con.cursor()

    results = []

    # Try semantic search first if available
    if HAS_OPENAI:
        try:
            query_embedding = _get_embedding(query)
            if query_embedding:
                if HAS_VSS:
                    # Use VSS for fast vector search
                    query_blob = sqlite_vss.serialize_float32(query_embedding)

                    if namespace:
                        cur.execute("""
                            SELECT d.id, d.namespace, d.title, d.content, d.meta, d.created_at,
                                   e.distance
                            FROM docs_embeddings e
                            JOIN docs d ON e.doc_id = d.id
                            WHERE e.embedding MATCH ? AND d.namespace = ?
                            ORDER BY e.distance
                            LIMIT ?
                        """, (query_blob, namespace, limit))
                    else:
                        cur.execute("""
                            SELECT d.id, d.namespace, d.title, d.content, d.meta, d.created_at,
                                   e.distance
                            FROM docs_embeddings e
                            JOIN docs d ON e.doc_id = d.id
                            WHERE e.embedding MATCH ?
                            ORDER BY e.distance
                            LIMIT ?
                        """, (query_blob, limit))

                    rows = cur.fetchall()
                    results = [{
                        "id": r[0],
                        "namespace": r[1],
                        "title": r[2],
                        "content": r[3],
                        "meta": json.loads(r[4] or "{}"),
                        "created_at": r[5],
                        "similarity_score": 1.0 - r[6],  # Convert distance to similarity
                        "search_type": "semantic"
                    } for r in rows]
                else:
                    # Use simple cosine similarity fallback
                    if namespace:
                        cur.execute("""
                            SELECT d.id, d.namespace, d.title, d.content, d.meta, d.created_at,
                                   e.embedding_json
                            FROM docs_embeddings_simple e
                            JOIN docs d ON e.doc_id = d.id
                            WHERE d.namespace = ?
                        """, (namespace,))
                    else:
                        cur.execute("""
                            SELECT d.id, d.namespace, d.title, d.content, d.meta, d.created_at,
                                   e.embedding_json
                            FROM docs_embeddings_simple e
                            JOIN docs d ON e.doc_id = d.id
                        """)

                    rows = cur.fetchall()
                    similarities = []
                    for r in rows:
                        doc_embedding = json.loads(r[6])
                        similarity = _cosine_similarity(query_embedding, doc_embedding)
                        similarities.append((r, similarity))

                    # Sort by similarity and take top results
                    similarities.sort(key=lambda x: x[1], reverse=True)
                    results = [{
                        "id": r[0][0],
                        "namespace": r[0][1],
                        "title": r[0][2],
                        "content": r[0][3],
                        "meta": json.loads(r[0][4] or "{}"),
                        "created_at": r[0][5],
                        "similarity_score": r[1],
                        "search_type": "semantic"
                    } for r in similarities[:limit]]

                if results:
                    logger.info(f"🔍 Found {len(results)} semantic matches for: {query}")
                    con.close()
                    return results
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")

    # Fall back to text search
    search_terms = f"%{query}%"

    if namespace:
        cur.execute("""
            SELECT id,namespace,title,content,meta,created_at
            FROM docs
            WHERE (title LIKE ? OR content LIKE ?) AND namespace = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_terms, search_terms, namespace, limit))
    else:
        cur.execute("""
            SELECT id,namespace,title,content,meta,created_at
            FROM docs
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_terms, search_terms, limit))

    rows = cur.fetchall()
    con.close()

    results = [{
        "id": r[0],
        "namespace": r[1],
        "title": r[2],
        "content": r[3],
        "meta": json.loads(r[4] or "{}"),
        "created_at": r[5],
        "search_type": "text"
    } for r in rows]

    logger.info(f"📝 Found {len(results)} text matches for: {query}")
    return results

def delete_doc(doc_id: int) -> bool:
    """Delete document and its embedding"""
    con = _conn()
    cur = con.cursor()

    # Delete embedding first
    if HAS_VSS:
        try:
            cur.execute("DELETE FROM docs_embeddings WHERE doc_id = ?", (doc_id,))
        except Exception:
            pass

    # Delete document
    cur.execute("DELETE FROM docs WHERE id = ?", (doc_id,))
    deleted = cur.rowcount > 0

    con.commit()
    con.close()

    if deleted:
        logger.info(f"🗑️ Deleted doc {doc_id}")

    return deleted

def get_stats() -> Dict[str, Any]:
    """Get memory database statistics"""
    con = _conn()
    cur = con.cursor()

    # Count docs by namespace
    cur.execute("SELECT namespace, COUNT(*) FROM docs GROUP BY namespace")
    namespace_counts = dict(cur.fetchall())

    # Total docs
    cur.execute("SELECT COUNT(*) FROM docs")
    total_docs = cur.fetchone()[0]

    # Count embeddings
    embedding_count = 0
    if HAS_OPENAI:
        try:
            if HAS_VSS:
                cur.execute("SELECT COUNT(*) FROM docs_embeddings")
            else:
                cur.execute("SELECT COUNT(*) FROM docs_embeddings_simple")
            embedding_count = cur.fetchone()[0]
        except Exception:
            pass

    con.close()

    return {
        "total_docs": total_docs,
        "namespace_counts": namespace_counts,
        "embedding_count": embedding_count,
        "has_embeddings": HAS_OPENAI,
        "db_path": DB_PATH
    }

# Convenience functions for quick use
def quick_save(namespace: str, content: str, title: Optional[str] = None) -> int:
    """Quick save with auto-generated title"""
    if not title:
        title = f"Note {time.strftime('%Y-%m-%d %H:%M')}"
    return save_doc(namespace, title, content)

def recent_docs(namespace: Optional[str] = None, days: int = 7) -> List[Dict[str,Any]]:
    """Get recently created documents"""
    since = time.time() - (days * 24 * 3600)
    con = _conn()
    cur = con.cursor()

    if namespace:
        cur.execute("""
            SELECT id,namespace,title,created_at
            FROM docs
            WHERE created_at > ? AND namespace = ?
            ORDER BY created_at DESC
        """, (since, namespace))
    else:
        cur.execute("""
            SELECT id,namespace,title,created_at
            FROM docs
            WHERE created_at > ?
            ORDER BY created_at DESC
        """, (since,))

    rows = cur.fetchall()
    con.close()

    return [{
        "id": r[0],
        "namespace": r[1],
        "title": r[2],
        "created_at": r[3]
    } for r in rows]