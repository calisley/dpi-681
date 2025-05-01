from agents import Agent, WebSearchTool, Runner,function_tool
import asyncio

@function_tool
def square(x: float) -> float:
    """
    Returns the square of the number x.
    """
    return x * x

agent = Agent(
    name="Assistant",
    tools=[
        WebSearchTool(),   # gives you `search(query: str) → List[SearchResult]`
        square        # gives you `square(x: int) → int`
    ],
)

async def main():
    # The agent can now call `search("...")` or `square(7)` under the hood
    prompt = """
    What's the weather in Paris today?
    """
    result = await Runner.run(agent, prompt)
    print(result.final_output)

    prompt = """
    What is the square of 3.7545624?
    """
    result = await Runner.run(agent, prompt)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
