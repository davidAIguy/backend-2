import os
from livekit import rtc
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import openai


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    print(f"Room connected: {ctx.room.name}")
    
    agent_config = get_agent_config()
    
    initial_ctx = llm.ChatContext()
    initial_ctx.messages.append(
        llm.ChatMessage(
            role=llm.ChatRole.SYSTEM,
            content=agent_config["system_prompt"]
        )
    )

    async def before_first_reply(agent, chat_ctx):
        chat_ctx.messages.append(
            llm.ChatMessage(
                role=llm.ChatRole.ASSISTANT,
                content="Hello! How can I help you today?"
            )
        )

    agent = openai.realtime.RealtimeModel(
        instructions=agent_config["system_prompt"],
        voice=agent_config.get("voice", "alloy"),
    )

    @ctx.room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant: rtc.RemoteParticipant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            agent.start(ctx.room, participant)

    await agent.spawn(ctx.room)


def get_agent_config() -> dict:
    return {
        "system_prompt": os.getenv("AGENT_SYSTEM_PROMPT", "You are a helpful AI assistant."),
        "voice": os.getenv("AGENT_VOICE", "alloy"),
    }


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
