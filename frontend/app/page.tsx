import { BookOpen, Sparkles, Image as ImageIcon, Layout } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50">
      <header className="px-6 py-4 flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center gap-2">
          <Sparkles className="w-8 h-8 text-indigo-600" />
          <span className="text-2xl font-bold tracking-tighter">NoTuMa</span>
        </div>
        <nav className="hidden md:flex items-center gap-6">
          <a href="#" className="text-sm font-medium hover:text-indigo-600 transition-colors">Projects</a>
          <a href="#" className="text-sm font-medium hover:text-indigo-600 transition-colors">Characters</a>
          <a href="#" className="text-sm font-medium hover:text-indigo-600 transition-colors">Exports</a>
        </nav>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors">
          Get Started
        </button>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-24 text-center">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6">
          Novel To <span className="text-indigo-600">Manga</span>
        </h1>
        <p className="max-w-2xl text-xl text-zinc-600 dark:text-zinc-400 mb-10">
          Transform your stories into high-fidelity manga and manhwa using advanced AI narrative analysis and professional-grade composition tools.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full">
          <div className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-left">
            <BookOpen className="w-10 h-10 text-indigo-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">Narrative Analysis</h3>
            <p className="text-zinc-600 dark:text-zinc-400">Intelligent parsing of EPUB, DOCX, and TXT with scene-level segmentation.</p>
          </div>
          <div className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-left">
            <ImageIcon className="w-10 h-10 text-indigo-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">AI Generation</h3>
            <p className="text-zinc-600 dark:text-zinc-400">Model Hub with BYOK support for NanoBanana, Replicate, and more.</p>
          </div>
          <div className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-left">
            <Layout className="w-10 h-10 text-indigo-600 mb-4" />
            <h3 className="text-xl font-bold mb-2">Pro Composition</h3>
            <p className="text-zinc-600 dark:text-zinc-400">Canvas-based editor for panels, speech bubbles, and manga effects.</p>
          </div>
        </div>
      </main>

      <footer className="px-6 py-8 border-t border-zinc-200 dark:border-zinc-800 text-center text-sm text-zinc-500">
        &copy; {new Date().getFullYear()} NoTuMa. All rights reserved.
      </footer>
    </div>
  );
}
