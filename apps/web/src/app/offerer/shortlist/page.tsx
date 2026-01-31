"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/lib/protected-route";
import { api } from "@/lib/api";

interface ShortlistedCandidate {
  id: string;
  candidate_id: string;
  headline: string;
  location: string;
  bio: string;
  fit_score: number;
  note: string | null;
  shortlisted_at: string;
}

export default function OffererShortlistPageWrapper() {
  return (
    <ProtectedRoute requiredRole="offerer">
      <OffererShortlistPage />
    </ProtectedRoute>
  );
}

function OffererShortlistPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [candidates, setCandidates] = useState<ShortlistedCandidate[]>([]);
  const [editingNote, setEditingNote] = useState<string | null>(null);
  const [noteText, setNoteText] = useState("");
  const [savingNote, setSavingNote] = useState(false);

  useEffect(() => {
    loadShortlist();
  }, []);

  const loadShortlist = async () => {
    try {
      const data = await api.get<ShortlistedCandidate[]>("/offerer/shortlist");
      setCandidates(data);
    } catch (err) {
      console.error("Failed to load shortlist:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditNote = (candidate: ShortlistedCandidate) => {
    setEditingNote(candidate.id);
    setNoteText(candidate.note || "");
  };

  const handleSaveNote = async (candidateId: string) => {
    setSavingNote(true);
    try {
      await api.post(`/offerer/shortlist/${candidateId}/note`, { note: noteText });
      
      // Update local state
      setCandidates((prev) =>
        prev.map((c) =>
          c.id === candidateId ? { ...c, note: noteText } : c
        )
      );
      
      setEditingNote(null);
    } catch (err) {
      console.error("Failed to save note:", err);
      alert("Failed to save note");
    } finally {
      setSavingNote(false);
    }
  };

  const handleCancelEdit = () => {
    setEditingNote(null);
    setNoteText("");
  };

  const handleRemoveFromShortlist = async (candidateId: string) => {
    if (!confirm("Remove this candidate from your shortlist?")) return;

    try {
      await api.post(`/offerer/shortlist/${candidateId}/remove`, {});
      setCandidates((prev) => prev.filter((c) => c.id !== candidateId));
    } catch (err) {
      console.error("Failed to remove candidate:", err);
      alert("Failed to remove candidate");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading shortlist...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Shortlist</h1>
            <p className="text-gray-600 mt-1">
              {candidates.length} candidate{candidates.length !== 1 ? "s" : ""} saved
            </p>
          </div>
          <button
            onClick={() => router.push("/offerer/feed")}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            Back to Feed
          </button>
        </div>

        {candidates.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              No candidates yet
            </h2>
            <p className="text-gray-600 mb-6">
              Swipe right on candidates to add them to your shortlist
            </p>
            <button
              onClick={() => router.push("/offerer/feed")}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
            >
              Browse Candidates
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {candidates.map((candidate) => {
              const isEditing = editingNote === candidate.id;

              return (
                <div
                  key={candidate.id}
                  className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-bold text-gray-800">
                          {candidate.headline}
                        </h3>
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-semibold ${
                            candidate.fit_score >= 80
                              ? "bg-green-100 text-green-700"
                              : candidate.fit_score >= 60
                              ? "bg-blue-100 text-blue-700"
                              : "bg-yellow-100 text-yellow-700"
                          }`}
                        >
                          {candidate.fit_score}% fit
                        </span>
                      </div>
                      <p className="text-gray-500 text-sm mb-3 flex items-center gap-1">
                         {candidate.location}
                      </p>
                      <p className="text-gray-700 text-sm line-clamp-2 mb-3">
                        {candidate.bio}
                      </p>
                    </div>

                    <button
                      onClick={() => handleRemoveFromShortlist(candidate.id)}
                      className="text-gray-400 hover:text-red-500 transition ml-4"
                      title="Remove from shortlist"
                    >
                      
                    </button>
                  </div>

                  {/* Notes Section */}
                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-semibold text-gray-700 uppercase">
                        Notes
                      </label>
                      {!isEditing && (
                        <button
                          onClick={() => handleEditNote(candidate)}
                          className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                        >
                          {candidate.note ? "Edit" : "Add Note"}
                        </button>
                      )}
                    </div>

                    {isEditing ? (
                      <div className="space-y-2">
                        <textarea
                          value={noteText}
                          onChange={(e) => setNoteText(e.target.value)}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                          placeholder="Add notes about this candidate..."
                          autoFocus
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleSaveNote(candidate.id)}
                            disabled={savingNote}
                            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 text-sm font-medium"
                          >
                            {savingNote ? "Saving..." : "Save"}
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            disabled={savingNote}
                            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : candidate.note ? (
                      <p className="text-gray-700 text-sm bg-gray-50 p-3 rounded-lg">
                        {candidate.note}
                      </p>
                    ) : (
                      <p className="text-gray-400 text-sm italic">
                        No notes yet
                      </p>
                    )}
                  </div>

                  <div className="mt-3 text-xs text-gray-500">
                    Shortlisted {new Date(candidate.shortlisted_at).toLocaleDateString()}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
