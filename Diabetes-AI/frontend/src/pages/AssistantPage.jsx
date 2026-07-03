import { useState } from "react";
import { askAssistant } from "../api";

const starterPrompts = [
  "Explain the difference between Type 1 and Type 2 diabetes.",
  "Why are glucose and BMI important for diabetes risk?",
  "Give simple prevention tips with diet and exercise suggestions.",
];

export default function AssistantPage({ predictionContext }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return;
    const nextMessages = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);
    try {
      const data = await askAssistant({
        message: text,
        prediction_context: predictionContext,
        history: nextMessages.slice(-8),
      });
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (error) {
      const timedOut = error.code === "ECONNABORTED";
      const message = timedOut
        ? "The assistant took too long to respond. Please try again in a moment, or check that the backend Gemini model is available."
        : "The assistant could not connect to the backend right now. Please check that the FastAPI server is running and try again.";
      setMessages((prev) => [...prev, { role: "assistant", content: message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">AI Health Assistant</h1>
      <p className="page-subtitle">
        Ask diabetes-awareness questions in simple language. This assistant never diagnoses or prescribes medicine.
      </p>
      <div className="disclaimer">
        This application is intended for educational and awareness purposes only. It is not a substitute for
        professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.
      </div>

      <div className="card">
        <div className="starter-wrap">
          {starterPrompts.map((prompt) => (
            <button key={prompt} className="secondary-btn" onClick={() => sendMessage(prompt)}>
              {prompt}
            </button>
          ))}
        </div>

        <div className="chat-box">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-msg ${msg.role}`}>
              <div className="chat-role">{msg.role === "user" ? "You" : "Assistant"}</div>
              <div className="chat-content">{msg.content}</div>
            </div>
          ))}
          {loading && (
            <div className="chat-msg assistant">
              <div className="chat-role">Assistant</div>
              <div className="chat-content">Thinking...</div>
            </div>
          )}
        </div>

        <div className="chat-input-wrap">
          <input
            className="chat-input"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                sendMessage(input);
              }
            }}
            placeholder="Ask about symptoms, prevention, risk factors, glucose, BMI, or your recent prediction..."
            disabled={loading}
          />
          <button className="primary-btn" onClick={() => sendMessage(input)} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
