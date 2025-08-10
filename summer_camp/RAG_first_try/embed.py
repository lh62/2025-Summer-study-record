import my_chunk
import chromadb
from google import genai
from tqdm import tqdm

google_client = genai.Client()
EMBEDDING_MODEL = "gemini-embeding-exp-03-07"
LLM_MODEL = "gemini-2.5-flash-preview-05-20"

chromadb_client = chromadb.PersistentClient("./google_chroma.db")#连接本地数据库
chromadb_collection = chromadb_client.get_or_create_collection("linghuchong")#创建或获取名为"linghuchong"的集合



def embed(text: str, store: bool) -> list[float]:
    tqdm.write(f"正在生成{'文档' if store else '查询'}的embedding...")
    result = google_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config={
            "task_type": "RETRIEVAL_DOCUMENT" if store else "RETRIEVAL_QUERY"        
            }
    )
    tqdm.write("embedding生成完成!")

    assert result.embeddings
    assert result.embeddings[0].values
    return result.embeddings[0].values

def create_db() -> None:
    for idx, c in enumerate(my_chunk.get_chunked_data()):
        print(f"Processing: {c}")
        embedding = embed(c,store=True)
        chromadb_collection.upsert(
            ids=str(idx),
            documents=c,
            embeddings=embedding
        )

def query_db(question: str) -> list[str]:
    question_embedding = embed(question, store=False)
    result = chromadb_collection.query(
        query_embeddings=question_embedding,
        n_results=5
    )
    assert result["documents"]
    return result["documents"][0]

if __name__ == "__main__":
    # 测试embedding生成
    # chunks = my_chunk.get_chunked_data()
    # for chunk in tqdm(chunks, desc="处理文档块"):
    #     embed(chunk, True)

    # 创建数据库
    #create_db()

    qustion = "令狐冲转生为史莱姆的故事是怎样的？" 
    chunks = query_db(qustion)

    prompt = "Please answer following questions based on the context we provide:\n"
    prompt += f"Question: {qustion}\n"
    prompt += "Context:\n"
    for c in chunks:
        prompt += f"{c}\n"
        prompt += "----------------------\n"
    
    result = google_client.models.generate_text(
        model=LLM_MODEL,
        contents=prompt
    )
    print(result)

    