Hi, my name is Nguyen (a very Vietnamese name)!
I do this project as an assistance that using LLM model (provided by Openrouter) and using [DSPy framework](https://dspy.ai/).
In the project I also using MCP as an MCP client and a each MCP server (collection of set of tool) will be managed by an agent, because by that approach we will prevent the warning like
```
Exceeding total tools limit
You have 54 tools from enabled servers. Too many tools can
degrade performance, and some models may not respect more
than 40 tools.
```
Well the whole project of course written by my and [Cursor](cursor.com) for code and [Stitch](https://stitch.withgoogle.com/) for design the UI
If you want to know more about the project specialy in architect then in generaly it's a graph of agent working together.
When you ask a question, a planing and output advisor (how to display the answer) will parallel process. Then the plan will be delegate to each agent to execute
After all, the conclusion will collecting all data from the tool agent make the final answer as output advisor and response to you.
Finally, a background task run after response (provided by python FastAPI framework) will write your question and the LLM response to the Weaviate Database
That all for now.

Road map: A few more thing I really want to add soon:
1. Feedback from user to the answer (to help evaluation and optimise)
2. Socket streaming thinking process and data from the tool to UI
3. Edit a question
