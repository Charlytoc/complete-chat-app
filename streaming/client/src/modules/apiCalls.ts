import axios from "axios";
import { API_URL, PUBLIC_TOKEN } from "./constants";

export const initConversation = async ({isPublic = false}) => {
  const endpoint = API_URL + "/v1/messaging/conversations";

  try {
    const { token, tokenType } = isPublic
      ? { token: PUBLIC_TOKEN, tokenType: "PublishToken" }
      : { token: localStorage.getItem("token"), tokenType: "Token" };

    if (!token) throw Error("No token found, impossible to init conversation");

    const response = await axios.post(
      endpoint,
      {},
      {
        headers: {
          Authorization: `${tokenType} ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error initiating conversation:", error);
    throw error;
  }
};

export const getConversation = async (conversationId: string) => {
  const endpoint = `${API_URL}/v1/messaging/conversations/${conversationId}`;

  try {
    const token = localStorage.getItem("token");
    if (!token) throw "No token found, impossible to get conversation";

    const response = await axios.get(endpoint, {
      headers: {
        Authorization: `Token ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching conversation:", error);
    throw error;
  }
};


export const getSuggestion = async (articleSlug: string) => {
  const endpoint = `${API_URL}/v1/seo/suggestions/${articleSlug}`;

  try {
    const response = await axios.get(endpoint);
    return response.data;
  } catch (error) {
    console.error("Error fetching suggestion:", error);
    throw error;
  }
};


export const fetchArticles = async () => {
  try {
    const response = await axios.get(API_URL + "/v1/seo/suggestions");
    if (response.status === 200) {
      return response.data
    } else {
      console.error("Error fetching articles");
    }
  } catch (error) {
    console.error("Error fetching articles", error);
  }
};