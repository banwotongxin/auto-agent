"""向量存储服务"""
import asyncio
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
from app.config import settings


class VectorStore:
    """向量存储服务"""
    
    _instance: Optional["VectorStore"] = None
    _client: Optional[chromadb.Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )
            
            # 设置嵌入函数
            self.embedding_function = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=settings.EMBEDDING_MODEL
                )
            )
    
    def get_or_create_collection(self, session_id: str):
        """获取或创建集合"""
        return self._client.get_or_create_collection(
            name=f"research_{session_id}",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def add_sources(
        self,
        session_id: str,
        sources: List[Dict[str, Any]]
    ):
        """
        添加来源到向量存储
        
        Args:
            session_id: 会话ID
            sources: 来源列表
        """
        collection = self.get_or_create_collection(session_id)
        
        # 分块处理
        chunks = []
        metadatas = []
        ids = []
        
        for i, source in enumerate(sources):
            content = source.get("content", "")
            
            # 简单分块
            chunk_size = settings.CHUNK_SIZE
            overlap = settings.CHUNK_OVERLAP
            
            for j in range(0, len(content), chunk_size - overlap):
                chunk = content[j:j + chunk_size]
                if len(chunk) > 100:  # 过滤太短的内容
                    chunk_id = f"{i}_{j}"
                    chunks.append(chunk)
                    metadatas.append({
                        "url": source.get("url", ""),
                        "title": source.get("title", ""),
                        "chunk_index": j // (chunk_size - overlap)
                    })
                    ids.append(chunk_id)
        
        if chunks:
            # 使用线程池执行同步操作
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: collection.add(
                    documents=chunks,
                    metadatas=metadatas,
                    ids=ids
                )
            )
    
    async def search_similar(
        self,
        session_id: str,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        搜索相似内容
        
        Args:
            session_id: 会话ID
            query: 查询文本
            n_results: 返回结果数
            
        Returns:
            相似内容列表
        """
        collection = self.get_or_create_collection(session_id)
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: collection.query(
                query_texts=[query],
                n_results=n_results
            )
        )
        
        return [
            {
                "content": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    
    async def delete_collection(self, session_id: str):
        """删除集合"""
        try:
            self._client.delete_collection(name=f"research_{session_id}")
        except Exception:
            pass  # 集合可能不存在
