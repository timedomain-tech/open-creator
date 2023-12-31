<h1 align="center">◓ Open Creator</h1>

<p align="center">
    <a href="https://discord.gg/eEraZEry53">
        <img alt="Discord" src="https://img.shields.io/discord/1153640284530417684?logo=discord&style=flat&logoColor=white"/>
    </a>
    <a href="README_JA.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
    <a href="README_ZH.md"><img src="https://img.shields.io/badge/文档-中文版-white.svg" alt="ZH doc"/></a>
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white&style=flat" alt="License"/>
    <a href="docs/tech_report/open-creator.pdf"><img src="https://img.shields.io/badge/arXiv-Paper-blue.svg" alt="paper"></a>
    <a href="https://huggingface.co/spaces/timedomain/skill-library-hub"><img src="https://img.shields.io/badge/%F0%9F%A4%97-Skills%20Library%20Hub-yellow" alt="huggingface"></a>
    <a href="docs/api_doc.md"><img src="https://readthedocs.org/projects/keytotext/badge/?version=latest" alt="docs"></a>
    <a href="[docs/api_doc.md](https://pepy.tech/project/open-creator)"><img src="https://static.pepy.tech/badge/open-creator" alt="downloads"></a>
    <a href="https://colab.research.google.com/github/timedomain-tech/open-creator/blob/main/docs/examples/08_creator_agent.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="colab"></a>
    <br><br>
    <b>构建您的定制技能库</b><br>
    一个开源的LLM工具，帮助您创建工具<br>
</p>

<br>

`open-creator` 是一个创新的包，设计用于从现有对话或需求中提取技能，保存它们，并在需要时检索它们。它提供了一种无缝的方法来整合和存档代码的精炼版本，将它们转化为随时可用的技能集，从而增强 [open-interpreter](https://github.com/KillianLucas/open-interpreter) 的功能。

![](docs/tech_report/figures/framework.png)


# 特点
- [x] **技能库**：高效地保存和检索结构化函数调用。
- [x] **反射代理**：自动结构化和分类您的函数调用。
- [x] **通过使用存储在 `~/.cache/open_creator/llm_cache/.langchain.db` 的SQLite缓存聊天LLM运行**：通过重用以前的运行节省时间和金钱。
- [x] **流**：流式处理您的函数调用
- [x] **社区中心**：分享并利用来自更广泛社区的技能。支持 [huggingface_hub](docs/skill-library-hub.md)。`langchain_hub` 还未支持。

# Updates
- [x] **2023-10-01**: 修复一些bugs，以及支持测试和重构代理agent
- [x] **2023-10-19**: 我们已修复了一些问题并对项目进行了优化。现在新增以下功能：
  - 创作者智能代理agent接口：`from creator.agents.creator_agent import open_creator_agent`
  - 命令行工具：详情请查阅：`creator -h`；启动服务器模式：`creator server`，之后访问 `http://localhost:8000/docs`；查看Streamlit界面演示：`creator ui`，然后访问 `http://localhost:8501/`
  - 更丰富的文档资料： [示例教程](docs/examples/01_skills_create.ipynb) 以及 [API参考手册](docs/api_doc.md)


# 安装
```shell
pip install -U open-creator
```

# 使用
```python
import creator
```
## 1. 创建技能
- [x] 1.1 来自请求
```python
request = "help me write a script that can extracts a specified section from a PDF file and saves it as a new PDF"
skill = creator.create(request=request)
```

- [x] 1.2 来自对话历史 (openai 消息格式)
- [x] 1.3 来自技能json文件
- [x] 1.4 来自消息json路径
- [x] 1.5 来自代码文件内容
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

- [x] 1.6 来自文档文件内容
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

- [x] 1.7 来自文件路径
```python
skill = creator.create(file_path="creator/utils/partial_json_parse.py")
```
- [x] 1.8 来自 huggingface
```python
skill = creator.create(huggingface_repo_id="YourRepoID", huggingface_skill_path="your_skill_path")
```


## 2. 保存技能
- [x] 2.1 保存到默认路径
```python
creator.save(skill)
```

- [x] 2.2 保存到特定技能路径
```python
creator.save(skill, skill_path="path/to/your/skill/directory")
```

- [x] 2.3 保存到 huggingface
```python
creator.save(skill, huggingface_repo_id="YourRepoID")
```

```
注意：在保存到huggingface之前，需要设置huggingface的身份验证方式。
推荐使用用户访问令牌的身份验证方式，请按照以下步骤操作：

1. 登录到你的Huggingface账号。
2. 在右上角的用户菜单中，选择"Settings"。
3. 在左侧导航栏中，选择"API Tokens"。
4. 点击"New Token"按钮创建一个新的访问令牌。
5. 输入一个描述性的名称，以便于识别该令牌的用途。
6. 选择适当的访问权限，确保你有足够的权限来上传和管理技能。
7. 点击"Create"按钮生成令牌。
8. 复制生成的访问令牌，并妥善保存。
9. 在Terminal中输入huggingface-cli login 
10. 输入上面复制的访问令牌，点击回车
现在你可以使用这个访问令牌来进行身份验证，以便在保存和上传技能时使用。确保在调用save函数之前，将访问令牌设置为环境变量HUGGINGFACE_TOKEN，这样API将能够使用该令牌进行身份验证。
```



## 3. 搜索技能

- [x] 3.1 本地搜索
```python
skills = creator.search("your_search_query")
for skill in skills:
    print(skill)
```

## 4. 使用技能
- [x] 4.1 使用技能
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

- [x] 4.2 以自然语言需求作为传参
```python
request = "extract 3-8 page form creator.pdf and save it as creator3-8.pdf"
resp = skill.run(request)
```



# 贡献
我们欢迎来自社区的贡献！无论是错误修复、新功能还是添加到库中的技能，您的贡献都是有价值的。请查看我们的 [贡献指南](CONTRIBUTING_ZH.md) 以获取指导原则。

## 许可证

Open Creator 根据 [MIT](./LICENSE) 许可证获得许可。您被允许使用、复制、修改、分发、再许可和销售软件的副本。
<br>

# 参考
> [1] Lucas, K. (2023). open-interpreter [软件]. 可以在这里获取：https://github.com/KillianLucas/open-interpreter

> [2] Qian, C., Han, C., Fung, Y. R., Qin, Y., Liu, Z., & Ji, H. (2023). CREATOR: 通过工具创建来区分大型语言模型的抽象和具体推理。arXiv 预印本 arXiv:2305.14318.

> [3] Wang, G., Xie, Y., Jiang, Y., Mandlekar, A., Xiao, C., Zhu, Y., Fan, L., & Anandkumar, A. (2023). Voyager: 一个使用大型语言模型的开放式实体代理。arXiv 预印本 arXiv:2305.16291.

# 论文与引用

如果您觉得我们的工作有用，请考虑引用我们！

```bibtex
@techreport{gong2023opencreator,
  title = {Open-Creator: Bridging Code Interpreter and Skill Library},
  author = {Gong, Junmin and Wang, Sen and Zhao, Wenxiao and Guo, Jing},
  year = {2023},
  month = {9},
  url = {https://github.com/timedomain-tech/open-creator/blob/main/docs/tech_report/open-creator.pdf},
}
```
