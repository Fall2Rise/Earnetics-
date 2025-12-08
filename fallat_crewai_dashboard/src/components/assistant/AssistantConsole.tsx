import React, { useMemo, useState } from "react";

const greetingPresets = [
  "Systems online. How can I assist you today?",
  "Operational control ready. What should we optimise?",
  "All agents synced. Give me a mission.",
];

type AssistantMessage = {
  id: string;
  from: "assistant" | "operator";
  text: string;
};

const responsePresets: Record<string, string> = {
  credentials:
    "Keeper can audit credentials. Ask me to \"audit credentials\" and I will run the diagnostics for you.",
  affiliate:
    "The Affiliate Expansion Division is primed. I can fetch the latest partner shortlist or launch new campaigns on request.",
  status:
    "System health is steady. Pulse monitors uptime while Sentinel watches for anomalies. Request a \"status report\" any time.",
};

const defaultResponse =
  "I'm processing that. For deeper tasks, let me know if you want to open a specific panel or run an operation.";

export const AssistantConsole: React.FC = () => {
  const [messages, setMessages] = useState<AssistantMessage[]>(() => [
    {
      id: crypto.randomUUID(),
      from: "assistant",
      text: greetingPresets[Math.floor(Math.random() * greetingPresets.length)],
    },
  ]);
  const [input, setInput] = useState("");

  const suggestions = useMemo(
    () => [
      "Show integration status",
      "Audit credentials",
      "Run affiliate cycle",
      "Open support dashboard",
    ],
    []
  );

  const handleSubmit = (value: string) => {
    if (!value.trim()) return;
    const lower = value.toLowerCase();
    const keywords = Object.keys(responsePresets);
    const matchedKey = keywords.find((key) => lower.includes(key));

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), from: "operator", text: value.trim() },
      {
        id: crypto.randomUUID(),
        from: "assistant",
        text: matchedKey ? responsePresets[matchedKey] : defaultResponse,
      },
    ]);
    setInput("");
  };

  return (
    <aside className="assistant-console" aria-live="polite">
      <div className="assistant-avatar">
        <div className="avatar-core" />
        <div className="avatar-ring" />
        <div className="avatar-particles" />
      </div>
      <div className="assistant-panel glass-panel">
        <header className="assistant-header">
          <div>
            <p className="assistant-name">NEXA-9</p>
            <p className="assistant-role">Strategic Operator Liaison</p>
          </div>
          <div className="assistant-status">
            <span className="status-indicator" /> Online
          </div>
        </header>

        <div className="assistant-log">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`assistant-message assistant-message--${message.from}`}
            >
              <span>{message.text}</span>
            </div>
          ))}
        </div>

        <div className="assistant-input">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                handleSubmit(input);
              }
            }}
            placeholder="Ask your assistant…"
          />
          <button type="button" onClick={() => handleSubmit(input)}>
            Send
          </button>
        </div>

        <div className="assistant-suggestions">
          {suggestions.map((suggestion) => (
            <button key={suggestion} type="button" onClick={() => handleSubmit(suggestion)}>
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};
