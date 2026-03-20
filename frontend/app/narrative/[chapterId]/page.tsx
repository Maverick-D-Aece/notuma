'use client'

import React, { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'

interface Dialogue {
    character_name: string;
    text: string;
}

interface Scene {
    id: string;
    text: string;
    dialogue: Dialogue[];
}

interface Character {
    id: string;
    name: string;
    traits: string[];
}

interface Chapter {
    title: string;
    scenes: Scene[];
    characters: Character[];
}

export default function NarrativeEditor() {
    const params = useParams()
    const chapterId = params.chapterId
    const [chapter, setChapter] = useState<Chapter | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchChapter = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/v1/narrative/chapter/${chapterId}`)
                const data = await response.json()
                setChapter(data)
                setLoading(false)
            } catch (error) {
                console.error('Error fetching chapter:', error)
                setLoading(false)
            }
        }
        if (chapterId) fetchChapter()
    }, [chapterId])

    if (loading) return <div className="p-8">Loading chapter analysis...</div>

    return (
        <div className="container mx-auto p-6 space-y-8">
            <header className="flex justify-between items-center mb-6 border-b pb-4">
                <h1 className="text-3xl font-bold">{chapter?.title || 'Chapter'} Analysis</h1>
                <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">Save Changes</button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2 space-y-6">
                    {chapter?.scenes.map((scene, index: number) => (
                        <div key={scene.id} className="bg-white border rounded-lg shadow-sm p-4 space-y-4">
                            <div className="text-sm font-medium text-gray-500 uppercase tracking-wider border-b pb-2">Scene {index + 1}</div>
                            <textarea
                                defaultValue={scene.text}
                                rows={6}
                                className="w-full p-3 text-sm border rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            />
                            <div className="space-y-2">
                                <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400">Dialogue Mapping</h4>
                                {scene.dialogue.map((d, i: number) => (
                                    <div key={i} className="flex gap-2 items-center">
                                        <span className="shrink-0 px-2 py-1 bg-gray-100 text-gray-600 text-[10px] font-bold rounded uppercase">{d.character_name || 'Unknown'}</span>
                                        <input
                                            defaultValue={d.text}
                                            className="w-full px-3 py-1 text-sm border rounded focus:ring-1 focus:ring-blue-400 focus:outline-none"
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="space-y-6">
                    <div className="bg-white border rounded-lg shadow-sm p-4">
                        <h3 className="text-lg font-bold mb-4 border-b pb-2">Characters Extracted</h3>
                        <div className="h-[400px] overflow-y-auto space-y-4 pr-2">
                            {chapter?.characters.map((char) => (
                                <div key={char.id || char.name} className="p-3 bg-gray-50 border rounded-lg space-y-2">
                                    <div className="font-semibold text-sm">{char.name}</div>
                                    <div className="flex flex-wrap gap-1">
                                        {char.traits?.map((trait: string) => (
                                            <span key={trait} className="px-2 py-0.5 bg-blue-100 text-blue-700 text-[10px] font-medium rounded-full">{trait}</span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="mt-4 pt-4 border-t space-y-3">
                            <input placeholder="Add character name..." className="w-full px-3 py-2 text-sm border rounded" />
                            <button className="w-full py-2 border border-blue-600 text-blue-600 rounded hover:bg-blue-50 transition text-sm font-medium">Add Character</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
