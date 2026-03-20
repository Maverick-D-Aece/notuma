'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'

interface UploadResponse {
    chapters: Array<{ id: string }>;
}

export default function IngestPage() {
    const router = useRouter()
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
            setError(null)
        }
    }

    const handleUpload = async () => {
        if (!file) return
        setUploading(true)
        setError(null)

        const formData = new FormData()
        formData.append('file', file)
        formData.append('project_title', file.name.split('.')[0])

        try {
            const response = await fetch('http://localhost:8000/api/v1/ingest/upload', {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                throw new Error('Upload failed')
            }

            const data: UploadResponse = await response.json()
            if (data.chapters && data.chapters.length > 0) {
                router.push(`/narrative/${data.chapters[0].id}`)
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Something went wrong';
            setError(message)
        } finally {
            setUploading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
            <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border p-8 space-y-6">
                <div className="text-center space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight">Upload Novel</h1>
                    <p className="text-gray-500 text-sm">Support for TXT, DOCX, and EPUB formats</p>
                </div>

                <div className="border-2 border-dashed border-gray-200 rounded-xl p-10 flex flex-col items-center justify-center space-y-4 hover:border-indigo-500 transition-colors cursor-pointer relative">
                    <input
                        type="file"
                        className="absolute inset-0 opacity-0 cursor-pointer"
                        onChange={handleFileChange}
                        accept=".txt,.docx,.epub"
                    />
                    {file ? (
                        <div className="text-center">
                            <p className="font-semibold text-sm">{file.name}</p>
                            <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                    ) : (
                        <p className="text-sm font-medium text-gray-600 text-center">
                            Click or drag and drop to upload
                        </p>
                    )}
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 p-3 rounded-lg text-red-600 text-xs">
                        {error}
                    </div>
                )}

                <button
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    className="w-full py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-all"
                >
                    {uploading ? 'Processing...' : 'Start Analysis'}
                </button>
            </div>
        </div>
    )
}
