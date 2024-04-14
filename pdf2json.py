import os
import arxiv
import PyPDF2
import json
import concurrent.futures
import string
import re
import nltk
nltk.download('punkt')

# 一些参数
input_json_path = "arxiv_papers.json"           # 输入：[{"id":,...}...]
papers_output_dir = "papers"                    # 文献下载路径
result_path = "result.json"                     # 结果文件

rm_abstract = True                              # 去除摘要
rm_references = True                            # 去除参考文献
rm_illegal = True                               # 去除非法字符


def download_pdf(arxiv_id, output_dir):
    """
    从 arXiv 下载指定 ID 的 PDF 文件
    """
    pdf_filename = f"{arxiv_id}.pdf"
    file_path = os.path.join("papers", f"{arxiv_id}.pdf")
    if os.path.exists(file_path):
        return pdf_filename
    paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))

    paper.download_pdf(dirpath=output_dir, filename=pdf_filename)
    print(f"{arxiv_id}" + " : download finished!")
    return pdf_filename


def extract_text_from_pdf(pdf_path):
    """
    从 PDF 文件中提取文本内容
    """
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()

    return text


def remove_abstract(text):
    """
    从文本中移除摘要
    """
    abstract_ind = text.find("ABSTRACT")
    if abstract_ind == -1:
        abstract_ind = text.find("Abstract")

    start = text.find("INTRODUCTION")
    if start == -1:
        start = text.find("Introduction")

    if abstract_ind != -1 and start != -1 and abstract_ind < start:     # 有的文献主体第一部分不是introduction, 就不删除摘要了
        text_judge_tokens = nltk.word_tokenize(text[abstract_ind: start])
        if len(text_judge_tokens) < 600:        # 确保这一部分是摘要
            text = text[start:]
    return text


def remove_references(text):
    """
    从文本中移除参考文献
    """
    end = text.rfind("REFERENCES")
    if end == -1:
        end = text.find("References")

    if end != -1:
        text = text[:end]
    return text


def create_json(arxiv_id, prompt_text):
    """
    创建 JSON 格式数据
    """
    translator = str.maketrans('', '', string.punctuation)
    tokens = nltk.word_tokenize(prompt_text.translate(translator))
    word_cnt = len(tokens)

    json_data = {
        "history": "",
        "prompt": prompt_text,
        "response": "",
        "task_level_1": "",
        "len": word_cnt,
        "id": arxiv_id
    }
    return json.dumps(json_data, ensure_ascii=False, indent=4)


def download_and_process(arxiv_id, output_dir):
    """
    下载并处理 PDF 文件
    """
    pdf_filename = download_pdf(arxiv_id, output_dir)  # 下载 PDF 文件
    text = extract_text_from_pdf(os.path.join(output_dir, pdf_filename))  # 提取 PDF 文件中的文本内容
    text = text.replace("-\n", "")
    text = text.replace("\n", " ")
    if rm_abstract:
        text = remove_abstract(text)
    if rm_references:
        text = remove_references(text)
    if rm_illegal:
        text = re.sub(r'[^\x00-\x7F]+', '', text)

    json_data = create_json(arxiv_id, remove_abstract(text.strip()))  # 创建 JSON 格式的数据
    return json_data  # 返回创建的 JSON 数据


def main(input_json_path, output_dir):
    """
    主函数，流程：
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(input_json_path, 'r', encoding='utf-8') as json_file:
        paper_list = json.load(json_file)

    output_data = []  # 用于存储所有的 JSON 数据
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        # 提交任务给线程池
        future_to_arxiv_id = {executor.submit(download_and_process, paper["id"], output_dir):
                                  paper["id"] for paper in paper_list}

        # 获取任务的返回结果
        for future in concurrent.futures.as_completed(future_to_arxiv_id):
            arxiv_id = future_to_arxiv_id[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f"Download and process for arxiv_id {arxiv_id} generated an exception: {exc}")
            else:
                output_data.append(json.loads(data))
                print(f"{arxiv_id}" + " : success!")

    with open(result_path, 'w', encoding='utf-8') as output_json_file:
        json.dump(output_data, output_json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    input_json_path = input_json_path
    output_dir = papers_output_dir
    main(input_json_path, output_dir)
