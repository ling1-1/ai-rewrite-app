#!/usr/bin/env python3
"""
使用 sentence-transformers 生成本地向量

模型：BAAI/bge-small-zh-v1.5（中文优化，轻量级）
维度：512
"""

from sentence_transformers import SentenceTransformer

# 加载模型（首次运行会自动下载）
print("📦 加载 Embedding 模型...")
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
print(f"✅ 模型加载成功！")

def get_embedding(text: str):
    """
    获取文本的向量嵌入
    
    Args:
        text: 输入文本
        
    Returns:
        list: 向量（512 维）
    """
    # 生成向量
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


if __name__ == "__main__":
    # 测试
    test_texts = [
        "机器学习是人工智能的一个分支",
        "深度学习使用神经网络学习数据表示",
        "自然语言处理让计算机理解人类语言",
    ]
    
    print("="*60)
    print("🚀 本地 Embedding 测试（BAAI/bge-small-zh-v1.5）")
    print("="*60)
    
    for text in test_texts:
        print(f"\n📝 输入：{text}")
        embedding = get_embedding(text)
        print(f"✅ 向量维度：{len(embedding)}")
        print(f"✅ 前 10 个值：{[f'{x:.4f}' for x in embedding[:10]]}")
    
    # 测试相似度
    print("\n\n" + "="*60)
    print("📊 相似度测试")
    print("="*60)
    
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    embeddings = [get_embedding(text) for text in test_texts]
    similarity = cosine_similarity([embeddings[0]], embeddings[1:])[0]
    
    print(f"\n'{test_texts[0]}' 与:")
    for i, sim in enumerate(similarity, 1):
        print(f"  - '{test_texts[i]}': 相似度 {sim:.4f}")
