"use client";
import React, { useState, useRef } from "react";

export default function Page() {
  const [form, setForm] = useState({
    name: "",
    company: "",
    product_company: "",
    product_description: "",
  });
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const eventSourceRef = useRef<EventSource | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const startStreaming = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setEmail("");
    setLoading(true);

    // You can change this URL to your API route or backend endpoint
    const res = await fetch("http://localhost:8000/generate-email-stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    if (!res.ok) {
      setError("Failed to generate email.");
      setLoading(false);
      return;
    }

    if (eventSourceRef.current) eventSourceRef.current.close();
    eventSourceRef.current = new EventSource(
      "http://localhost:8000/generate-email-stream"
    );

    eventSourceRef.current.onmessage = (event) => {
      setEmail((prev) => prev + event.data);
    };

    eventSourceRef.current.onerror = () => {
      setLoading(false);
      eventSourceRef.current?.close();
    };
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#181E29] via-[#131622] to-[#0B0D13] px-2 py-12">
      <div className="w-full max-w-2xl mx-auto rounded-3xl shadow-2xl p-10 bg-white/10 backdrop-blur-lg border border-white/10">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-white mb-8 tracking-tight text-center drop-shadow-md">
          Sales Email Magic
        </h1>
        <p className="mb-10 text-lg text-gray-200 text-center max-w-lg mx-auto">
          Instantly craft bespoke B2B cold emails, tailored for your product and target company — see your AI message appear in real time.
        </p>

        <form
          onSubmit={startStreaming}
          className="space-y-6"
          autoComplete="off"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div>
              <label className="block mb-2 text-gray-300 text-xs font-medium tracking-wide">
                Recipient Name
              </label>
              <input
                id="name"
                name="name"
                required
                value={form.name}
                onChange={handleChange}
                className="w-full rounded-xl bg-white/10 border border-gray-700 px-4 py-3 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-600 focus:bg-white/20 outline-none transition"
                placeholder="e.g. John Smith"
                autoComplete="off"
              />
            </div>
            <div>
              <label className="block mb-2 text-gray-300 text-xs font-medium tracking-wide">
                Recipient Company
              </label>
              <input
                id="company"
                name="company"
                required
                value={form.company}
                onChange={handleChange}
                className="w-full rounded-xl bg-white/10 border border-gray-700 px-4 py-3 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-600 focus:bg-white/20 outline-none transition"
                placeholder="e.g. Rocket Mortgage"
                autoComplete="off"
              />
            </div>
            <div>
              <label className="block mb-2 text-gray-300 text-xs font-medium tracking-wide">
                Your Company
              </label>
              <input
                id="product_company"
                name="product_company"
                required
                value={form.product_company}
                onChange={handleChange}
                className="w-full rounded-xl bg-white/10 border border-gray-700 px-4 py-3 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-600 focus:bg-white/20 outline-none transition"
                placeholder="e.g. Kastle"
                autoComplete="off"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block mb-2 text-gray-300 text-xs font-medium tracking-wide">
                Product Description
              </label>
              <textarea
                id="product_description"
                name="product_description"
                required
                rows={3}
                value={form.product_description}
                onChange={handleChange}
                className="w-full rounded-xl bg-white/10 border border-gray-700 px-4 py-3 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-600 focus:bg-white/20 outline-none transition resize-none"
                placeholder="What does your product do?"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-400 hover:brightness-110 transition rounded-xl py-3 font-semibold text-lg text-white shadow-xl disabled:opacity-60"
          >
            {loading ? "Generating..." : "Generate Email"}
          </button>
        </form>

        {error && (
          <div className="mt-4 text-center text-red-400 font-medium animate-pulse">
            {error}
          </div>
        )}

        <div className="mt-10">
          <label className="block mb-2 text-gray-300 text-xs font-semibold tracking-wide">
            Generated Email
          </label>
          <pre className="min-h-[140px] whitespace-pre-wrap font-mono bg-white/5 rounded-xl border border-gray-800 p-6 text-base text-white relative transition-all duration-300">
            {email}
            {loading && (
              <span className="text-blue-400 animate-pulse absolute -right-4 bottom-4 text-2xl select-none">
                |
              </span>
            )}
          </pre>
        </div>
      </div>
    </div>
  );
}
