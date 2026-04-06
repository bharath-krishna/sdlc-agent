import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.adk.runners import Runner
from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService

from sdlc_agent.agent import app # import code from agent.py
from google.adk.memory import VertexAiMemoryBankService

# memory_service = VertexAiMemoryBankService(
#     project="krishproject87",
#     location="us-central1",
#     agent_engine_id="sdlc-agent-memory-service",
# )

# session_service = VertexAiSessionService(
#     project="krishproject87",
#     location="us-central1",
#     agent_engine_id="sdlc-agent-session-service",
# )


load_dotenv() # load API keys and settings
# Set a Runner using the imported application object
runner = InMemoryRunner(app=app)
# runner = Runner(
#     app=app,
#     memory_service=memory_service,
#     session_service=session_service
# )



async def main():
    try:  # run_debug() requires ADK Python 1.18 or higher:
        response = await runner.run_debug("I have accidentally delete postgres.tf terraform files from terraform dir of this doll_shop repo. find it and recreate it for me.")

    except Exception as e:
        print(f"An error occurred during agent execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())