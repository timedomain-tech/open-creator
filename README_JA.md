<h1 align="center">◓ Open Creator</h1>

<p align="center">
    <a href="https://discord.gg/eEraZEry53">
        <img alt="Discord" src="https://img.shields.io/discord/1153640284530417684?logo=discord&style=flat&logoColor=white"/>
    </a>
    <a href="README_JA.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
    <a href="README_ZH.md"><img src="https://img.shields.io/badge/文档-中文版-white.svg" alt="ZH doc"/></a>
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white&style=flat" alt="License"/>
    <a href="docs/tech_report/open-creator.pdf"><img src="https://img.shields.io/badge/arXiv-Paper-blue.svg" alt="paper"></a>
    <br><br>
    <b>カスタマイズされたスキルライブラリを構築</b><br>
    ツールを作成するためのオープンソースのLLMツール<br>
</p>

<br>

`open-creator` は、既存の会話や要求からスキルを抽出し、それらを保存し、必要に応じて取得するために設計された革新的なパッケージです。これは、コードの洗練されたバージョンを統合し、アーカイブするシームレスな方法を提供し、それらを即座に使用可能なスキルセットに変えることで、[open-interpreter](https://github.com/KillianLucas/open-interpreter) の力を強化します。

![](docs/tech_report/figures/framework.png)


# 特徴
- [x] **スキルライブラリ**：効率的に構造化された関数呼び出しを保存および取得。
- [x] **リフレクションエージェント**：あなたの関数呼び出しを自動的に構造化し、カテゴリ分けします。
- [x] **`~/.cache/open_creator/llm_cache/.langchain.db` に格納されているSQLiteを使用してチャットLLMをキャッシュ**：以前の実行を再利用して時間とお金を節約。
- [x] **ストリーミング**：関数呼び出しをストリームします。
- [x] **コミュニティハブ**：より広いコミュニティからのスキルを共有し、利用します。 `huggingface_hub` をサポート。 `langchain_hub` はまだです。

# Updates
- [x] **2023-10-01**: いくつかのバグを修正し、エージェントエージェントのテストとリファクタリングをサポートします
- [x] **2023-10-19**: バグの修正とプロジェクトの構造変更を行いました。新たに以下のサポートを追加しました：
  - クリエーターツールのインポート：`from creator.agents.creator_agent import open_creator_agent`
  - コマンドライン操作：詳しくは`creator -h`を参照。サーバーモードでの起動：`creator server`、アクセスは `http://localhost:8000/docs`。Streamlitデモの表示：`creator ui`、アクセスは `http://localhost:8501/`
  - 豊富なドキュメンテーション： [ノートブックサンプル](examples/01_skills_create.ipyn) と [APIのドキュメント](docs/api_doc.md)


# インストール
```shell
pip install -U open-creator
```

# 使用法
```python
import creator
```
## 1. スキルを作成
- [x] 1.1 リクエストから
```python
request = "help me write a script that can extracts a specified section from a PDF file and saves it as a new PDF"
skill = creator.create(request=request)
```

- [x] 1.2 会話履歴から（openaiメッセージ形式）
- [x] 1.3 スキルjsonファイルから
- [x] 1.4 messages_json_pathから
- [x] 1.5 コードファイルの内容から
```python
code_content = """
import json

def convert_to_openai_messages(messages):
    new_messages = []

    for message in messages:  
        new_message = {
            "role": message["role"],
            "content": ""
        }

        if "message" in message:
            new_message["content"] = message["message"]

        if "code" in message:
            new_message["function_call"] = {
                "name": "run_code",
                "arguments": json.dumps({
                    "language": message["language"],
                    "code": message["code"]
                }),
                # parsed_arguments isn't actually an OpenAI thing, it's an OI thing.
                # but it's soo useful! we use it to render messages to text_llms
                "parsed_arguments": {
                    "language": message["language"],
                    "code": message["code"]
                }
            }

        new_messages.append(new_message)

        if "output" in message:
            output = message["output"]

            new_messages.append({
                "role": "function",
                "name": "run_code",
                "content": output
            })

    return new_messages
"""
skill = creator.create(file_content=code_content)
```

- [x] 1.6 ドキュメントファイルの内容から

```python
doc_content = """
# Installation
\`\`\`shell
pip install langchain openai 
\`\`\`
The chat model will respond with a message.
\`\`\`python
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.chat_models import ChatOpenAI

chat = ChatOpenAI()
chat([HumanMessage(content="Translate this sentence from English to French: I love programming.")])
\`\`\`
you will get AIMessage(content="J'adore la programmation.", additional_kwargs={}, example=False)

We can then wrap our chat model in a ConversationChain, which has built-in memory for remembering past user inputs and model outputs.

\`\`\`python
from langchain.chains import ConversationChain  
  
conversation = ConversationChain(llm=chat)  
conversation.run("Translate this sentence from English to French: I love programming.")
\`\`\`
output: 'Je adore la programmation.'

conversation.run("Translate it to German.")

output: 'Ich liebe Programmieren.'
"""

skill = creator.create(file_content=doc_content)
```

- [x] 1.7 ファイルパスから
```python
skill = creator.create(file_path="creator/utils/partial_json_parse.py")
```

- [x] 1.8 huggingfaceから
```python
skill = creator.create(huggingface_repo_id="YourRepoID", huggingface_skill_path="your_skill_path")
```


## 2. スキルを保存
- [x] 2.1 デフォルトのパスに保存
```python
creator.save(skill)
```

- [x] 2.2 特定のスキルパスに保存
```python
creator.save(skill, skill_path="path/to/your/skill/directory")
```

- [x] 2.3 huggingfaceに保存
```python
creator.save(skill, huggingface_repo_id="YourRepoID")
```


## 3. スキルを検索
- [x] 3.1 ローカル検索
```python
skills = creator.search("your_search_query")
for skill in skills:
    print(skill)
```

## 4. スキルを使用
- [x] 4.1 スキルを使用
```python
from rich import print
skill = creator.search("pdf extract section")[0]
input_args = {
    "pdf_path": "creator.pdf",
    "start_page": 3,
    "end_page": 8,
    "output_path": "creator3-8.pdf"
}
skill.show()
resp = skill.run(input_args)
print(resp)
```

- [x] 4.2 リクエストによるスキルの使用
```python
request = "extract 3-8 page form creator.pdf and save it as creator3-8.pdf"
resp = skill.run(request)
```

# 貢献
コミュニティからの貢献を歓迎します！バグ修正、新機能、ライブラリに追加するスキルなど、あなたの貢献は価値があります。ガイドラインについては、[貢献ガイドライン](CONTRIBUTING_JA.md) をご覧ください。

## ライセンス

Open Creatorは [MIT](./LICENSE) ライセンスの下でライセンスされています。ソフトウェアのコピーを使用、コピー、変更、配布、サブライセンス、販売することが許可されています。
<br>

# 参照
> [1] Lucas, K. (2023). open-interpreter [Software]. Available at: https://github.com/KillianLucas/open-interpreter

> [2] Qian, C., Han, C., Fung, Y. R., Qin, Y., Liu, Z., & Ji, H. (2023). CREATOR: Disentangling Abstract and Concrete Reasonings of Large Language Models through Tool Creation. arXiv preprint arXiv:2305.14318.

> [3] Wang, G., Xie, Y., Jiang, Y., Mandlekar, A., Xiao, C., Zhu, Y., Fan, L., & Anandkumar, A. (2023). Voyager: An Open-Ended Embodied Agent with Large Language Models. arXiv preprint arXiv:2305.16291.

# 論文と引用

もし私たちの研究が役立つと思われる場合、引用を検討してください！

```bibtex
@techreport{gong2023opencreator,
  title = {Open-Creator: Bridging Code Interpreter and Skill Library},
  author = {Gong, Junmin and Wang, Sen and Zhao, Wenxiao and Guo, Jing},
  year = {2023},
  month = {9},
  url = {https://github.com/timedomain-tech/open-creator/blob/main/docs/tech_report/open-creator.pdf},
}
```
