---
id: conversation
kind: archetype
summary: Support chronological exchange, response, and conversational state.
signals: [chat, messages, support, assistant, llm]
variants: [human, group, support, assistant]
compatible: [workspace, publication, guided-flow]
---

# Conversation

## Structural contract

Own chronology, identity, unread state, composer behavior, delivery state, and the active conversational context. In assistant variants, generated content is the product surface; keep chrome subordinate and code/content readable.

## Required states

Cover sending, streaming, typing, delivered, failed, retry, edited, deleted, long content, attachments, and empty history. Maintain keyboard and screen-reader continuity during updates.

## Blend contract

Pair with `workspace` for tools and history, `publication` for long answers, and `guided-flow` for structured collection inside a conversation.

## Anti-patterns

Avoid decorative motion competing with new messages, ambiguous sender identity, hidden failure states, automatic scroll that steals reading position, and forcing bubble geometry when the reference uses a document-like conversation.
