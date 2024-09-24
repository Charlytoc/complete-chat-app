import { LoaderFunction } from "react-router-dom";
import { getSuggestion, fetchArticles } from "../../modules/apiCalls";

export const articleLoader: LoaderFunction = async ({
  request,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
}): Promise<{ article: any; suggestions: any } | { message: string }> => {
  const url = new URL(request.url);
  const articleSlug = url.searchParams.get("article");
  if (articleSlug) {
    try {
      const data = await getSuggestion(articleSlug);

      return data;
    } catch (error) {
      console.error("Error fetching suggestion:", error);
      return { message: "Error fetching suggestion" };
    }
  } else {
    const data = fetchArticles();
    return data;
  }
};
