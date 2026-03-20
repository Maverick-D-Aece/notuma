'use client';

import { useState } from 'react';
import { Sparkles, Image as ImageIcon, Loader2 } from "lucide-react";
import Image from 'next/image';

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('');
  const [provider, setProvider] = useState('pollinations');
  const [apiKey, setApiKey] = useState('');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/image/generate-panel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          provider,
          api_key: apiKey || undefined,
        }),
      });
      const data = await response.json();
      setImageUrl(data.image_url);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50">
      <header className="px-6 py-4 flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center gap-2">
          <Sparkles className="w-8 h-8 text-indigo-600" />
          <span className="text-2xl font-bold tracking-tighter">NoTuMa</span>
        </div>
      </header>

      <main className="flex-1 container mx-auto py-12 px-6 max-w-4xl">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-extrabold tracking-tight mb-2 flex items-center justify-center gap-2">
            <ImageIcon className="w-8 h-8 text-indigo-600" />
            High-Fidelity Generation
          </h1>
          <p className="text-zinc-500">Generate professional manga panels using your favorite AI providers.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-1 space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-semibold uppercase tracking-wider text-zinc-500">Provider</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 focus:ring-2 focus:ring-indigo-600 outline-none transition-all"
              >
                <option value="pollinations">Pollinations (Free)</option>
                <option value="openai">OpenAI</option>
                <option value="stability">Stability AI</option>
                <option value="replicate">Replicate</option>
                <option value="nanobanana">NanoBanana</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold uppercase tracking-wider text-zinc-500">API Key (BYOK)</label>
              <input
                type="password"
                placeholder="Enter your API key..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 focus:ring-2 focus:ring-indigo-600 outline-none transition-all"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold uppercase tracking-wider text-zinc-500">Prompt</label>
              <textarea
                rows={4}
                placeholder="A samurai fighting in the rain, manga style, high contrast, speed lines..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 focus:ring-2 focus:ring-indigo-600 outline-none transition-all resize-none"
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading || !prompt}
              className="w-full py-4 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                'Generate Panel'
              )}
            </button>
          </div>

          <div className="md:col-span-2">
            <div className="h-full min-h-[400px] border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-2xl flex items-center justify-center bg-zinc-50/50 dark:bg-zinc-900/50 overflow-hidden relative">
              {imageUrl ? (
                <Image src={imageUrl} alt="Generated Panel" width={1024} height={1024} className="w-full h-full object-contain" />
              ) : (
                <div className="text-center p-8">
                  <div className="w-16 h-16 bg-zinc-100 dark:bg-zinc-800 rounded-full flex items-center justify-center mx-auto mb-4">
                    <ImageIcon className="w-8 h-8 text-zinc-400" />
                  </div>
                  <p className="text-zinc-500">Your generated panel will appear here.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
