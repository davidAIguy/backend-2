import os
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import openai, ai_coustics

load_dotenv()

AGENT_NAME = os.getenv("AGENT_NAME", "voice-agent")
SYSTEM_PROMPT = os.getenv("AGENT_SYSTEM_PROMPT", "You are a helpful AI voice assistant. Be friendly and concise.")
VOICE = os.getenv("AGENT_VOICE", "alloy")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)


server = AgentServer()


@server.rtc_session(agent_name=AGENT_NAME)
async def voice_agent(ctx: agents.JobContext):
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice=VOICE,
        )
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    print(f"[WORKER] Starting voice-agent with name: {AGENT_NAME}")
    agents.cli.run_app(server)
