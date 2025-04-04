import os
import json
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from langchain.prompts import ChatPromptTemplate

# 设置 Tavily API Key
os.environ["TAVILY_API_KEY"] = "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"

# 定义系统提示词
system_prompt = """你是一个专业的数据爬虫专家，只回答与以下领域相关的问题：
- 数据爬取/网络爬虫技术
- 数据收集/信息采集
- 数据分析/数据处理
- 网页抓取/API调用
- 数据清洗/数据存储

请严格按以下规则执行：
1. 首先判断用户问题是否属于上述领域
2. 如果不属于，直接回复："你的问题与我的领域无关，我无法回答"
3. 如果属于，返回三个相关的结果: 主题："标题内容" 网址："完整URL"，不要添加任何解释或额外文字

判断标准：
- 问题是否涉及从网络或系统中获取、处理或分析数据
- 是否涉及自动化数据采集技术
- 是否与数据处理流程相关"""

# 定义回答提示词
answer_prompt = """
请严格按以下规则执行：
1.返回相关的结果(尽可能返回5条数据，可以用中国的搜索引擎/数据)  不要添加任何解释或额外文字  格式：主题："{相关的标题内容}" 网址："{完整URL}"，
"""

# 初始化通义千问
llm = ChatOpenAI(
    api_key="sk-38344865a8fc498a88b16d4cdaff768b",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",
)

# 创建带领域判断的提示模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

# 初始化 Tavily 搜索工具
tavily_search_tool = TavilySearch(max_results=5, topic="general")

# 创建 Agent
agent = create_react_agent(llm, [tavily_search_tool])


def get_ai_response(question):
    """获取AI响应并处理领域判断"""
    # 先进行领域判断
    judgment = llm.invoke(prompt_template.format(input=f"请判断以下问题是否属于数据爬取/处理领域，只能回答'是'或'否': {question}"))
    if "否" in judgment.content:
        print("你的问题与我的领域无关，我无法回答")
        return
    elif "无关" in judgment.content:
        print("你的问题与我的领域无关，我无法回答")
        return
    else :
        #  如果是领域内问题，执行Agent流程
        user_input = question + " " + answer_prompt
        finalMsg = ""
        for step in agent.stream({"messages": user_input}, stream_mode="values"):
            finalMsg = step["messages"][-1]
            step["messages"][-1].pretty_print()
            # 遍历消息链中的所有消息
        for item in finalMsg:
            if item[0] == 'content':  # 检查元组的第一个元素是否为'content'
                print(item)
                content_data = item[1]  # 获取内容部分

                # 处理内容数据，分割成单独的项目
                items = [i.strip() for i in content_data.split('\n') if i.strip()]

                # 解析每个项目
                result = []
                for item in items:
                    try:
                        # 分割主题和URL
                        theme_part, url_part = item.split('网址：')

                        # 清理数据
                        theme = theme_part.replace('主题："', '').replace('"', '').strip()
                        url = url_part.replace('"{', '').replace('}"', '').replace('"', '').strip()

                        result.append({
                            "主题": theme,
                            "网址": url
                        })
                    except ValueError:
                        continue  # 跳过格式不正确的行

                # 保存为JSON文件
                output_file = f"${question}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)

                print(f"数据已成功保存到 {output_file}")
                break  # 找到后立即退出循环





user_input = input("请输入你的问题：")
get_ai_response(user_input)
print('\n')
