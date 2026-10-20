# Emcee as a Foundry hosted agent (Responses protocol on port 8088, via agent-framework-foundry-hosting).
# Build from the REPO ROOT so the skills and the episode data can be copied in:
#   docker build -f agents/Dockerfile -t emcee .
#   docker run --rm -p 8088:8088 -e EMCEE_MOCK=1 -e EMCEE_SITE_URL=http://host.docker.internal:8000 emcee
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8088 \
    EMCEE_MARP=off

WORKDIR /app

COPY agents/requirements.txt agents/requirements.txt
RUN pip install -r agents/requirements.txt

# The specialists load these SKILL.md files at runtime and run check.py (which reads the episode data).
COPY .github/skills/mm-recap .github/skills/mm-recap
COPY .github/skills/mm-deck .github/skills/mm-deck
COPY data/episodes.json data/seasons.json data/
COPY data/youtube/videos.json data/youtube/videos.json
COPY agents agents

RUN useradd --create-home --uid 10001 emcee && mkdir -p agents/.out && chown -R emcee /app
USER emcee

EXPOSE 8088
CMD ["python", "-m", "agents.emcee.hosted"]
