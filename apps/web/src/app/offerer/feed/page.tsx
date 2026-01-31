"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/lib/protected-route";
import { api } from "@/lib/api";
import { CandidateCard } from "@/components/CandidateCard";

interface Candidate {
  id: string;
  headline: string;
  location: string;
  bio: string;
  attributes: {
    technical_skills: number;
    communication: number;
    leadership: number;
    problem_solving: number;
    adaptability: number;
    teamwork: number;
  };
  fit_score: number;
}

export default function OffererFeedPageWrapper() {
  return (
    <ProtectedRoute requiredRole="offerer">
      <OffererFeedPage />
    </ProtectedRoute>
  );
}

function OffererFeedPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [swipeDirection, setSwipeDirection] = useState<"left" | "right" | null>(null);
  
  const cardRef = useRef<HTMLDivElement>(null);
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const loadCandidates = async () => {
      try {
        const data = await api.get<Candidate[]>("/offerer/feed");
        setCandidates(data);
      } catch (err) {
        console.error("Failed to load candidates:", err);
      } finally {
        setLoading(false);
      }
    };
    loadCandidates();
  }, []);

  const currentCandidate = candidates[currentIndex];

  const handleSwipe = async (direction: "left" | "right") => {
    if (!currentCandidate) return;

    setSwipeDirection(direction);
    const action = direction === "right" ? "like" : "pass";

    try {
      await api.post("/offerer/swipe", {
        candidate_id: currentCandidate.id,
        action,
      });
    } catch (err) {
      console.error("Failed to save swipe:", err);
    }

    // Wait for animation then show next card
    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
      setSwipeDirection(null);
      setDragOffset({ x: 0, y: 0 });
    }, 300);
  };

  // Touch/Mouse event handlers
  const handleDragStart = (e: React.TouchEvent | React.MouseEvent) => {
    const point = "touches" in e ? e.touches[0] : e;
    setDragStart({ x: point.clientX, y: point.clientY });
  };

  const handleDragMove = (e: React.TouchEvent | React.MouseEvent) => {
    if (!dragStart) return;
    
    const point = "touches" in e ? e.touches[0] : e;
    const deltaX = point.clientX - dragStart.x;
    const deltaY = point.clientY - dragStart.y;
    setDragOffset({ x: deltaX, y: deltaY });
  };

  const handleDragEnd = () => {
    if (!dragStart) return;

    const swipeThreshold = 100;
    
    if (Math.abs(dragOffset.x) > swipeThreshold) {
      handleSwipe(dragOffset.x > 0 ? "right" : "left");
    } else {
      // Reset card position
      setDragOffset({ x: 0, y: 0 });
    }
    
    setDragStart(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading candidates...</div>
      </div>
    );
  }

  if (candidates.length === 0 || currentIndex >= candidates.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-6xl mb-4"></div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            All caught up!
          </h2>
          <p className="text-gray-600 mb-6">
            You&apos;ve reviewed all available candidates
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => router.push("/offerer/role-select")}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
            >
              Change Role
            </button>
            <button
              onClick={() => router.push("/offerer/shortlist")}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
            >
              View Shortlist
            </button>
          </div>
        </div>
      </div>
    );
  }

  const rotation = dragOffset.x * 0.1;
  const opacity = 1 - Math.abs(dragOffset.x) / 300;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => router.push("/offerer/role-select")}
            className="text-gray-600 hover:text-gray-800"
          >
             Change Role
          </button>
          <h1 className="text-xl font-bold text-gray-800">
            {currentIndex + 1} / {candidates.length}
          </h1>
          <button
            onClick={() => router.push("/offerer/shortlist")}
            className="text-indigo-600 hover:text-indigo-700 font-semibold"
          >
            Shortlist 
          </button>
        </div>

        {/* Card Stack */}
        <div className="relative h-[600px] mb-6">
          {/* Next card preview */}
          {candidates[currentIndex + 1] && (
            <div className="absolute inset-0 flex items-center justify-center">
              <CandidateCard
                candidate={candidates[currentIndex + 1]}
                style={{
                  transform: "scale(0.95)",
                  opacity: 0.5,
                }}
              />
            </div>
          )}

          {/* Current card */}
          <div
            ref={cardRef}
            className="absolute inset-0 flex items-center justify-center cursor-grab active:cursor-grabbing"
            style={{
              transform: `translateX(${dragOffset.x}px) translateY(${dragOffset.y}px) rotate(${rotation}deg)`,
              opacity: opacity,
              transition: dragStart ? "none" : "all 0.3s ease-out",
            }}
            onMouseDown={handleDragStart}
            onMouseMove={handleDragMove}
            onMouseUp={handleDragEnd}
            onMouseLeave={handleDragEnd}
            onTouchStart={handleDragStart}
            onTouchMove={handleDragMove}
            onTouchEnd={handleDragEnd}
          >
            <CandidateCard candidate={currentCandidate} />

            {/* Swipe indicators */}
            {Math.abs(dragOffset.x) > 50 && (
              <div
                className={`absolute top-8 ${
                  dragOffset.x > 0 ? "right-8" : "left-8"
                } text-6xl font-bold transform -rotate-12 ${
                  dragOffset.x > 0 ? "text-green-500" : "text-red-500"
                }`}
                style={{
                  opacity: Math.min(Math.abs(dragOffset.x) / 100, 1),
                }}
              >
                {dragOffset.x > 0 ? "LIKE" : "PASS"}
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-6 justify-center">
          <button
            onClick={() => handleSwipe("left")}
            className="w-16 h-16 rounded-full bg-white shadow-lg flex items-center justify-center text-3xl hover:scale-110 transition transform active:scale-95"
          >
            
          </button>
          <button
            onClick={() => handleSwipe("right")}
            className="w-20 h-20 rounded-full bg-green-500 shadow-lg flex items-center justify-center text-4xl hover:scale-110 transition transform active:scale-95"
          >
            
          </button>
        </div>
      </div>
    </div>
  );
}
