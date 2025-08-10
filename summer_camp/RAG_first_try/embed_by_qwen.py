import requests
import my_chunk
import chromadb
import yaml

chromadb_client = chromadb.PersistentClient("./chroma.db")#连接本地数据库
chromadb_collection = chromadb_client.get_or_create_collection("linghuchong")#创建或获取名为"linghuchong"的集合


def embeding(chunk: str, api_key: str) -> list[float]:
    url = "https://api.siliconflow.cn/v1/embeddings"

    payload = {
        "model": "BAAI/bge-large-zh-v1.5",
        "input": chunk, 
        "encoding_format": "float"
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    assert response.json()['data']
    assert response.json()['data'][0]['embedding']
    return response.json()['data'][0]['embedding']

def create_db(api_key: str) -> None:
    for idx, chunk in enumerate(my_chunk.get_chunked_data()):
        print(f"Processing: {chunk}")
        embedding = embeding(chunk, api_key)
        chromadb_collection.upsert(
            ids=str(idx),
            documents=chunk,
            embeddings=embedding
        )

def query_db(question: str, api_key: str, n_results: int = 5) -> list[str]:
    question_embedding = embeding(question, api_key)
    result = chromadb_collection.query(
        query_embeddings=question_embedding,
        n_results=n_results
    )
    assert result["documents"]
    return result["documents"][0]

def call_llm(prompt: str, api_key: str) -> list[str]:

    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    assert response.json()['choices']
    assert response.json()['choices'][0]['message']['content']
    return response.json()['choices'][0]['message']['content']

def main(question: str, api_key: str, n_results: int = 5):
    similar_chunks = query_db(question, api_key, n_results)
    prompt = "请根据以下上下文回答问题:\n"
    prompt += "\n".join([f"上下文 {i+1}: {chunk}" for i, chunk in enumerate(similar_chunks)])
    prompt += f"\n\n问题: {question}\n回答:"
    print("Prompt:\n\n", prompt)
    response = call_llm(prompt, api_key)
    print(response)

if __name__ == "__main__":
    with open('2025-Summer-study-record/summer_camp/RAG_first_try/api_key.yaml', "r", encoding="utf-8") as f:
        api_key = yaml.safe_load(f)['api_key']
        print(api_key)

    #create_db(api_key) # 创建数据库
    main("令狐冲修得了什么功法？", api_key) # 回答问题
