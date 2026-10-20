---
episode: s4-e09
kind: recap
title: "Building voice agents in Foundry: from conversation to diagnosis"
generated_by: mm-recap
grounding: transcript
sources:
  - https://www.youtube.com/watch?v=rBFQLt3StVI
  - https://www.youtube.com/watch?v=rBFQLt3StVI&t=114s
  - https://www.youtube.com/watch?v=rBFQLt3StVI&t=436s
  - https://www.youtube.com/watch?v=rBFQLt3StVI&t=854s
  - https://www.youtube.com/watch?v=rBFQLt3StVI&t=2047s
  - https://www.youtube.com/watch?v=rBFQLt3StVI&t=2688s
  - https://www.youtube.com/watch?v=rBFQLt3StVI&t=3069s
  - https://aka.ms/model-mondays/collection
---

# Building voice agents in Foundry: from conversation to diagnosis

A convincing voice demo is only the beginning: you also need to connect tools, handle interruptions, and understand why a conversation went wrong. In S4-E09, hosted by Gustavo Cordido, guests explore speech models and voice agents in Microsoft Foundry, with a mortgage-assistance walkthrough you can follow from conversation to execution traces.

## What we covered

- **[Weekly news highlights](https://www.youtube.com/watch?v=rBFQLt3StVI&t=114s)** - The roundup covered specialized decision models, Claude Haiku, cost-efficient evaluations, Grok, and Maia infrastructure. Its practical theme was choosing models and evaluation strategies around workload needs, latency, and cost.
- **[Voice agents in Foundry](https://www.youtube.com/watch?v=rBFQLt3StVI&t=436s)** - Guests distinguished standalone Voice Live API, Voice Live connected to an existing Foundry agent, and the integrated voice-agent experience, described as public preview. Your choice depends on where your agent lives and how much lifecycle management you want brought together.
- **[A finance agent, end to end](https://www.youtube.com/watch?v=rBFQLt3StVI&t=854s)** - The demo walked through caller verification, collecting financing needs, calculating indicative offers, and selecting a human loan officer. The playground walkthrough then showed model and voice selection, rapid testing, and traces for diagnosing misunderstood amounts and mistimed turn taking.
- **[Audio models for listening and speaking](https://www.youtube.com/watch?v=rBFQLt3StVI&t=2047s)** - Guests contrasted processing recorded audio with streaming partial and final transcripts for live conversations. Speech-generation demos explored expressiveness, responsiveness, and maintaining a recognizable voice across languages.
- **[Architectures and implementation Q&A](https://www.youtube.com/watch?v=rBFQLt3StVI&t=2688s)** - Speech-to-speech, semi-cascaded, cascaded, and bring-your-own-model approaches offer different control over recognition, reasoning, and output voices. The [customer discussion](https://www.youtube.com/watch?v=rBFQLt3StVI&t=3069s) covered contact centers, interactive training, personal assistants, and multilingual configuration.

## Key takeaways

1. **Pick your integration path before picking a voice.** If you already have an agent and tools, the session outlines ways to add voice rather than rebuild everything.
2. **Treat traces as part of the experience.** The finance demo shows why a plausible answer is not enough: inspect recognized input and tool execution when a number is misunderstood or a pause triggers an unwanted response.
3. **Match the pipeline to your constraints.** The session positions speech-to-speech for fluid interaction and cascaded approaches for more control over individual stages, including recognition and voice customization.
4. **Plan multilingual behavior deliberately.** The Q&A distinguishes regional defaults, switching languages on request, and dialect-specific customization; your audience's needs should guide the configuration.

## Try it yourself

- Start with the [finance walkthrough](https://www.youtube.com/watch?v=rBFQLt3StVI&t=854s). Map its verification, calculation, and handoff steps to one workflow you want to support, then revisit how traces expose conversation failures.
- Explore the [episode's linked resource collection](https://aka.ms/model-mondays/collection) for follow-up learning.

## Watch the replay

https://www.youtube.com/watch?v=rBFQLt3StVI · Approximately 62 minutes · Hosted by Gustavo Cordido

## Sources

- Episode transcript and timestamped chapters: https://www.youtube.com/watch?v=rBFQLt3StVI
- Resource collection linked in the video description: https://aka.ms/model-mondays/collection

## Notes for reviewer

- Grounded in the full cached transcript; fetching fresh transcripts was IP-blocked.
- Guest names are absent from the structured episode record, so this draft uses "guests."
- Source status says scheduled despite an available recording; treated as completed.
- News names and availability claims need announcement-link verification; see the companion highlights draft.
