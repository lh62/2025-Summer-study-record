def read_data(file_path: str) -> str:
    with open(file=file_path, mode="r", encoding="utf-8") as file:
        content = file.read()
    return content 

def get_chunked_data() -> list[str]:
    
    content: str = read_data(file_path="/home/lh/桌面/2025-Summer-study-record/summer_camp/RAG_first_try/关于令狐冲转生为史莱姆并对世界献上了美好的炎爆这件事.txt")
    chunks: list[str] = content.split("\n\n")

    result: list = []
    header = ""
    for c in chunks:
        if c.startswith('#'):
            header += f"{c}\n"
        else:
            result.append(f"{header}{c}")
            header = ""
    return result


def main() -> None:     
    chunks: list[str] = get_chunked_data()
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}:\n{chunk}\n{'-' * 40}")

if __name__ == "__main__":
    main()
