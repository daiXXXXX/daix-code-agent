def New_Agent(tools):
    import os

    from langchain.agents import create_agent
    from langchain.agents.middleware import ModelCallLimitMiddleware
    from langchain_openai import ChatOpenAI

    client = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "qwen3.5-flash"),
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_BASE_URL"],
        use_responses_api=False
    )

    agent = create_agent(
        model=client,
        tools=tools,
        system_prompt=(
            "你是一个 Code Agent，通过工具完成用户任务。"
            "先查看相关文件，再修改代码；修改后运行验证。"
            "根据工具实际返回结果判断是否完成，用中文回答。"
        ),
        middleware=[
            ModelCallLimitMiddleware(
                run_limit=10,
                exit_behavior="end"
            )
        ]
    )

    return agent