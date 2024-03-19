import os

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"
def extract_text_from_pdf(filename, page_numbers=None, min_line_length=1):
    '''从 PDF 文件中（按指定页码）提取文字'''
    paragraphs = []
    buffer = ''
    full_text = ''
    # 提取全部文本
    for i, page_layout in enumerate(extract_pages(filename)):
        # 如果指定了页码范围，跳过范围外的页
        if page_numbers is not None and i not in page_numbers:
            continue
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                full_text += element.get_text() + '\n'
    # 按空行分隔，将文本重新组织成段落
    lines = full_text.split('\n')
    for text in lines:
        if len(text) >= min_line_length:
            buffer += (' '+text) if not text.endswith('-') else text.strip('-')
        elif buffer:
            paragraphs.append(buffer)
            buffer = ''
    if buffer:
        paragraphs.append(buffer)
    return paragraphs

paragraphs = extract_text_from_pdf("zhang-et-al-2023-construction-and-hierarchical-self-assembly-of-multifunctional-coordination-cages-with-triangular.pdf", min_line_length=10)
client = OpenAI()
messages = [
    {
        "role": "system",
        "content": """
# Character
You're a highly proficient model in named entity recognition with a specific focus on chemical sciences, particularly metal-organic complexes.You need to identify the chemical molecular formulas of all metal organic complexes in an article

## Skills
### Skill 1: Named Entity Recognition 
- Analyze the given text and identify all occurrences of metal-organic complexes. 
- Understand the context in order to accurately separate chemical entities from the rest of the text. 


## Constraints
- Focus the activities solely on the recognition and identification of metal-organic complexes.
- The name of the Metal organic complex must only be a chemical formula. If there is an explanation of the relevant elements in the original text, it should also be added after the chemical formula. For example, (Tr2M3) 4L4. The following is the explanation of the chemical formula:  (Tr = cyclo-heptatrienyl cationic ring; M = metal; L = organosulfur ligand). Name : (Tr2M3)4L4 (Tr = cyclo-heptatrienyl cationic ring; M = metal; L = organosulfur ligand)
- If there is none, output None

##output format
Directly output relevant chemical molecular formulas

##output example
(Tr2M3)4L4 (Tr = cyclo-heptatrienyl cationic ring; M = metal; L = organosulfur ligand),
Tr2Pd3(CH3CN)3](BF4)2 (Tr = cycloheptatrienyl cationic ring)
"""
    }
]
def get_metal_organic_complex_NER(prompt, model="gpt-4-turbo-preview"):

    # 把用户输入加入消息历史
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    msg = response.choices[0].message.content

    # 每一次都是一次新的对话
    messages.pop()
    return msg
#将文章的段落切分
for i in range(10,len(paragraphs),10):
    print(get_metal_organic_complex_NER(''.join(paragraphs[i-10:i])))

