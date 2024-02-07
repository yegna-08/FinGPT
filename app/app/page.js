import React from "react";
import Navigation from "@/components/Navigation";

export default function Index() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />

      <div className="hero min-h-screen">
        <div className="hero-content text-center text-purple-700">
          <div className="max-w-md">
            <h1 className="text-5xl font-bold">Hello there</h1>
            <p className="text-l py-6">
            This website serves as a repository for Financial Generative Pre-trained Transformer models, 
            offering users a centralized platform to explore and access a variety of open-source models tailored for financial analysis and forecasting.
            </p>
            <form
              action="https://github.com/AI4Finance-Foundation/FinGPT?tab=readme-ov-file"
              method="post"
              target="_blank"
            >
              <button className="btn hover:btn-neutral">Paper</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
