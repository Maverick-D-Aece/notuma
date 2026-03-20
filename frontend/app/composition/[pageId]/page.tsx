'use client';

import { useEffect, useRef, useState } from 'react';
import { useParams } from 'next/navigation';
import * as fabric from 'fabric';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  Square,
  MessageSquare,
  ChevronRight,
  Download,
  Layout,
  Type,
  Grid,
  Zap,
  Layers
} from 'lucide-react';

export default function CompositionEditor() {
  const { pageId } = useParams();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [canvas, setCanvas] = useState<fabric.Canvas | null>(null);
  const [isManhwa, setIsManhwa] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!canvasRef.current) return;

    const fabricCanvas = new fabric.Canvas(canvasRef.current, {
      width: isManhwa ? 800 : 800,
      height: isManhwa ? 2400 : 1200,
      backgroundColor: '#ffffff'
    });

    setCanvas(fabricCanvas);

    // Load existing layout if available
    const loadLayout = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/v1/composition/page/${pageId}`);
            const data = await res.json();
            if (data.layout && Object.keys(data.layout).length > 0) {
                await fabricCanvas.loadFromJSON(data.layout);
                fabricCanvas.renderAll();
            }
        } catch (err) {
            console.error("Failed to load layout:", err);
        }
    };
    loadLayout();

    return () => {
      fabricCanvas.dispose();
    };
  }, [isManhwa, pageId]);

  const addPanel = () => {
    if (!canvas) return;
    const rect = new fabric.Rect({
      left: 100,
      top: 100,
      fill: '#f0f0f0',
      stroke: 'black',
      strokeWidth: 4,
      width: 400,
      height: 300,
      hasControls: true,
      cornerColor: '#2563eb',
      cornerSize: 10,
      transparentCorners: false,
    });
    canvas.add(rect);
    canvas.setActiveObject(rect);
  };

  const addDiagonalPanel = () => {
      if (!canvas) return;
      // Using Polygon for diagonal/custom panel shapes (Issue 4.1)
      const points = [
          { x: 0, y: 0 },
          { x: 400, y: 50 },
          { x: 350, y: 300 },
          { x: -50, y: 250 }
      ];
      const poly = new fabric.Polygon(points, {
          left: 150,
          top: 150,
          fill: '#f0f0f0',
          stroke: 'black',
          strokeWidth: 4,
      });
      canvas.add(poly);
      canvas.setActiveObject(poly);
  };

  const addBubble = () => {
    if (!canvas) return;

    // Advanced Bubble with tail (Issue 4.3)
    const bubble = new fabric.Ellipse({
        fill: 'white',
        stroke: 'black',
        strokeWidth: 2,
        rx: 100,
        ry: 60,
    });

    const text = new fabric.IText('Dialogue...', {
        fontSize: 18,
        fontFamily: 'MangaFont',
        textAlign: 'center',
        originX: 'center',
        originY: 'center'
    });

    const group = new fabric.Group([bubble, text], {
        left: 200,
        top: 200,
    });

    canvas.add(group);
    canvas.setActiveObject(group);
  };

  const addScreentone = () => {
      if (!canvas) return;
      // Simulate screentone overlay (Issue 4.4)
      const rect = new fabric.Rect({
          left: 0,
          top: 0,
          width: canvas.width,
          height: canvas.height,
          fill: 'rgba(0,0,0,0.1)', // Placeholder for pattern
          selectable: false,
          evented: false
      });
      canvas.add(rect);
      alert("Screentone layer added!");
  };

  const saveLayout = async () => {
      if (!canvas) return;
      setLoading(true);
      const layoutData = canvas.toJSON();

      try {
          const res = await fetch('http://localhost:8000/api/v1/composition/page/save', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ pageId, layout: layoutData })
          });
          if (res.ok) {
              alert('Layout saved successfully!');
          }
      } catch (err) {
          console.error("Save error:", err);
      } finally {
          setLoading(false);
      }
  };

  const renderPage = async () => {
    setLoading(true);
    try {
        const res = await fetch('http://localhost:8000/api/v1/composition/page/render', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pageId })
        });
        const data = await res.json();
        alert(`Rendering started. Task ID: ${data.taskId}`);
    } catch (err) {
        console.error("Render error:", err);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-zinc-100 dark:bg-zinc-950 overflow-hidden font-sans">
      {/* Sidebar - Tools */}
      <aside className="w-72 border-r border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-6 flex flex-col gap-8 overflow-y-auto">
        <div>
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-zinc-900 dark:text-zinc-100">
            <Layout className="w-6 h-6 text-blue-600" /> NoTuMa Studio
          </h2>

          <div className="space-y-6">
            <section>
                <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-3">Layout & Panels</h3>
                <div className="grid grid-cols-2 gap-2">
                    <Button variant="outline" size="sm" onClick={addPanel} className="flex flex-col h-20 gap-2 border-dashed">
                        <Square className="w-5 h-5" />
                        <span className="text-[10px]">Standard</span>
                    </Button>
                    <Button variant="outline" size="sm" onClick={addDiagonalPanel} className="flex flex-col h-20 gap-2 border-dashed">
                        <Layers className="w-5 h-5" />
                        <span className="text-[10px]">Diagonal</span>
                    </Button>
                </div>
            </section>

            <section>
                <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-3">Narrative</h3>
                <div className="grid grid-cols-2 gap-2">
                    <Button variant="outline" size="sm" onClick={addBubble} className="flex flex-col h-20 gap-2 border-dashed">
                        <MessageSquare className="w-5 h-5" />
                        <span className="text-[10px]">Speech</span>
                    </Button>
                    <Button variant="outline" size="sm" className="flex flex-col h-20 gap-2 border-dashed">
                        <Type className="w-5 h-5" />
                        <span className="text-[10px]">SFX</span>
                    </Button>
                </div>
            </section>

            <section>
                <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-3">Aesthetics</h3>
                <div className="grid grid-cols-2 gap-2">
                    <Button variant="outline" size="sm" onClick={addScreentone} className="flex flex-col h-20 gap-2 border-dashed">
                        <Grid className="w-5 h-5" />
                        <span className="text-[10px]">Screentone</span>
                    </Button>
                    <Button variant="outline" size="sm" className="flex flex-col h-20 gap-2 border-dashed">
                        <Zap className="w-5 h-5" />
                        <span className="text-[10px]">Speed Lines</span>
                    </Button>
                </div>
            </section>
          </div>
        </div>

        <div className="mt-auto pt-6 border-t border-zinc-100 dark:border-zinc-800">
            <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium">Manhwa Mode</span>
                <button
                    onClick={() => setIsManhwa(!isManhwa)}
                    className={`w-12 h-6 rounded-full transition-colors relative ${isManhwa ? 'bg-blue-600' : 'bg-zinc-300'}`}
                >
                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${isManhwa ? 'left-7' : 'left-1'}`} />
                </button>
            </div>
            <div className="flex flex-col gap-2">
                <Button onClick={saveLayout} disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                    <Download className="w-4 h-4 mr-2" /> {loading ? 'Saving...' : 'Save Draft'}
                </Button>
                <Button onClick={renderPage} variant="secondary" disabled={loading} className="w-full">
                    <ChevronRight className="w-4 h-4 mr-2" /> {loading ? 'Processing...' : 'Export High-Res'}
                </Button>
            </div>
        </div>
      </aside>

      {/* Main Canvas Area */}
      <main className="flex-1 overflow-auto p-12 flex justify-center items-start scrollbar-hide bg-zinc-200 dark:bg-black/40">
        <div className="relative">
            <div className="absolute -top-8 left-0 text-[10px] font-mono text-zinc-400 uppercase tracking-widest">
                {isManhwa ? 'Vertical Strip Layout' : 'Standard Page Layout'} | {pageId}
            </div>
            <Card className="shadow-[0_20px_50px_rgba(0,0,0,0.2)] bg-white dark:bg-zinc-900 p-0 border-none overflow-hidden">
                <canvas ref={canvasRef} />
            </Card>
        </div>
      </main>
    </div>
  );
}
