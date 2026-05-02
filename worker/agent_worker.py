import os
from livekit import rtc
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import openai

# Set agent name for dispatch
os.environ["AGENT_NAME"] = os.getenv("AGENT_NAME", "voice-agent")

async def entrypoint(ctx: JobContext):
    print(f"[AGENT] Room connected: {ctx.room.name}")
    
    agent_config = get_agent_config()
    
    initial_ctx = llm.ChatContext()
    initial_ctx.messages.append(
        llm.ChatMessage(
            role=llm.ChatRole.SYSTEM,
            content=agent_config["system_prompt"]
        )
    )

    agent = openai.realtime.RealtimeModel(
        instructions=agent_config["system_prompt"],
        voice=agent_config.get("voice", "alloy"),
    )

    @ctx.room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant: rtc.RemoteParticipant):
        print(f"[AGENT] Track subscribed from {participant.identity}")
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            agent.start(ctx.room, participant)

    await ctx.connect()


def get_agent_config() -> dict:
    return {
        "system_prompt": os.getenv("AGENT_SYSTEM_PROMPT", "You are a helpful AI assistant."),
        "voice": os.getenv("AGENT_VOICE", "alloy"),
    }


if __name__ == "__main__":
    agent_name = os.getenv("AGENT_NAME", "voice-agent")
    print(f"[WORKER] Starting with agent_name: {agent_name}")
    
    # Create worker options with agent name
    opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
    )
    
    cli.run_app(opts)
