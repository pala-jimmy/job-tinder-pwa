"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/lib/protected-route";
import { api } from "@/lib/api";

interface AttributeScore {
  technical_skills: number;
  communication: number;
  leadership: number;
  problem_solving: number;
  adaptability: number;
  teamwork: number;
}

interface RoleFit {
  role_name: string;
  fit_score: number;
}

interface StatsData {
  attributes: AttributeScore;
  role_fits: RoleFit[];
  top_match?: string;
}

export default function SeekerStatsPageWrapper() {
  return (
    <ProtectedRoute requiredRole="seeker">
      <SeekerStatsPage />
    </ProtectedRoute>
  );
}

function SeekerStatsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<StatsData | null>(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await api.get<StatsData>("/seeker/stats");
        setStats(data);
      } catch (err) {
        console.error("Failed to load stats:", err);
        setError(err instanceof Error ? err.message : "Failed to load stats");
      } finally {
        setLoading(false);
      }
    };
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading your stats...</div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-red-600 mb-4">
            {error || "No stats available"}
          </p>
          <p className="text-gray-600 mb-4">
            Complete the questionnaire to see your stats
          </p>
          <button
            onClick={() => router.push("/seeker/questionnaire")}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go to Questionnaire
          </button>
        </div>
      </div>
    );
  }

  const attributes = [
    { key: "technical_skills", label: "Technical Skills", color: "bg-blue-500" },
    { key: "communication", label: "Communication", color: "bg-green-500" },
    { key: "leadership", label: "Leadership", color: "bg-purple-500" },
    { key: "problem_solving", label: "Problem Solving", color: "bg-orange-500" },
    { key: "adaptability", label: "Adaptability", color: "bg-pink-500" },
    { key: "teamwork", label: "Teamwork", color: "bg-teal-500" },
  ];

  // Sort role fits by score
  const sortedRoleFits = [...stats.role_fits].sort((a, b) => b.fit_score - a.fit_score);
  const topMatches = sortedRoleFits.slice(0, 3);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Your Profile Stats</h1>
          <p className="text-gray-600">
            Based on your questionnaire responses
          </p>
        </div>

        {/* Top Match Banner */}
        {stats.top_match && (
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl"></span>
              <h2 className="text-xl font-bold">Best Match</h2>
            </div>
            <p className="text-2xl font-bold">{stats.top_match}</p>
            <p className="text-indigo-100 mt-1">
              This role aligns perfectly with your strengths and preferences
            </p>
          </div>
        )}

        {/* Attribute Scores */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Your Attributes</h2>
          <div className="space-y-5">
            {attributes.map((attr) => {
              const score = stats.attributes[attr.key as keyof AttributeScore];
              return (
                <div key={attr.key}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {attr.label}
                    </span>
                    <span className="text-sm font-bold text-gray-900">
                      {score}/100
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                      className={`${attr.color} h-3 rounded-full transition-all duration-500`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top 3 Role Fits */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Top Role Matches</h2>
          <div className="grid gap-4 md:grid-cols-3">
            {topMatches.map((role, index) => {
              const medals = ["", "", ""];
              const colors = [
                "border-yellow-400 bg-yellow-50",
                "border-gray-400 bg-gray-50",
                "border-orange-400 bg-orange-50",
              ];
              return (
                <div
                  key={role.role_name}
                  className={`border-2 ${colors[index]} rounded-lg p-4 text-center`}
                >
                  <div className="text-4xl mb-2">{medals[index]}</div>
                  <h3 className="font-semibold text-gray-800 mb-2">
                    {role.role_name}
                  </h3>
                  <div className="text-2xl font-bold text-indigo-600">
                    {role.fit_score}%
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Fit Score</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* All Role Fits */}
        {sortedRoleFits.length > 3 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-6">All Role Fits</h2>
            <div className="space-y-3">
              {sortedRoleFits.map((role) => {
                let badgeColor = "bg-gray-100 text-gray-700";
                if (role.fit_score >= 80) badgeColor = "bg-green-100 text-green-700";
                else if (role.fit_score >= 60) badgeColor = "bg-blue-100 text-blue-700";
                else if (role.fit_score >= 40) badgeColor = "bg-yellow-100 text-yellow-700";
                else badgeColor = "bg-red-100 text-red-700";

                return (
                  <div
                    key={role.role_name}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-indigo-300 transition"
                  >
                    <span className="font-medium text-gray-800">
                      {role.role_name}
                    </span>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${badgeColor}`}
                    >
                      {role.fit_score}%
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-4">
          <button
            onClick={() => router.push("/seeker/profile")}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
          >
            Edit Profile
          </button>
          <button
            onClick={() => router.push("/seeker/questionnaire")}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
          >
            Retake Questionnaire
          </button>
          <button
            onClick={() => router.push("/")}
            className="flex-1 bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
