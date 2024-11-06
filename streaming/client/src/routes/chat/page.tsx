import React, { useEffect, useState } from "react";
import axios from "axios";
import "./page.css";
import { Message } from "../../components/Message/Message";
import { ChatInput } from "../../components/ChatInput/ChatInput";

import { useLoaderData } from "react-router-dom";
import { Sidebar } from "../../components/Sidebar/Sidebar";
import { useStore } from "../../modules/store";
import { TChatLoader, TMessage } from "../../types/chatTypes";
import { ChatHeader } from "../../components/ChatHeader/ChatHeader";
import toast, { Toaster } from "react-hot-toast";
import { playAudioFromBytes } from "../../modules/utils";
import socketManager from "../../modules/socketManager";

export default function ChatView() {
  const loaderData = useLoaderData() as TChatLoader;

  const { chatState, input, setInput, model, conversation, cleanAttachments } =
    useStore((state) => ({
      chatState: state.chatState,
      toggleSidebar: state.toggleSidebar,
      input: state.input,
      setInput: state.setInput,
      model: state.model,
      conversation: state.conversation,
      cleanAttachments: state.cleanAttachments,
    }));

  const [messages, setMessages] = useState(
    loaderData.conversation.messages as TMessage[]
  );

  useEffect(() => {
    socketManager.on("connect", () => {
      console.log("Connected to socket server");
    });

    socketManager.on("disconnect", () => {
      console.log("Disconnected from socket server");
    });

    const updateMessages = (chunk: string) => {
      const newMessages = [...messages];
      const lastMessage = newMessages[newMessages.length - 1];

      if (lastMessage && lastMessage.type === "assistant") {
        lastMessage.text += chunk;
      } else {
        const assistantMessage = {
          type: "assistant",
          text: chunk,
          attachments: [],
        };
        newMessages.push(assistantMessage);
      }
      return newMessages;
    };

    socketManager.on("response", (data) => {
      setMessages(updateMessages(data.chunk));
    });
    socketManager.on("audio-file", (audioFile) => {
      playAudioFromBytes(audioFile);
    });

    socketManager.on("responseFinished", (data) => {
      console.log("Response finished:", data);
      socketManager.disconnect();
    });

    return () => {
      socketManager.off("connect");
      socketManager.off("disconnect");
      socketManager.off("response");
      socketManager.off("audio-file");
      socketManager.off("responseFinished");
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages]);

  useEffect(() => {
    if (!conversation?.messages) return;
    setMessages(conversation?.messages);
  }, [conversation]);

  const handleSendMessage = async () => {
    if (input.trim() === "") return;

    socketManager.connect();
    const userMessage = {
      type: "user",
      text: input,
      attachments: chatState.attachments,
    };
    setMessages([...messages, userMessage]);

    try {
      socketManager.emit("message", {
        message: userMessage,
        context: messages.map((msg) => `${msg.type}: ${msg.text}`).join("\n"),
        model: model,
        conversation: conversation ? conversation : loaderData.conversation,
      });

      setInput("");
      cleanAttachments();
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleGenerateSpeech = async (text) => {
    try {
      socketManager.connect();

      // TODO: Send the token in every socket event, maybe we need to have a socket manager for the client ir order to have a straightforward interface
      // const token = localStorage.getItem("token");
      socketManager.emit("speech_request", {
        text,
      });
    } catch (error) {
      console.error("Error generating speech:", error);
    }
  };

  const handleGenerateImage = async (text) => {
    try {
      const response = await axios.post(
        "/generate_image/",
        { prompt: text },
        {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        }
      );
      const imageUrl = response.data.image_url;

      const imageMessage = {
        type: "assistant",
        text: "",
        attachments: [
          {
            type: "image",
            content: imageUrl,
            name: "Generated image",
          },
        ],
      };
      setMessages([...messages, imageMessage]);
    } catch (error) {
      console.error("Error generating image:", error);

      toast.error(
        "Error generating image: " + error.response?.data?.detail?.message ||
          error.message
      );
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && event.shiftKey) {
      setInput(event.target.value + "\n");
    } else if (event.key === "Enter") {
      handleSendMessage();
    } else {
      setInput(event.target.value);
    }
  };

  return (
    <>
      <Toaster />
      {chatState.isSidebarOpened && <Sidebar />}
      <div className="chat-container">
        <ChatHeader />
        <ChatInput
          handleSendMessage={handleSendMessage}
          handleKeyDown={handleKeyDown}
        />
        <div className="chat-messages">
          {messages &&
            messages.map((msg, index) => (
              <Message
                {...msg}
                key={index}
                onGenerateSpeech={handleGenerateSpeech}
                onGenerateImage={handleGenerateImage}
              />
            ))}
        </div>
      </div>
    </>
  );
}
