"use client";

import { FileText, Upload, Image as ImageIcon, X } from "lucide-react";
import { useRef, useState, type DragEvent } from "react";

interface ResumeUploadProps {
  file: File | null;
  onFileSelected: (file: File | null) => void;
}

const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".png", ".jpg", ".jpeg"];

export function ResumeUpload({ file, onFileSelected }: ResumeUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const dropped = event.dataTransfer.files[0];
    if (dropped) onFileSelected(dropped);
  }

  const isImage = file && (file.type.startsWith("image/") || file.name.match(/\.(png|jpg|jpeg)$/i));

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`relative flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
          isDragging
            ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-950/20 shadow-lg shadow-emerald-500/10 scale-[1.01]"
            : file
            ? "border-emerald-500/50 bg-slate-50 dark:bg-slate-900/90"
            : "border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/40 hover:border-slate-400 dark:hover:border-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900/70"
        }`}
      >
        {file ? (
          <div className="flex flex-col items-center w-full">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 flex items-center justify-center mb-2">
              {isImage ? <ImageIcon className="h-6 w-6" /> : <FileText className="h-6 w-6" />}
            </div>

            <div className="flex items-center gap-2 max-w-full px-4">
              <span className="font-mono text-sm font-bold text-slate-900 dark:text-slate-100 truncate">
                {file.name}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30 uppercase font-semibold">
                {(file.size / 1024).toFixed(0)} KB
              </span>
            </div>

            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Click or drag & drop to replace file</p>

            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onFileSelected(null);
              }}
              className="mt-3 text-xs text-rose-600 dark:text-rose-400 hover:text-rose-700 dark:hover:text-rose-300 flex items-center gap-1 transition-colors font-medium"
            >
              <X className="w-3.5 h-3.5" /> Remove file
            </button>
          </div>
        ) : (
          <>
            <div className="w-12 h-12 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center mb-1 group-hover:scale-110 transition-transform">
              <Upload className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                Drop candidate resume here, or <span className="text-emerald-600 dark:text-emerald-400 underline">browse</span>
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Supports PDF, Word (.docx), or Images (.png, .jpg)
              </p>
            </div>

            <div className="flex items-center gap-2 mt-2">
              {["PDF", "DOCX", "PNG / JPG"].map((ext) => (
                <span key={ext} className="px-2 py-0.5 text-[10px] font-mono rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-400 border border-slate-300 dark:border-slate-700 font-semibold">
                  {ext}
                </span>
              ))}
            </div>
          </>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_EXTENSIONS.join(",")}
        className="hidden"
        onChange={(e) => onFileSelected(e.target.files?.[0] ?? null)}
      />
    </div>
  );
}
