import os
from langchain_core.embeddings import Embeddings
from openai import OpenAI
from httpx import Client, Timeout

# 修复后的CustomEmbeddings（兼容Document对象）
class CustomEmbeddings(Embeddings):
    def __init__(self):
        http_client = Client(
            timeout=Timeout(60.0, connect=60.0),
            follow_redirects=True
        )
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
            http_client=http_client
        )
    #这里LanceDB 自动调用时传入的texts类型是List [Document]（对象列表），而传入OpenAI接口的batch要求是List[Str]
    def embed_documents(self, texts):
        batch_size = 5
        all_embeddings = []
        
        # 关键修复：提取Document对象的page_content纯文本
        text_strings = []
        for item in texts:
            # 兼容Document对象和纯字符串
            if hasattr(item, 'page_content'):
                text = item.page_content.strip()
            else:
                text = str(item).strip()
            if text:  # 过滤空文本
                text_strings.append(text)

        # 批量处理纯文本（和测试代码逻辑一致）
        for i in range(0, len(text_strings), batch_size):
            batch = text_strings[i: i + batch_size]
            if not batch:
                continue
            response = self.client.embeddings.create(
                model="text-embedding-v4",
                input=batch,
                dimensions=1024
            )
            all_embeddings.extend([data.embedding for data in response.data])
        return all_embeddings

    def embed_query(self, text):
        return self.embed_documents([text])[0]