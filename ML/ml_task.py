from datasets import load_dataset
import json
import re
import hashlib
import pandas as pd
import tqdm

def generate_md5_hash(data):
    """使用MD5算法生成hash ID"""
    # 如果输入不是字符串，转换为字符串
    if not isinstance(data, str):
        data = str(data)
    
    # 确保输入是bytes类型
    if isinstance(data, str):
        data = data.encode('utf-8')
        
    # 生成MD5 hash
    md5_hash = hashlib.md5(data).hexdigest()
    return md5_hash

def check_yes_no_ending(text):
    """
    检查字符串是否以yes或no结尾，如果是则提取结果
    
    Args:
        text (str): 需要检查的字符串
        
    Returns:
        str or None: 如果找到yes或no则返回对应值，否则返回None
    """
    # 使用正则表达式匹配字符串末尾的yes或no（不区分大小写）
    pattern = r'(yes|no)\s*$'
    match = re.search(pattern, text.lower())
    
    if match:
        answer = match.group(1)
        # 移除结尾的yes或no和任何前面的空白
        question = re.sub(r'\s*(yes|no)\s*$', '', text, flags=re.IGNORECASE).strip()
        
        result = {
            "Question": question,
            "Answer": answer
        }
        
        return result
    else:
        result = {
            "Question": text,
            "Answer": None
        }
        return result

def extract_question(text, gold_index, tag_data):
    """
    从input中提取问题
    
    Args:
        text (str): 需要提取问题的字符串
        gold_index (int): 最后一个问题的答案
        
    Returns:
        str or None: 如果找到yes或no则返回对应值，否则返回None
    """
    # 使用正则表达式匹配字符串末尾的yes或no（不区分大小写）
    pattern = r'(yes|no)\s*$'
    options = ["no","yes"]
    result = []
    # 分割问题
    question_pairs = text.split("\n\n")
    for pair in question_pairs:
        for tag in tag_data:
            if tag['News'] in pair:
                qa_pairs = check_yes_no_ending(pair)
                qa_pairs['tags'] = tag['tag']
                qa_pairs['id'] = generate_md5_hash(qa_pairs['Question'])
                if qa_pairs['Answer'] is not None:
                    qa_pairs['Answer'] = options[gold_index]
                    result.append(qa_pairs)
        # break
    return result

def extract_tag(entry):
    tag_dict = {
                "Price Direction Up": entry["Price Direction Up"],
                "Price Direction Constant": entry["Price Direction Constant"],
                "Price Direction Down": entry["Price Direction Down"],
                "Asset Comparision": entry["Asset Comparision"],
                "Past Information": entry["Past Information"],
                "Future Information": entry["Future Information"],
                "Price Sentiment": entry["Price Sentiment"]
            }
    item = {
        "News": entry['News'],
        "tag": tag_dict
    }
    return item

if __name__ == "__main__":

    # 读取数据
    data = load_dataset("AdaptLLM/finance-tasks", "Headline")
    tag_datasets = load_dataset("SaguaroCapital/sentiment-analysis-in-commodity-market-gold")
    
    # 提取标签
    tag_data = []
    for i, entry in enumerate(tag_datasets['train']):
        item = extract_tag(entry)
        tag_data.append(item)
    for i, entry in enumerate(tag_datasets['test']):
        item = extract_tag(entry)
        tag_data.append(item)
    

    # 提取问题
    result = []
    
    for i, entry in enumerate(tqdm.tqdm(data['test'], desc="Processing test entries")):
        qa_pairs = extract_question(entry['input'],entry["gold_index"], tag_data)
        result.extend(qa_pairs)
    
    # 保存结果
    with open("qa_pairs.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)