import { LoaderFunction } from "react-router-dom";
import { getPublicSitemapIndexes } from "../../modules/apiCalls";

export const dashboardLoader: LoaderFunction = async (): Promise<any> => {
  try {
    const res = await getPublicSitemapIndexes();
    return res;
  } catch (error) {
    console.error("Error loading conversation:", error);
    return null;
  }
};
