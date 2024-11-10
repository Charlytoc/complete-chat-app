import React from "react";
import { TSomething } from "../../types";

import { useLoaderData } from "react-router-dom";
import { Headline } from "../../components/Headline/Headline";
import { SubHeadline } from "../../components/SubHeadline/SubHeadline";
import { CallToAction } from "../../components/CallToAction/CallToAction";

export default function Root() {
  const data = useLoaderData() as { conversation: TSomething };

  return (
    <>
      <main>
        <Headline />
        <SubHeadline />
        <CallToAction />
      </main>
    </>
  );
}
