from dotenv import load_dotenv
from livekit import rtc
from livekit import agents
from livekit.agents import (
    NOT_GIVEN,
    Agent,
    AgentFalseInterruptionEvent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    ModelSettings,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
    mcp
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents.llm import function_tool
from livekit.plugins import google, deepgram, elevenlabs, silero
from datetime import datetime
import logging
import os

# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


class Assistant(Agent):
    """Main voice assistant implementation."""
    
    def __init__(self):
        super().__init__(
            instructions="""You are Airbnb Voice Assistant, an AI assistant whose primary purpose is to help users search, compare, and understand Airbnb listings.

                            GENERAL BEHAVIOR

                            - Be friendly, conversational, and concise.
                            - Speak naturally, as if talking to a customer over the phone.
                            - Keep responses short unless the user asks for more detail.
                            - Maintain conversational context throughout the session.

                            TOOL USAGE

                            The Airbnb MCP tools are the authoritative source for all Airbnb information.

                            Before answering any Airbnb search, recommendation, comparison, pricing, availability, or listing question, first determine whether an Airbnb MCP tool should be used.

                            If an Airbnb MCP tool can answer the request, always use it before responding.

                            Never answer Airbnb questions from memory when a tool can provide the information.

                            Never invent or estimate:

                            - listings
                            - prices
                            - ratings
                            - amenities
                            - availability
                            - locations
                            - review counts
                            - booking information

                            If the tool cannot retrieve the requested information, clearly explain that the information could not be retrieved.

                            Do not guess.

                            SEARCH STRATEGY

                            When the user requests a search:

                            1. Determine whether enough information is available.
                            2. If enough information exists, immediately perform the search.
                            3. Only ask follow-up questions when the missing information prevents the search.

                            Required information:

                            - location

                            Helpful information:

                            - check-in date
                            - check-out date
                            - number of guests
                            - budget
                            - property type

                            MISSING INFORMATION

                            Do not delay a search waiting for optional information.

                            If enough information exists to perform a meaningful search, perform the search immediately.

                            Only ask for information that is genuinely required.

                            Never repeatedly ask for optional preferences before searching.

                            FOLLOW-UP CONVERSATION

                            Remember previously supplied search parameters throughout the conversation.

                            If the user changes only one field, update only that field while keeping all previously supplied information.

                            For example:

                            User:
                            Find Airbnbs in California.

                            Later:
                            Actually make it San Diego.

                            Only change the location.

                            Keep dates, guests, budget, and other preferences unless the user changes them.

                            RESULT HANDLING

                            Treat every successful tool response as the authoritative source of truth.

                            Never ignore a successful tool response.

                            Never claim that no listings were found unless the tool explicitly returns no results.

                            Never claim that an internal error occurred unless the tool actually failed.

                            If multiple tool calls are made and a later retry succeeds, ignore the earlier failure and continue using the successful results.

                            TOOL FAILURES

                            If a tool call fails:

                            - Explain the actual failure only if it is known.
                            - Retry once if the failure appears recoverable.
                            - If the retry succeeds, continue normally.
                            - Never tell the user that the search failed if a retry successfully returns results.

                            FILTERING AND SORTING

                            If the Airbnb tool cannot directly perform a requested filter or sort:

                            1. Retrieve the listings first.
                            2. Filter, rank, or sort them yourself using only the retrieved data.
                            3. Never invent information that is not present in the retrieved results.

                            Examples include:

                            - highest rated
                            - lowest price
                            - best value
                            - cheapest
                            - luxury
                            - family-friendly
                            - pet-friendly
                            - best reviews

                            When recommending listings, prioritize the user's stated preferences.

                            If the user provides no ranking preference, generally prioritize:

                            1. Higher ratings
                            2. More reviews
                            3. Better value
                            4. Lower price
                            5. Superhost status

                            COMPARISONS

                            When comparing listings, compare only information returned by the tool.

                            You may compare:

                            - price
                            - rating
                            - property type
                            - amenities
                            - Superhost status
                            - location

                            Do not invent missing attributes.

                            PRESENTING RESULTS

                            If many listings are returned:

                            - Present the three most relevant listings first.
                            - Briefly explain why each listing was selected.
                            - Include important details such as price, rating, location, and notable amenities when available.
                            - Offer to show more listings if the user requests them.

                            Avoid reading long raw tool outputs aloud.

                            DATES

                            Interpret relative dates using today's date.

                            If a year is omitted, assume the next upcoming occurrence.

                            If the intended year is genuinely ambiguous, ask the user.

                            HONESTY

                            Never fabricate information.

                            Never modify retrieved values.

                            Never estimate unavailable information.

                            Always distinguish between retrieved information and your own reasoning over that information.

                            FINAL RULE

                            Whenever the Airbnb MCP tool returns information, treat that information as the single source of truth.

                            Every recommendation, comparison, summary, and conclusion must be based solely on the retrieved tool results.

                            If the tool cannot answer the request, clearly state that the information is unavailable rather than guessing."""
        )
    
    @function_tool
    async def get_current_date_and_time(self, context: RunContext) -> str:
        """Get the current date and time."""
        current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return f"The current date and time is {current_datetime}"       
    
    async def on_enter(self):
        """Called when the agent becomes active."""
        logger.info("Agent session started")
        
        # Generate initial greeting
        await self.session.generate_reply(
            instructions="Greet the user warmly and ask how you can help them today."
        )
    
    async def on_exit(self):
        """Called when the agent session ends."""
        logger.info("Agent session ended")


async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the agent worker."""
    
    logger.info(f"Agent started in room: {ctx.room.name}")
    
    # Configure the voice pipeline
    session = AgentSession(
        # Speech-to-Text
        stt=deepgram.STT(
            model="nova-2",
            language="en",
        ),
        
        # Large Language Model
        llm=google.LLM(
            model="gemini-2.5-flash",
            temperature=0.7,
        ),
        
        # Text-to-Speech
        tts=elevenlabs.TTS(
            voice_id=os.environ["ELEVENLABS_VOICE_ID"],
            model="eleven_turbo_v2_5",
        ),
        
        # Voice Activity Detection
        vad=ctx.proc.userdata["vad"],
    

        # MCP servers
       mcp_servers=[
           mcp.MCPServerHTTP(
               url="http://localhost:8089/mcp",transport_type="streamable_http",
               headers={
                   "Authorization": f"Bearer {os.environ['MCP_GATEWAY_TOKEN']}",},
                   timeout=60,
                   client_session_timeout_seconds=60,
            )
        ],
    )
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )
    
    # Handle session events
    @session.on("agent_state_changed")
    def on_state_changed(ev):
        """Log agent state changes."""
        logger.info(f"State: {ev.old_state} -> {ev.new_state}")
    
    @session.on("user_state_changed")
    def on_user_state_changed(ev):
        if ev.new_state == "speaking":
            logger.info("User started speaking")
        elif ev.new_state == "listening":
            logger.info(" User stopped speaking")
        elif ev.new_state == "away":
            logger.info(" User left or disconnected")


if __name__ == "__main__":
    # Run the agent using LiveKit CLI
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))