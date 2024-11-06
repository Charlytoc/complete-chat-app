import { LoaderFunctionArgs } from "react-router-dom";
import { getSuggestion, fetchArticles } from "../../modules/apiCalls";

export const articleLoader = async ({ params }: LoaderFunctionArgs) => {
  const { id } = params;
  if (id) {
    try {
      const data = await getSuggestion(id);
      return {
        article: data.article,
        suggestion: data.suggestion,
      };
    } catch (error) {
      console.error("Error fetching suggestion:", error);
      return { message: "Error fetching suggestion" };
    }
  } else {
    try {
      const data = await fetchArticles();
      return data;
    } catch (error) {
      console.error("Error fetching articles:", error);
      return { message: "Error fetching articles" };
    }
  }
};

